"""Read-only connection, graph discovery, and write-privilege checks."""
from dotenv import dotenv_values, load_dotenv
import psycopg
from psycopg import sql
from demo import ROOT,DEMOS

load_dotenv(ROOT/'.env')
creds=dotenv_values(ROOT/'secrets/reader.env')
with psycopg.connect('',user=creds['PGUSER'],password=creds['PGPASSWORD']) as conn:
    conn.execute('SET TRANSACTION READ ONLY')
    graphs=conn.execute('SELECT property_graph_name FROM information_schema.property_graphs').fetchall()
    assert graphs,'Reader sees no graphs'
    for (graph,) in graphs:
        count=conn.execute(sql.SQL('SELECT count(*) FROM GRAPH_TABLE ({} MATCH (n) COLUMNS(n.id AS id))').format(sql.Identifier(graph))).fetchone()[0]
        assert count>0
        print('PASS reader discovers and queries',graph,count)
    for _,schema in DEMOS.values():
        rows=conn.execute("SELECT has_table_privilege(current_user,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE') FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname=%s AND c.relkind='r'",(schema,)).fetchall()
        assert not any(r[0] for r in rows),'Reader has write privileges'
print('Read-only login verified; no password printed.')
