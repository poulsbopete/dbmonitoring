# Sample: Datadog MongoDB Dashboard Description

Use this text as a starting point if you do not have a screenshot of an existing
Datadog MongoDB dashboard. Paste it into Cursor and ask Claude to rebuild it in Elastic.

---

## Datadog MongoDB Dashboard — "MongoDB Cluster Health"

### Widgets (top to bottom, left to right)

**Row 1 — KPI tiles**
- Current Connections — `mongodb.connections.current`
- Opcounters Insert/sec — `mongodb.opcounters.insert` (rate)
- Resident Memory (MB) — `mongodb.mem.resident`
- Replication Lag (s) — `mongodb.replset.replicationlag`

**Row 2 — Time series**
- "Operations per Second" — stacked area: insert, query, update, delete, command, getmore
- "Open Connections" — line by `replset_name`

**Row 3 — Time series**
- "Memory (Resident vs Virtual)" — dual-line, MB
- "Network Bytes In/Out" — area: bytes_in vs bytes_out

**Row 4 — Table: Database Breakdown**
| Database | Collection Count | Total Size (MB) | Index Size (MB) |
|---|---|---|---|

**Row 5 — Single tile**
- Replication Lag over time — line chart for each secondary host

**Filters**: `replset_name`, `host`, `environment`

**Default time range**: Last 3 hours
