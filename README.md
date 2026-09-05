# AlloyDB Omni + Kineviz Desktop

Test synthetic payment investigations and infrastructure dependencies in
**AlloyDB Omni**, then explore the property graph using Kineviz Desktop's
**native Google AlloyDB Omni project connector**. No `graphxr-database-proxy`,
bridge server, service-account upload, API URL, or CSV mapping is required.

This is a port of [spanner-omni-kineviz-examples](https://github.com/Kineviz/spanner-omni-kineviz-examples).
It preserves the three synthetic generators and their planted examples, replaces
the database layer with PostgreSQL SQL/PGQ, and replaces the proxy-based
[`connect/` workflow](https://github.com/Kineviz/spanner-omni-kineviz-examples/tree/main/connect)
with [direct project connection steps](connect/README.md).

## Important: use the SQL/PGQ build

The native connector requires **AlloyDB Omni on PostgreSQL 19+ with SQL/PGQ**.
The supplied Compose file pins the Google custom-release **19beta1 preview**
image by digest. Standard Omni 16.x cannot run this repo's `CREATE PROPERTY GRAPH`
or `GRAPH_TABLE` queries. Do not substitute `google/alloydbomni:16.8.0` or `latest`.

The preview image is **linux/amd64**. Apple Silicon uses Docker's x86 emulation;
performance and memory use differ from a native Linux host. Preview access and
terms must be confirmed with Google; a registry denial is not a reason to use an
incompatible image. This is a reproducible lab, not a production deployment or a
claim that managed AlloyDB supports the same graph feature. See [compatibility](docs/COMPATIBILITY.md).

## Quick start

You need Git, Python 3.10+, Docker Compose v2, a machine with capacity for the
preview database, and Kineviz Desktop. These commands are for macOS/Linux; on
Windows run the shell steps in WSL2 and install the Windows Desktop application.

From this repository's root:

```bash
./gxr start
```

That one command creates the Python environment, installs pinned dependencies,
initializes local credentials if absent, starts the database, creates the demo
database if needed, loads and verifies PaySim, and configures and checks a
read-only Desktop login. Docker must already be running.

Want all three demos? Run **`./gxr start all`** instead. Rerun either command to
resume: existing passwords and data are preserved. Newly loaded demo schemas
are added to the reader's access. A failed demo load or verification rolls back
that demo's transaction; earlier successful demos remain. Setup refuses schemas
not marked as belonging to this repo and never resets a replay.

`start` manages only this repo's default local Compose database. For an existing
compatible database configured separately in `.env`, use `./gxr up <demo>` and
the reader helper in the [connection guide](connect/README.md).

Now follow **[connect/README.md](connect/README.md)**:

1. Download Desktop from **[kineviz.com](https://kineviz.com)** → Download Kineviz Desktop.
2. Install and sign in yourself. The release checked for this guide is **v0.19.0**.
3. **Create New Project → Database Type → Google AlloyDB Omni**.
4. Enter `127.0.0.1`, port `55432`, database `kineviz_demo`, graph `paysim_graph`,
   and the read-only credentials from `secrets/reader.env`.
5. Confirm the project, check its schema, and run a [canvas query](demos/paysim-schemaless/queries/canvas/02-payments.sql).

![Kineviz Desktop's native AlloyDB connection form with the local demo settings](docs/images/alloydb-connection-fields.jpg)

Desktop 0.19.0 connection setup. The password is intentionally blank in this
screenshot; enter your reader password before confirming. See the
[illustrated connection guide](connect/README.md#4-create-the-project) for each step.

Desktop queries the database directly. Keep it and the database running while
exploring. **Query → SQL → PostgreSQL is a different, table-import workflow**;
it is not the connection path used here.

## Examples

| Demo | Database schema / graph | What to inspect |
|---|---|---|
| [paysim-schemaless](demos/paysim-schemaless/README.md) | `paysim_demo` / `paysim_graph` | 400 clients, 12,033 payments, shared identifiers, ring, collector and family false positive |
| [fraud-rings](demos/fraud-rings/README.md) | `fraud_demo` / `fraud_graph` | Shared devices, a four-account cycle and merchant payments |
| [edge-fleet](demos/edge-fleet/README.md) | `fleet_demo` / `fleet_graph` | Gateway concentration, single-person coverage, vulnerable firmware and dependencies |

```bash
./gxr list
./gxr start all
./gxr verify paysim-schemaless
./gxr query paysim-schemaless --number 1
```

Each demo has PostgreSQL schema/graph DDL, scalar SQL investigation queries and
graph-mode queries for Desktop. [Streaming](streaming/README.md) replays the
PaySim file directly or through Kafka. No cloud resources are created by these
commands. Local Docker images, volumes and processes consume disk and memory.

## What changed from Spanner

| Spanner source | This repo |
|---|---|
| Spanner Omni image and CLI | AlloyDB Omni SQL/PGQ image and psycopg |
| GoogleSQL / GQL | PostgreSQL SQL + `GRAPH_TABLE` |
| Dynamic graph labels/properties | JSONB storage with explicitly declared graph views and labels |
| `graphxr-database-proxy` | Native **Google AlloyDB Omni** project connector |
| No preview database password | Password-authenticated PostgreSQL, with a read-only Desktop login |
| Spanner dashboard / project export | New graph queries; old Spanner project/dashboard files are not imported |

The PaySim-style generator is synthetic, not the original PaySim simulator.
Planted signals are test fixtures, not proof of criminal intent or a validated
fraud model. See [provenance and MIT attribution](vendor/README.md).

## Stop, test, and hand off

```bash
./gxr test
.venv/bin/python tests/integration.py
./gxr stop
```

Integration tests require the three demos already loaded. They only read the
existing demo rows. Volumes survive `stop`.
Destructive resets are separate, explicitly confirmed commands documented in
[troubleshooting](docs/TROUBLESHOOTING.md). Never reset a database containing
unrelated work.

For a shared deployment, plan permissions, network access, backups and support
with [Kineviz Enterprise](https://kineviz.com/enterprise); the laptop's loopback
address is not an Enterprise connection endpoint.

See [verification status](docs/VERIFICATION.md) for what was actually tested.
Licensed under [MIT](LICENSE).
