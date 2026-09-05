"""Create or reuse the saved reader; grant access only to repo-owned demo schemas."""
import os
import secrets
from demo import ROOT, connect, DEMOS, preflight, owned
from dotenv import dotenv_values
import psycopg
from psycopg import sql

role = 'kineviz_demo_reader'
directory = ROOT / 'secrets'
directory.mkdir(mode=0o700, exist_ok=True)
path = directory / 'reader.env'
existing = dotenv_values(path) if path.exists() else None
if existing is not None and (existing.get('PGUSER') != role or not existing.get('PGPASSWORD')):
    raise SystemExit('Invalid reader credential file; refusing to overwrite it.')
password = existing['PGPASSWORD'] if existing else secrets.token_hex(24)
with connect() as conn:
    preflight(conn)
    database = conn.execute('SELECT current_database()').fetchone()[0]
    exists = conn.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(role,)).fetchone()
    if bool(exists) != bool(existing):
        raise SystemExit('Reader role and saved credentials do not match; refusing to replace either.')
    if existing:
        try:
            with psycopg.connect('', user=role, password=password, connect_timeout=10):
                pass
        except psycopg.Error:
            raise SystemExit('Saved reader login failed; no password or grants changed.')
    else:
        conn.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
    conn.execute(sql.SQL('GRANT CONNECT ON DATABASE {} TO {}').format(sql.Identifier(database),sql.Identifier(role)))
    schemas=[]
    for demo,(prefix,schema) in DEMOS.items():
        if not conn.execute('SELECT 1 FROM information_schema.property_graphs WHERE property_graph_schema=%s AND property_graph_name=%s',(schema,prefix+'_graph')).fetchone():
            continue
        owned(conn, schema)
        schemas.append(schema)
        conn.execute(sql.SQL('GRANT USAGE ON SCHEMA {} TO {}').format(sql.Identifier(schema),sql.Identifier(role)))
        conn.execute(sql.SQL('GRANT SELECT ON ALL TABLES IN SCHEMA {} TO {}').format(sql.Identifier(schema),sql.Identifier(role)))
        conn.execute(sql.SQL('GRANT SELECT ON PROPERTY GRAPH {} TO {}').format(sql.Identifier(schema,prefix+'_graph'),sql.Identifier(role)))
    if not schemas:
        raise SystemExit('Run ./gxr up <demo> before creating a reader.')
    conn.execute(sql.SQL('ALTER ROLE {} IN DATABASE {} SET search_path TO {}, pg_catalog').format(
        sql.Identifier(role),sql.Identifier(database),sql.SQL(',').join(map(sql.Identifier,schemas))))
    # Persist the secret before commit; if commit fails, delete only this new file.
    if not existing:
        with path.open('x') as f:
            os.chmod(path,0o600)
            f.write(f'PGUSER={role}\nPGPASSWORD={password}\n')
    try:
        conn.commit()
    except Exception:
        if not existing:
            path.unlink()
        raise
print('Read-only login configured. Local credentials: secrets/reader.env (not tracked by git).')
print('It can read only the demo schemas currently installed. It cannot load/replay data.')
