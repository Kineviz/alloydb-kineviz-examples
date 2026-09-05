"""Create a new least-privilege local demo login; refuse to replace an existing role."""
import os
import secrets
from demo import ROOT, connect, DEMOS, preflight
from psycopg import sql

role = 'kineviz_demo_reader'
directory = ROOT / 'secrets'
directory.mkdir(mode=0o700, exist_ok=True)
path = directory / 'reader.env'
if path.exists():
    raise SystemExit('Reader credentials already exist; not overwriting them.')
password = secrets.token_hex(24)
with connect() as conn:
    preflight(conn)
    database = conn.execute('SELECT current_database()').fetchone()[0]
    if conn.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(role,)).fetchone():
        raise SystemExit('Reader role already exists; refusing to change its password or permissions.')
    conn.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
    conn.execute(sql.SQL('GRANT CONNECT ON DATABASE {} TO {}').format(sql.Identifier(database),sql.Identifier(role)))
    schemas=[]
    for demo,(prefix,schema) in DEMOS.items():
        if not conn.execute('SELECT 1 FROM information_schema.property_graphs WHERE property_graph_schema=%s AND property_graph_name=%s',(schema,prefix+'_graph')).fetchone():
            continue
        schemas.append(schema)
        conn.execute(sql.SQL('GRANT USAGE ON SCHEMA {} TO {}').format(sql.Identifier(schema),sql.Identifier(role)))
        conn.execute(sql.SQL('GRANT SELECT ON ALL TABLES IN SCHEMA {} TO {}').format(sql.Identifier(schema),sql.Identifier(role)))
        conn.execute(sql.SQL('GRANT SELECT ON PROPERTY GRAPH {} TO {}').format(sql.Identifier(schema,prefix+'_graph'),sql.Identifier(role)))
    if not schemas:
        raise SystemExit('Run ./gxr up <demo> before creating a reader.')
    conn.execute(sql.SQL('ALTER ROLE {} IN DATABASE {} SET search_path TO {}, pg_catalog').format(
        sql.Identifier(role),sql.Identifier(database),sql.SQL(',').join(map(sql.Identifier,schemas))))
    # Persist the secret before commit; if commit fails, delete only this new file.
    with path.open('x') as f:
        os.chmod(path,0o600)
        f.write(f'PGUSER={role}\nPGPASSWORD={password}\n')
    try:
        conn.commit()
    except Exception:
        path.unlink()
        raise
print('Created read-only login. Local credentials: secrets/reader.env (not tracked by git).')
print('It can read only the demo schemas currently installed. It cannot load/replay data.')
