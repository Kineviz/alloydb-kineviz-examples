#!/usr/bin/env python3
"""Safe, schema-scoped setup and verification for the AlloyDB SQL port."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import psycopg
from psycopg import sql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DEMOS = {
    'paysim-schemaless': ('paysim', 'paysim_demo'),
    'fraud-rings': ('fraud', 'fraud_demo'),
    'edge-fleet': ('fleet', 'fleet_demo'),
}
OWNER = 'alloydb-kineviz-examples:v1'
TX_LABELS = {'performs', 'to_client', 'to_merchant', 'to_bank'}


def connect():
    load_dotenv(ROOT / '.env')
    if not os.environ.get('PGDATABASE'):
        raise ValueError('Set PGDATABASE to a dedicated demo database in .env.')
    host = os.environ.get('PGHOST', '')
    if host not in {'127.0.0.1', 'localhost', '::1'} and os.environ.get('PGSSLMODE') != 'verify-full':
        raise ValueError('Remote connections require PGSSLMODE=verify-full and a trusted certificate; otherwise use a loopback tunnel.')
    return psycopg.connect('', connect_timeout=10, options='-c statement_timeout=60000')


def preflight(conn):
    version = conn.execute("SELECT current_setting('server_version_num')::int").fetchone()[0]
    if version < 190000:
        raise ValueError('Native project connector requires AlloyDB Omni on PostgreSQL 19+ with SQL/PGQ, not standard Omni 16.x')
    require(conn.execute("SELECT to_regclass('information_schema.property_graphs')").fetchone()[0], 'SQL/PGQ catalog is missing')


def owned(conn, schema, create=False):
    exists = conn.execute('SELECT 1 FROM pg_namespace WHERE nspname=%s', (schema,)).fetchone()
    if not exists and create:
        conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(schema)))
        conn.execute(sql.SQL('COMMENT ON SCHEMA {} IS {}').format(sql.Identifier(schema), sql.Literal(OWNER)))
    else:
        marker = conn.execute("SELECT obj_description(oid,'pg_namespace') FROM pg_namespace WHERE nspname=%s", (schema,)).fetchone()
        if not marker or marker[0] != OWNER:
            raise ValueError(f'{schema} is missing or not owned by this demo; refusing to modify it.')
    conn.execute(sql.SQL('SET search_path TO {}, pg_catalog').format(sql.Identifier(schema)))


def generate(demo):
    out = ROOT / 'generated' / demo
    subprocess.run([sys.executable, str(ROOT / 'vendor' / (DEMOS[demo][0]+'.py')), '--out', str(out)], check=True)
    return out


def dataset(demo, entities_only=False):
    out = ROOT / 'generated' / demo
    manifest = json.loads((out / 'csv-export.json').read_text())
    for spec in manifest['tables']:
        table = spec['tableName'].lower()
        columns = [c['columnName'].lower() for c in spec['columns']]
        with (out / spec['filePatterns'][0]).open(newline='') as fh:
            rows = list(csv.reader(fh))
        if entities_only and demo == 'paysim-schemaless':
            rows = [r for r in rows if (r[1] != 'transaction' if table == 'graphnode' else r[3] not in TX_LABELS)]
        yield table, columns, rows


def setup(conn, demo, entities_only):
    owned(conn, DEMOS[demo][1], create=True)
    conn.execute((ROOT / 'demos' / demo / 'schema.sql').read_text())
    for table, columns, rows in dataset(demo, entities_only):
        target = sql.Identifier(table)
        stage = sql.Identifier('_stage_'+table)
        conn.execute(sql.SQL('CREATE TEMP TABLE {} (LIKE {} INCLUDING DEFAULTS) ON COMMIT DROP').format(stage, target))
        buf = io.StringIO()
        csv.writer(buf).writerows(rows)
        with conn.cursor().copy(sql.SQL('COPY {} ({}) FROM STDIN WITH (FORMAT CSV)').format(
            stage, sql.SQL(',').join(map(sql.Identifier, columns)))) as copy:
            copy.write(buf.getvalue())
        conn.execute(sql.SQL('INSERT INTO {} SELECT * FROM {} ON CONFLICT DO NOTHING').format(target, stage))
    graph = DEMOS[demo][0]+'_graph'
    exists = conn.execute('SELECT 1 FROM information_schema.property_graphs WHERE property_graph_schema=%s AND property_graph_name=%s', (DEMOS[demo][1], graph)).fetchone()
    if not exists:
        conn.execute((ROOT / 'demos' / demo / 'property-graph.sql').read_text())


def query(conn, demo, number):
    path = next((ROOT / 'demos' / demo / 'queries').glob(f'{number:02}-*.sql'))
    cur = conn.execute(path.read_text())
    return [dict(zip([c.name for c in cur.description], row)) for row in cur]


def require(condition, message):
    if not condition:
        raise ValueError('Verification failed: '+message)


def verify(conn, demo, entities_only=False):
    owned(conn, DEMOS[demo][1])
    graph = DEMOS[demo][0]+'_graph'
    graph_nodes = conn.execute(sql.SQL('SELECT count(*) FROM GRAPH_TABLE ({} MATCH (n) COLUMNS (n.id AS id))').format(sql.Identifier(graph))).fetchone()[0]
    require(graph_nodes > 0, 'native GRAPH_TABLE returned no nodes')
    counts = {}
    for table, _, rows in dataset(demo, entities_only):
        count = conn.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier(table))).fetchone()[0]
        require(count == len(rows), f'{table}: expected {len(rows)}, got {count}. Use a fresh dedicated schema for a different mode.')
        counts[table] = count
    if demo == 'paysim-schemaless':
        shared = query(conn, demo, 1)
        transfers = query(conn, demo, 2)
        require(len(shared) == 8, 'expected eight shared identifier VALUES')
        require(len({r['identifier_id'] for r in transfers}) == (0 if entities_only else 4), 'unexpected shared values with direct transfers')
        planted = json.loads((ROOT / 'generated' / demo / 'PLANTED.json').read_text())
        family = ['client_'+m for m in planted['family']['members']]
        between = conn.execute('SELECT count(*) FROM payments WHERE sender_id=ANY(%s) AND receiver_id=ANY(%s)', (family, family)).fetchone()[0]
        require(between == 0, 'family must not exchange payments')
        if not entities_only:
            cycles = query(conn, demo, 7)
            ring = {'client_'+m for m in planted['ring_a']['members']}
            require(any(set(r.values()) == ring for r in cycles), 'planted four-account cycle missing')
            require(bool(query(conn, demo, 3)) and bool(query(conn, demo, 4)), 'collector or cash-out findings missing')
        counts.update(shared_identifier_values=8, shared_values_with_transfers=0 if entities_only else 4)
    elif demo == 'fraud-rings':
        require(bool(query(conn, demo, 1)), 'no shared devices')
        # The source plants a four-account cycle; assert its four directed legs.
        ring = conn.execute("SELECT count(DISTINCT (src_client_id,dst_client_id)) FROM paid WHERE (src_client_id,dst_client_id) IN (('C00000','C00001'),('C00001','C00002'),('C00002','C00003'),('C00003','C00000'))").fetchone()[0]
        require(ring == 4, 'planted cycle missing')
        family = conn.execute("SELECT count(*) FROM paid WHERE src_client_id IN ('C00008','C00009','C00010') AND dst_client_id IN ('C00008','C00009','C00010')").fetchone()[0]
        require(family == 0, 'family must not exchange payments')
    else:
        gateways = query(conn, demo, 1)
        require(gateways[0]['devices'] > 2*gateways[1]['devices'], 'concentration gateway missing')
        require(bool(query(conn, demo, 2)) and bool(query(conn, demo, 4)), 'single-cover site or dependency chain missing')
    counts['graph_nodes'] = graph_nodes
    print(json.dumps({'verified': demo, 'counts': counts}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['list','generate','preflight','up','verify','query','handoff','reset'])
    parser.add_argument('demo', nargs='?', choices=DEMOS)
    parser.add_argument('--entities-only', action='store_true', help='PaySim actors/identifiers only, ready for replay; requires empty schema')
    parser.add_argument('--number', type=int, default=1)
    parser.add_argument('--confirm-schema', help='reset requires the exact owned schema name')
    args = parser.parse_args()
    if args.command == 'list':
        print('\n'.join(f'{d}: schema {v[1]}' for d,v in DEMOS.items()))
        return
    if not args.demo:
        parser.error('demo is required')
    if args.entities_only and args.demo != 'paysim-schemaless':
        parser.error('--entities-only is only supported for paysim-schemaless')
    if args.command == 'generate':
        generate(args.demo)
        return
    if args.command == 'handoff':
        print('Open connect/README.md. Desktop → Create New Project → Google AlloyDB Omni. Graph Name: '+DEMOS[args.demo][0]+'_graph')
        return
    with connect() as conn:
        preflight(conn)
        if args.command in {'preflight','up'}:
            info = conn.execute('SELECT current_database(),version()').fetchone()
            print('Connected:', info[0], info[1])
        if args.command == 'up':
            generate(args.demo)
            setup(conn, args.demo, args.entities_only)
            verify(conn, args.demo, args.entities_only)
            print('Verified. Next: connect/README.md — Create New Project → Google AlloyDB Omni.')
        elif args.command == 'verify':
            verify(conn, args.demo, args.entities_only)
        elif args.command == 'query':
            print(json.dumps(query(conn, args.demo, args.number), indent=2, default=str))
        elif args.command == 'reset':
            schema = DEMOS[args.demo][1]
            if args.confirm_schema != schema:
                raise ValueError(f'Reset deletes this demo schema and its contents. Explicitly pass --confirm-schema {schema}.')
            owned(conn, schema)
            conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(schema)))
            print(f'Deleted only schema {schema}. Recover by rerunning up; custom additions are not recoverable without a backup.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, psycopg.Error, subprocess.CalledProcessError) as exc:
        # Avoid echoing connection strings or passwords in database errors.
        detail = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        print(f'REMEDIATION: {detail}. Check .env, database reachability and docs/TROUBLESHOOTING.md.', file=sys.stderr)
        sys.exit(1)
