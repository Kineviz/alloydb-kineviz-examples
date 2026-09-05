# Verification record

Tested September 4–5, 2026 in an isolated local Compose deployment. The user's
pre-existing AlloyDB and Spanner deployments were not modified.

| Check | Result |
|---|---|
| Database identity | AlloyDB custom-release image pinned in compose.yaml; PostgreSQL 19beta1; Google extensions present in the inspected build |
| Desktop version / UI | Installed v0.19.0; Create New Project → Google AlloyDB Omni and its seven connection fields inspected |
| PaySim full setup | 13,666 graph nodes, 25,266 graph edges, 12,033 transactions |
| PaySim findings | 8 shared identifier values; 4 with direct transfers; planted cycle present; family transfers absent |
| PaySim repeated setup | Passed, same row counts |
| Fraud example | 620 graph nodes, 3,319 graph edges; four planted cycle legs; no family transfers |
| Fleet example | 954 graph nodes, 2,012 graph edges; concentration gateway, lone coverage and dependency walk present |
| Scalar SQL | All 17 investigation/display queries executed and returned rows |
| SQL/PGQ | Native GRAPH_TABLE node/edge counts for all three graphs; two additional PaySim queries passed |
| Read-only login | Discovers and queries all three unqualified graph names with its search_path; no table write privileges |
| Unit tests | 14 tests pass, including launcher sequencing, database-creation guards, full 12,033-event batch/replay payload parity, invalid input, schema ownership and version/TLS guards |
| gxr Python bootstrap | Clean temporary checkout created its own venv, installed pinned dependencies and passed all 14 tests |
| gxr start | `start all` and subsequent default `start` passed against the existing local volume; all graph counts and the saved reader login verified |
| gxr replay | `replay --seconds 0` passed against the full PaySim dataset without duplicates; Kafka launcher sequencing is unit-tested |
| Kafka actors-only replay | Grew from 1,633 nodes / 1,200 edges to full verified PaySim totals |
| Repeated direct replay | Same full counts after replaying all 12,033 transactions again; no duplicates |
| Native connector implementation | Read-only tests using the local Kineviz schema mapper, category/expansion query builders, graph-mode rewrite and result mapper passed for all three graphs and all four canvas query files |

These checks do **not** establish a production deployment, managed AlloyDB
compatibility, a supported release guarantee for the preview, or an automated
end-to-end Desktop canvas test. The connection form was inspected, but no new
Desktop project was created or signed in on the user's behalf. The guide's final
query-and-expand check remains the user's acceptance step.

The new launcher's missing-database creation branch is covered by a mocked unit
test; the real `start` runs reused the existing database and reader. They do not
constitute a fresh-volume end-to-end installation test.

Reproduce core checks with:

```bash
./gxr test
.venv/bin/python tests/integration.py
.venv/bin/python tools/check_reader.py
```
