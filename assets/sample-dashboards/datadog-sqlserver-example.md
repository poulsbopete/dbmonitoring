# Sample: Datadog SQL Server Dashboard Description

Use this text as a starting point if you do not have a screenshot of an existing
Datadog SQL Server dashboard. Paste it into Cursor and ask Claude to rebuild it in Elastic.

---

## Datadog SQL Server Dashboard — "SQL Server Overview"

### Widgets (top to bottom, left to right)

**Row 1 — KPI tiles**
- User Connections (current) — `sqlserver.connections.active`
- Batch Requests/sec — `sqlserver.stats.batch_requests` (rate)
- Buffer Cache Hit Ratio (%) — `sqlserver.buffer.cache_hit_ratio`
- Total Deadlocks — `sqlserver.stats.deadlocks` (cumulative)

**Row 2 — Time series**
- "User Connections Over Time" — line, by `host`
- "Batch Requests/sec" — area, by `host`
- "Lock Waits/sec" — line, by `host` (uses `sqlserver.stats.lock_waits`)

**Row 3 — Per-database breakdown**
- "Page Read/Write Latency (ms)" — grouped bar by `db` showing read vs write
- "Database Size (bytes)" — horizontal bar ranked by `sqlserver.database.size`

**Row 4 — Table**
- "Top Databases by Lock Waits" — columns: database, lock_waits, avg_wait_time_ms,
  deadlocks, active_connections

**Filters at top**: `host`, `environment` (prod / staging)

**Default time range**: Last 4 hours
