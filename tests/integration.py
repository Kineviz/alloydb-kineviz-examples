"""Read-only checks against the configured, already seeded SQL/PGQ database."""
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from demo import connect,preflight,verify,DEMOS
from psycopg import sql

with connect() as conn:
    conn.execute('SET TRANSACTION READ ONLY')
    preflight(conn)
    for demo,(prefix,schema) in DEMOS.items():
        verify(conn,demo)
        for path in sorted((ROOT/'demos'/demo/'queries').glob('*.sql')):
            rows=conn.execute(path.read_text()).fetchall()
            if not rows:
                raise AssertionError(f'No result: {path}')
            print('PASS query',path.relative_to(ROOT),len(rows))
        graph=sql.Identifier(schema,prefix+'_graph')
        edges=conn.execute(sql.SQL('SELECT count(*) FROM GRAPH_TABLE ({} MATCH (s)-[e]->(d) COLUMNS (s.id AS src,d.id AS dst))').format(graph)).fetchone()[0]
        expected={'paysim-schemaless':25266,'fraud-rings':3319,'edge-fleet':2012}[demo]
        assert edges==expected,(demo,edges,expected)
        print('PASS native graph edge count',demo,edges)
    for path in sorted((ROOT/'demos/paysim-schemaless/queries/pgq').glob('*.sql')):
        rows=conn.execute(path.read_text()).fetchall()
        assert rows,path
        print('PASS SQL/PGQ',path.name,len(rows))
print('All integration checks passed.')
