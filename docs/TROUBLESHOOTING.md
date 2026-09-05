# Troubleshooting and cleanup

**Database won't start:** `docker compose ps` and `docker compose logs --tail 60 db`.
Confirm preview access, available memory/disk, Docker x86 emulation on ARM, and
that port 55432 is free. Do not stop another application's database to free it.

**Wrong PostgreSQL version / GRAPH_TABLE missing:** the native connector requires
the SQL/PGQ preview. An ordinary Omni image is not compatible.

**Connection refused:** Desktop uses host port 55432. The Docker-internal name
`db` and internal port 5432 are not the host connection values.

**Password rejected:** `tools/init_env.py` sets a password for a *new* volume.
Changing .env later does not rotate the database password. Use the existing
credentials or have the administrator rotate it; do not delete a volume to fix
authentication. The read-only user's password is in secrets/reader.env.

**Graph missing / relation does not exist:** run `./gxr verify <demo>`. Use
`paysim_graph`, `fraud_graph` or `fleet_graph` as Graph Name, and ensure the login's
search_path includes the corresponding schema. The reader helper handles this.
Close and reopen the project connection after changing login defaults.

**Permission denied:** read access requires schema USAGE, SELECT on backing
tables/views, and SELECT ON PROPERTY GRAPH. Reset/rebuild removes object grants.
Have an administrator regrant only the intended demo objects.

**Table instead of graph:** use the project's Query panel and the graph-mode
examples under queries/canvas. Do not use Query → SQL or paste scalar SQL and
expect it to render nodes automatically.

**Verify count mismatch:** do not mix custom data with these seeded schemas.
An entities-only setup refuses to pretend an already full schema is empty.
Use a new dedicated database or explicitly reset that demo if it is disposable.
Generation is deterministic. Fix code/data drift rather than loosening checks.

## Stop without deleting data

```bash
./gxr stop
```

The volumes persist. `./gxr start` restarts and verifies the PaySim database;
`./gxr replay --via kafka` starts the broker when needed and replays the events.

## Explicit destructive operations (only when requested)

Reset a **disposable demo schema**, not the container or all databases:

```bash
./gxr reset paysim-schemaless --confirm-schema paysim_demo
./gxr up paysim-schemaless
```

This deletes the owned paysim_demo schema, its graph and dependent objects.
Generated demo rows can be recreated; custom additions cannot be recovered
without a backup. Do not add unrelated dependent objects to a demo schema.

Removing the **entire dedicated local deployment and its data** is separate:

```bash
# Review `docker compose ps` first; run only in THIS repository.
docker compose down --volumes
docker compose -f streaming/compose.yaml down --volumes
```

These commands are never run automatically. They irreversibly remove this
Compose project's data volumes. Never substitute the existing Spanner or another
AlloyDB project's name. Stop is enough for routine cleanup.
