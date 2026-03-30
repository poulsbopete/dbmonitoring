# Sample: Datadog SQL Server Dashboard Description

Use this screenshot and description as a starting point to rebuild the equivalent
dashboard in Elastic using Cursor + Elastic Agent Skills.

![Datadog SQL Server Overview](https://raw.githubusercontent.com/poulsbopete/dbmonitoring/main/assets/sample-dashboards/datadog-sqlserver-overview.png)

---

## Datadog SQL Server Dashboard — "SQL Server Overview"

### Widgets visible in screenshot (top to bottom, left to right)

**Row 1 — Header / Agent health**
- SQL Server logo tile
- "SQL Server — Agents Up" — count metric showing **1 warn / 7 total**
- "SQL Server Monitor Status" — Warn: 3 / OK: 61
- "SQL Server Events" table — source, message, date

**Row 2 — KPI tiles**
- **Failed Logins** — event count, 1w window (shows "No data")
- **Batch req…** — Batch requests/sec — **143.8 reqs/s** (green)
- **User co…** — User connections — **5.42 conns** (green)
- **Buffer c…** — Buffer cache hit ratio — **100.0%** (green)

**Row 3 — Time series (right panel)**
- **Page splits (per sec)** — line chart, ~80 peak
- **SQL compilations/s** — line chart with spikes to 4k
- **SQL re-compilations** — line chart

**Row 4 — Usage area / time series**
- **User Connections** — stacked area chart (blue/purple, 4h window, 12:00–15:00)
- **Batch Requests (per sec)** — line chart with load spikes (4h window)

**Top filters**: `scope`, `db`, `env` dropdowns

**Default time range**: Last 1 Hour

---

## Elastic Equivalent — Prompt for Cursor

Paste the following into Cursor to recreate this dashboard in Elastic:

```
I have a screenshot of a Datadog SQL Server monitoring dashboard.
Here is what it shows:

KPI row: Batch requests/sec (143.8), User connections (5.42), Buffer cache hit ratio (100%).
Time series: User Connections stacked area chart over 4 hours broken down by instance.
Time series: Batch Requests per second line chart over 4 hours.
Additional metrics: Page splits/sec, SQL compilations/sec, SQL recompilations/sec.
Status table: Monitor name, status (Warn/OK), group.

Please build an equivalent Kibana dashboard using the Elastic Agent Skills.
The data is in index pattern: metrics-sqlserverreceiver.otel.otel-default
Key fields:
- sqlserver.user.connection.count (user connections)
- sqlserver.batch_sql_request.count (batch requests — counter_long, cast to double)
- sqlserver.page.buffer_cache.hit_ratio (buffer cache %)
- sqlserver.page.split.rate (page splits)
- sqlserver.sql.compilation.rate (SQL compilations)
- sqlserver.sql.recompilation.rate (SQL recompilations)
- service.instance.id (to split by instance)
```
