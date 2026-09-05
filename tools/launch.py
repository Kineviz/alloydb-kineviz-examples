"""One-command local setup; existing low-level gxr commands remain available."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / '.venv/bin/python'
DEMOS = ('paysim-schemaless', 'fraud-rings', 'edge-fleet')


def run(*args):
    subprocess.run([str(a) for a in args], cwd=ROOT, check=True)


def runtime():
    if sys.version_info < (3, 10):
        raise ValueError('Install Python 3.10 or newer.')
    if not PYTHON.exists():
        run(sys.executable, '-m', 'venv', ROOT / '.venv')
    digest = hashlib.sha256((ROOT / 'requirements.txt').read_bytes()).hexdigest()
    marker = ROOT / '.venv/.gxr-requirements'
    if not marker.exists() or marker.read_text() != digest:
        run(PYTHON, '-m', 'pip', 'install', '-r', ROOT / 'requirements.txt')
        marker.write_text(digest)


def local_database():
    from dotenv import dotenv_values
    import psycopg
    from psycopg import sql
    if not (ROOT / '.env').exists():
        run(PYTHON, ROOT / 'tools/init_env.py')
    config = dotenv_values(ROOT / '.env')
    expected = dict(PGHOST='127.0.0.1', PGPORT='55432',
                    PGDATABASE='kineviz_demo', PGUSER='postgres', PGSSLMODE='disable')
    for key, value in expected.items():
        if config.get(key) != value or os.environ.get(key, value) != value:
            raise ValueError('start manages only the default local Compose database. '
                             'For a separately configured database use ./gxr up <demo>.')
    for key in ('PGPASSWORD', 'POSTGRES_PASSWORD'):
        if not config.get(key) or os.environ.get(key, config[key]) != config[key]:
            raise ValueError('Local credentials are missing or conflict with the environment; preserve existing passwords.')
    if config['PGPASSWORD'] != config['POSTGRES_PASSWORD']:
        raise ValueError('Local admin passwords must match; do not rotate an existing volume password automatically.')
    run('docker', 'compose', 'up', '-d', '--wait', 'db')
    with psycopg.connect(host='127.0.0.1', port=55432, dbname='postgres',
                          user='postgres', password=config['PGPASSWORD'],
                          sslmode='disable', connect_timeout=10, autocommit=True) as conn:
        from demo import preflight
        preflight(conn)
        if not conn.execute('SELECT 1 FROM pg_database WHERE datname=%s', ('kineviz_demo',)).fetchone():
            conn.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier('kineviz_demo')))


def restart_transactions():
    from demo import connect, generate, owned, preflight, setup, verify
    demo = 'paysim-schemaless'
    generate(demo)
    with connect() as conn:
        preflight(conn)
        owned(conn, 'paysim_demo', create=True)
        exists = conn.execute("SELECT to_regclass('paysim_demo.graphnode')").fetchone()[0]
        if exists:
            # Lock both tables until deletion and actors-only verification commit.
            # Never DROP the schema: preserve the graph, grants and identifiers.
            conn.execute('LOCK TABLE paysim_demo.graphnode, paysim_demo.graphedge IN EXCLUSIVE MODE')
            conn.execute("DELETE FROM paysim_demo.graphedge WHERE id IN (SELECT id FROM paysim_demo.graphnode WHERE label='transaction') OR dest_id IN (SELECT id FROM paysim_demo.graphnode WHERE label='transaction')")
            removed = conn.execute("DELETE FROM paysim_demo.graphnode WHERE label='transaction'").rowcount
        else:
            removed = 0
        setup(conn, demo, True)
        verify(conn, demo, True)
    print(f'Restart committed: removed {removed} transaction nodes and their incident edges. '
          'Actors, identifiers and other demo schemas preserved. Replay regenerates the synthetic payments.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=
        'Other commands: list, up <demo>, verify <demo>, query <demo>, '
        'generate <demo>, preflight <demo>, handoff <demo>, reset <demo>.')
    subs = parser.add_subparsers(dest='command', required=True)
    start = subs.add_parser('start', help='Prepare local database, load, verify and configure reader')
    start.add_argument('demo', nargs='?', default='paysim-schemaless', choices=(*DEMOS, 'all'))
    start.add_argument('--entities-only', action='store_true', help='Seed PaySim for replay without deleting existing data')
    subs.add_parser('stop', help='Stop this repo database and Kafka; preserve volumes')
    replay = subs.add_parser('replay', help='Replay PaySim; optionally clear transactions first')
    replay.add_argument('--restart', action='store_true', help='DESTRUCTIVE: delete all PaySim transaction nodes and incident edges, preserve actors, then replay (local demo only)')
    replay.add_argument('--via', choices=('direct', 'kafka'), default='direct')
    replay.add_argument('--seconds', type=float, default=60)
    subs.add_parser('test', help='Run unit tests (no database required)')
    if len(sys.argv) > 1 and sys.argv[1] not in {'start', 'stop', 'replay', 'test', '-h', '--help'}:
        runtime()
        run(PYTHON, ROOT / 'tools/demo.py', *sys.argv[1:])
        return
    args = parser.parse_args()
    if args.command == 'start' and args.entities_only and args.demo != 'paysim-schemaless':
        parser.error('--entities-only requires paysim-schemaless')
    if args.command == 'replay':
        import math
        if not math.isfinite(args.seconds) or args.seconds < 0:
            parser.error('--seconds must be finite and nonnegative')
    if args.command == 'stop':
        run('docker', 'compose', 'stop')
        run('docker', 'compose', '-f', 'streaming/compose.yaml', 'stop')
        return
    runtime()
    if Path(sys.prefix).resolve() != (ROOT / '.venv').resolve():
        run(PYTHON, ROOT / 'tools/launch.py', *sys.argv[1:])
        return
    if args.command == 'start':
        local_database()
        for demo in DEMOS if args.demo == 'all' else (args.demo,):
            flags = ['--entities-only'] if args.entities_only else []
            run(PYTHON, ROOT / 'tools/demo.py', 'up', demo, *flags)
        run(PYTHON, ROOT / 'tools/create_reader.py')
        run(PYTHON, ROOT / 'tools/check_reader.py')
        print('Ready for Desktop → Create New Project → Google AlloyDB Omni.\n'
              'Host: 127.0.0.1 | Port: 55432 | Database: kineviz_demo\n'
              'Graph: paysim_graph / fraud_graph / fleet_graph (choose a loaded demo).\n'
              'Reader credentials: secrets/reader.env (password not printed).\n'
              'See connect/README.md for screenshots and the final canvas check.')
    elif args.command == 'replay':
        if args.restart:
            local_database()
        if args.via == 'kafka':
            run(PYTHON, '-m', 'pip', 'install', '-r', 'streaming/requirements.txt')
            run('docker', 'compose', '-f', 'streaming/compose.yaml', 'up', '-d', '--wait')
        if args.restart:
            print('Restart requested: clearing PaySim transactions before replay. Stop other replay writers first.', flush=True)
            restart_transactions()
            run(PYTHON, ROOT / 'tools/create_reader.py')
            run(PYTHON, ROOT / 'tools/check_reader.py')
        run(PYTHON, ROOT / 'streaming/replay.py', '--via', args.via, '--seconds', str(args.seconds))
    elif args.command == 'test':
        run(PYTHON, '-m', 'unittest', 'discover', '-s', 'tests', '-v')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        detail = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        print(f'REMEDIATION: {detail}. See docs/TROUBLESHOOTING.md. '
              'If --restart committed, transactions were cleared; replay may be incomplete. '
              'Run replay without --restart to retry without clearing again.', file=sys.stderr)
        sys.exit(1)
