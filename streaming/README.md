# Replay the payments into AlloyDB Omni

The generator writes the entire synthetic transaction history first. Replay
adds those recorded events over time; it does not generate new transactions
live. Kineviz's native AlloyDB project connection reads the same property graph.
No graphxr-database-proxy is involved in either replay route.

## Clear transactions and start streaming in one command

From the repository root, with Docker running:

```bash
./gxr replay --restart
```

**Destructive by design:** `--restart` deletes all transaction nodes and their
incident edges in this repo's owned `paysim_demo` schema, including custom
transactions there. It preserves actors, shared identifiers, the property graph
and other demo schemas. Synthetic payments can be regenerated; custom transaction
changes require a backup to recover. Stop any other replay process first.

The command prepares Python and the local database, clears previous payments,
seeds and verifies 1,633 actors/identifiers and 1,200 identifier edges, configures
the reader, then replays all 12,033 payments with a 60-second target and verifies
the final counts. It also works on a fresh local demo database. No schema reset
or separate setup command is needed.

For Kafka, use **`./gxr replay --restart --via kafka`**. Its dependency and broker
are prepared before transactions are cleared.

Open **Dashboard → PaySim · AlloyDB full (imported)** to watch the metrics grow;
[import the dashboard first](../connect/README.md#6-load-the-live-paysim-dashboard)
if needed. Desktop setup and dashboard import remain manual. Existing canvas
nodes do not disappear automatically when database transactions are deleted.

Deletion and actors-only verification commit together. A later replay failure
can leave a partial dataset: retry `./gxr replay` **without** `--restart` to retain
landed rows. Without `--restart`, replay never deletes existing transactions.

## Start from actors and identifiers only

On a new dedicated demo database, before the full PaySim load:

```bash
./gxr start --entities-only
```

This seeds 1,633 non-transaction nodes and 1,200 identifier edges. There are eight
shared identifier values and zero direct-transfer matches. It **does not delete**
an existing full dataset. To restart a disposable demo, explicitly reset only
its schema using [the cleanup guide](../docs/TROUBLESHOOTING.md).

## Route 1: direct PostgreSQL replay

```bash
./gxr replay
```

## Route 2: preserve the Kafka leg

```bash
./gxr replay --via kafka
```

The Kafka command installs its dependency and starts the broker automatically.
Both replay commands verify the final graph and default to a 60-second target.
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

Stop the database and broker without removing data: `./gxr stop`.
