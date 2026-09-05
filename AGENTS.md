# AlloyDB examples

This targets AlloyDB Omni's PostgreSQL 19 SQL/PGQ preview, not standard Omni 16.x.
Read README.md and connect/README.md. Run preflight → setup → verify → handoff
with `./gxr up <demo>`. Never report a working database from static tests alone.
Do not create billable cloud resources without a project, region and approval.
Do not install Desktop, create an account or sign in for the user.
Do not drop schemas, reset a replay or remove volumes without explicit approval.
Never expose database, Kafka or Auth Proxy listeners beyond loopback by default.
Never commit credentials, generated synthetic identifiers, or local app projects.
Use Create New Project → Google AlloyDB Omni. The native project connector
reads property graphs through SQL/PGQ. SQL import is not the primary workflow.
Do not claim compatibility with managed AlloyDB versions lacking SQL/PGQ.
Preserve vendor generators and their MIT attribution. Fix adapters, not planted
findings, when tests fail. Do not load unrelated data into demo-owned schemas.
