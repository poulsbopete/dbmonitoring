# Sample: Dynatrace PostgreSQL Dashboard Description

Use this text as a starting point if you do not have a screenshot of an existing
Dynatrace PostgreSQL dashboard. Paste it into Cursor and ask Claude to rebuild it in Elastic.

---

## Dynatrace PostgreSQL Dashboard — "PostgreSQL Service Overview"

### Tiles (top to bottom, left to right)

**Row 1 — Single-value tiles**
- Active Connections — gauge, threshold: warn > 80, critical > 150
- Transactions/sec — `databaseservice.transactions` (rate)
- Cache Hit Rate (%) — derived: `pg_stat_bgwriter.hit / (hit + read)`
- Deadlocks (last 1 h) — count

**Row 2 — Charts**
- "Active Sessions" — line over time, split by database name
- "Transaction Throughput" — stacked area: commits vs rollbacks vs rollbacks_ratio

**Row 3 — Charts**
- "Query Wait Times by State" — heatmap; states: client, lock, io, cpu
- "Replication Lag (replica)" — line chart, seconds behind primary

**Row 4 — Table: Top 10 heaviest queries**
| Query Digest | Avg Duration (ms) | Calls/min | Rows Returned | Database |
|---|---|---|---|---|

**Filters**: `database.name`, `host.name`, `environment`

**Default time range**: Last 2 hours
