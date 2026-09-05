# Shared devices and payment rings

```bash
./gxr up fraud-rings
./gxr verify fraud-rings
```

Use the native **Google AlloyDB Omni** connector with graph **fraud_graph**.
The deterministic dataset has 300 clients, 310 devices, 10 merchants, 2,007
client-to-client payments and 1,001 merchant payments. Three family members
share a device without transferring to one another. Four other accounts share
a device and form a payment cycle; a second group pays a collector.

The ordered SQL files inspect shared devices, four-account cycles, collectors
and merchant payments. The canvas file renders device relationships directly.
Shared devices and payment patterns are investigative signals, not proof of intent.

[Connection steps](../../connect/README.md) · [Upstream provenance](../../vendor/README.md)
