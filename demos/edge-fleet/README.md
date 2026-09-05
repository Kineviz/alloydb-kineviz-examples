# Edge fleet dependencies

```bash
./gxr start edge-fleet
./gxr verify edge-fleet
```

Use the native **Google AlloyDB Omni** connector with graph **fleet_graph**.
The synthetic fleet contains 900 devices, 30 gateways, 12 sites, six firmware
versions and six technicians. Verification checks that the busiest gateway
has more than twice the devices of the runner-up, and that the dependency
chain and single-person site coverage are present.

Queries cover gateway concentration, lone coverage, synthetic firmware advisory
exposure, and a cycle-safe dependency walk bounded to four hops. The advisory
identifier is synthetic; it is not a claim about a real vulnerability.

[Connection steps](../../connect/README.md) · [Upstream provenance](../../vendor/README.md)
