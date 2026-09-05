# PaySim-style payments on AlloyDB Omni

```bash
./gxr up paysim-schemaless
./gxr verify paysim-schemaless
```

Connect the Desktop project directly to **Google AlloyDB Omni**, database
`kineviz_demo`, graph **paysim_graph**. Follow [connect](../../connect/README.md).

The unmodified upstream generator creates 400 clients and 12,033 transactions:
12,000 background events plus 33 planted events. A family of three shares a
phone but never exchanges payments; a four-account ring shares identifiers and
does exchange payments. A separate collector receives money from several
accounts. These are synthetic test fixtures, not a fraud verdict.

Read the queries in order:

1. Shared identifiers return eight **values**, not eight rings.
2. Requiring a direct payment leaves four shared values from the planted ring.
3. Collector accounts receive transfers from at least three distinct senders.
4. Cash-out queries show payments over 1,000 to synthetic high-risk merchants.
5. The bounded four-account-cycle query follows money returning to its origin.

`queries/*.sql` return scalar results through psql or `./gxr query ... --number N`.
`queries/pgq/` demonstrates database-native GRAPH_TABLE with explicit columns.
`queries/canvas/` uses Kineviz's COLUMNS(*) shorthand to render graph entities.
They are intentionally separate: Kineviz's shorthand is not raw PostgreSQL syntax.

The slug is retained from the Spanner source for familiarity. Storage is two
JSONB-backed graph tables, but graph labels are declared through filtered views;
this port does not claim Spanner-style dynamic graph DDL. See [compatibility](../../docs/COMPATIBILITY.md).

For the graph building up over time, use [replay](../../streaming/README.md).
