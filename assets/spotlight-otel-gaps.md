# Spotlight-style monitoring vs OpenTelemetry (lab notes)

This workshop adds **Quest Spotlight–like** dashboards on top of synthetic OTLP data. Use this page when customers ask what OTel can and cannot replace out of the box.

## Collection model

| Target | Lab simulation | Typical OTel path |
|--------|----------------|-------------------|
| SQL Server on-premises | `sqlserverreceiver` metrics + custom `sqlserver.spotlight.*` | [OpenTelemetry SQL Server receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/sqlserverreceiver) on the Windows/Linux host |
| SQL Server on Azure VM | Same receiver on the VM; `cloud.provider` / `cloud.platform` set by the collector or `resourcedetection` | Azure VM metadata + agent on guest OS |
| Azure SQL Managed Instance / Azure SQL Database | **Gap**: no full OS/SQL process surface from inside the DB PaaS boundary | Database-level metrics via Azure Monitor export → OTel, Elastic integrations, or Elastic Azure native metrics — not identical to Spotlight’s host + SQL combo |
| MongoDB on-premises | `mongodbreceiver` / self-managed scrapes; lab uses `mongodbatlas` dataset name for convenience | Official MongoDB exporter → OTLP |
| MongoDB Atlas | Atlas metrics API / log export → collector → OTLP | Same pattern; attribute `mongo.deployment=atlas`, `cloud.provider` |

## Metrics aligned with Spotlight (lab)

Synthetic gauges (not all are standard semantic conventions):

- `spotlight.health.severity` — 0 informational, 1 healthy, 2 warning, 3 critical; dimensions `spotlight.grid_row`, `spotlight.entity_type` (`sqlserver`, `windows`, `mongodb`).
- `sqlserver.spotlight.*` — sessions, performance rating, CPU, memory breakdown (incl. PLE, procedure cache), process counts, virtualization overhead, error-log rate, services running.

## Gaps vs full Spotlight

- **Deep wait stats / latch / file-level I/O**: Partially covered by `sqlserverreceiver`; Spotlight-specific breakdowns may need custom queries or DBM-style agents.
- **Windows OS health (paging, disk queues, full service control)**: Not fully modeled by SQL receiver alone — add **host metrics** (`hostmetrics` receiver) and **Windows performance counters** where needed.
- **Blocking chain / who blocks whom**: Usually requires SQL text or extended events — OTel SQL receiver exposes summaries, not always session-level chains.
- **Error log text**: Spotlight parses ERRORLOG; OTel would use **logs** (not only metrics) with a filelog or sidecar tailing the log.
- **PaaS SQL (Azure SQL / MI)**: No “Windows host” row in the heat map; health must be derived from **database/engine metrics** and platform signals.

## Heat map colours in Kibana

Lens maps cell **value** to a colour ramp. Tune the palette so higher `spotlight.health.severity` maps toward **red** and low values toward **blue/green** (Panel settings → Colour).
