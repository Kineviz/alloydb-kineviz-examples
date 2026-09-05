# Compatibility and preview scope

Checked September 4–5, 2026.

- **Kineviz Desktop:** v0.19.0, native `Google AlloyDB Omni` project connection.
- **Database:** Google's custom AlloyDB Omni PostgreSQL **19beta1** SQL/PGQ build,
  pinned in `compose.yaml` to digest
  `sha256:fc414e1d1cbd3933cecb39e754a964ed3345c84b72a946bf7a529a058d490987`.
- **Image platform:** linux/amd64; local tests use emulation on an ARM Mac.
- **Not supported by this native path:** standard Omni 16.x, Spanner GQL, the
  Spanner proxy driver, or a managed AlloyDB instance lacking SQL/PGQ.

`SELECT version()` in the preview reports PostgreSQL, not the AlloyDB brand.
Google's `google_columnar_engine`, `google_db_advisor` and `alloydb_scann` entries
in `pg_available_extensions` distinguish the inspected build. We do not enable
those extensions or claim a columnar-engine benchmark.

Preview image availability and use rights are controlled by Google. A user may
need access from their Google contact. No registry credential is included. If
pulling fails, confirm access to the PostgreSQL 19 graph preview; do not switch
silently to an ordinary Omni image. Hardware minimums for a standard release are
not a guarantee for this custom preview.

The JSONB PaySim store preserves the source generator's flexible properties.
SQL/PGQ views and graph labels are **explicitly declared**. Adding JSON keys does
not expose them as new graph properties; update the view and graph definition.
Adding a new node category is not the Spanner demo's DYNAMIC LABEL operation.

References:

- [Kineviz Desktop v0.19.0 release](https://github.com/Kineviz/kineviz-desktop/releases/tag/v0.19.0)
- [PostgreSQL property graphs](https://www.postgresql.org/docs/19/ddl-property-graphs.html)
- [CREATE PROPERTY GRAPH syntax](https://www.postgresql.org/docs/19/sql-create-property-graph.html)
- [Graph privileges](https://www.postgresql.org/docs/19/sql-grant.html)
- [Standard AlloyDB Omni installation](https://docs.cloud.google.com/alloydb/omni/containers/current/docs/quickstart)

The last link describes the standard release, **not** provisioning rights or
support guarantees for the pinned custom SQL/PGQ preview.
