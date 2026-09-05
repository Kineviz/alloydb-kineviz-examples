# Upstream provenance

These three unmodified synthetic-data generators and the root MIT LICENSE come
from https://github.com/Kineviz/spanner-omni-kineviz-examples at commit
`fb395d58514836043b5daba0ea5e47448802864a` (retrieved 2026-09-04).

| Local file | Original path |
|---|---|
| paysim.py | demos/paysim-schemaless/data/generate.py |
| fraud.py | demos/fraud-rings/data/generate.py |
| fleet.py | demos/edge-fleet/data/generate.py |

Their module comments and CSV manifests describe the original Spanner target.
Only their generated data is reused here. The loader translates those manifests
to PostgreSQL table names; none of their Spanner commands or DDL are executed.
The PaySim-style generator is not the original PaySim simulator and does not
model a bank's complete ledger or balances. All actors and payments are synthetic.
