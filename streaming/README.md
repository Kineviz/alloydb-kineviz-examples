# Replay the payments into AlloyDB Omni

The generator writes the entire synthetic transaction history first. Replay
adds those recorded events over time; it does not generate new transactions
live. Kineviz's native AlloyDB project connection reads the same property graph.
No graphxr-database-proxy is involved in either replay route.

## Start from actors and identifiers only

On a new dedicated demo database, before the full PaySim load:

```bash
./gxr up paysim-schemaless --entities-only
./gxr verify paysim-schemaless --entities-only
```

This seeds 1,633 non-transaction nodes and 1,200 identifier edges. There are eight
shared identifier values and zero direct-transfer matches. It **does not delete**
an existing full dataset. To restart a disposable demo, explicitly reset only
its schema using [the cleanup guide](../docs/TROUBLESHOOTING.md).

## Route 1: direct PostgreSQL replay

```bash
.venv/bin/python streaming/replay.py --via direct --seconds 60
```

## Route 2: preserve the Kafka leg

```bash
.venv/bin/pip install -r streaming/requirements.txt
docker compose -f streaming/compose.yaml up -d --wait
.venv/bin/python streaming/replay.py --via kafka --seconds 60
```

Kafka is local-only on port 19096, distinct from the source repo's broker.
The producer and database sink run on your host in this small lab harness;
only the broker is containerized. Each run creates and prints a fresh topic.
A single partition preserves the generated event order. The target 60 seconds
uses batches of 100 events; database/broker overhead can make it longer. Use
`--seconds 0` for an unpaced correctness check, not a throughput benchmark.

Both routes atomically write a transaction and its sender/receiver edges, with
stable keys and conflict handling. Kafka offsets are committed **after** the
database commit. Repeating a run does not duplicate graph rows. This is not an
exactly-once production streaming system: the command restarts the file in a
new topic after failure, tolerating already-landed rows. Topics persist until
you explicitly clean up the dedicated broker.

## Check what landed

```bash
./gxr verify paysim-schemaless
./gxr query paysim-schemaless --number 2
```

The final totals must match batch setup: 13,666 nodes, 25,266 edges, 12,033
transaction nodes, eight shared identifier values, four with direct payments.
Verification also confirms the family's lack of transfers and the planted cycle.

In Desktop, rerun `queries/canvas/02-payments.sql` or configure a query-backed
dashboard to refresh. The native connector is live when queried; it is not an
automatic canvas subscription. Replaying onto a full dataset tests idempotency
but will not make the graph appear to grow.

Stop without removing data: `docker compose -f streaming/compose.yaml stop`.
