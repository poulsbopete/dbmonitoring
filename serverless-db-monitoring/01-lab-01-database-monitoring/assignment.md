---
slug: lab-01-database-monitoring
id: a8za8uie5rvp
type: challenge
title: Database Monitoring — MySQL · PostgreSQL · SQL Server · MongoDB · Db2 · Oracle
teaser: Explore live OTel data for six databases in Kibana—quick path is dashboards
  + an alert from a panel. Advanced Cursor + Agent Skills lab is folded at the bottom
  of the assignment.
notes:
- type: text
  contents: "## While you wait… \U0001F9DB\n\n<iframe src=\"https://poulsbopete.github.io/Vampire-Clone/\"\n
    \ width=\"100%\" height=\"800\" frameborder=\"0\"\n  allow=\"autoplay\" style=\"border-radius:8px;display:block\">\n</iframe>\n\n*Your
    Elastic environment and database telemetry are generating in the background.*\n"
- type: text
  contents: |
    ## Data is loading…

    The track bootstrap is generating telemetry for all six database
    platforms via OpenTelemetry → Elastic managed OTLP:

    ```
    MySQL · PostgreSQL · SQL Server · MongoDB · Db2 · Oracle
                │
                │  Python OTLP HTTP  (db_otel_generator.py)
                ▼
        Elastic managed OTLP
                │
                ▼
      Observability Serverless
      logs-mysql.*          ← slow queries + error logs
      metrics-postgresql.*  ← connections, commits, deadlocks, size
      metrics-sqlserver.*   ← connections, lock waits, cache hit, I/O latency
      metrics-mongodb.*     ← operations, memory, replication lag
      metrics-db2.*         ← connections, buffer pool, log util, tablespaces
      metrics-oracledb.*    ← sessions, tablespaces, parses, PGA memory
                │
                ▼
         Kibana Dashboards  (10 deployed automatically)
    ```

    No proprietary agents. Pure OpenTelemetry.
- type: text
  contents: |
    ## Elastic vs Datadog Database Monitoring (DBM) vs Dynatrace

    | Capability | Datadog DBM | Dynatrace | **Elastic** |
    |---|---|---|---|
    | Slow query capture | ✓ proprietary agent | ✓ OneAgent | ✓ **OpenTelemetry** |
    | Full query text | ✓ | Limited | ✓ |
    | MySQL | ✓ | ✓ | ✓ |
    | PostgreSQL | ✓ | ✓ | ✓ |
    | **SQL Server** | ✓ extra cost | ✓ | ✓ **same price** |
    | **MongoDB** | ✓ extra cost | Limited | ✓ |
    | **IBM Db2** | ✓ extra cost | ✓ extra cost | ✓ **same price** |
    | **Oracle** | ✓ extra cost | ✓ extra cost | ✓ **same price** |
    | Custom dashboards | Template-only | Template-only | **Unlimited — Lens + ES\|QL** |
    | AI-assisted dashboard building | ✗ | ✗ | **✓ Cursor + Agent Skills** |
    | Bring your own telemetry (OTel) | Limited | Limited | **Native** |
    | Data sovereignty | ✗ (vendor cloud) | ✗ | ✓ **your cluster** |
    | Vendor lock-in | High | High | **None — open standards** |
tabs:
- id: cz9hvpxnxobm
  title: Elastic Serverless
  type: service
  hostname: es3-api
  path: /app/dashboards#/list?_g=(filters:!(),refreshInterval:(pause:!f,value:30000),time:(from:now-1m,to:now))
  port: 8080
  custom_request_headers:
  - key: Content-Security-Policy
    value: 'script-src ''self'' https://kibana.estccdn.com; worker-src blob: ''self'';
      style-src ''unsafe-inline'' ''self'' https://kibana.estccdn.com; style-src-elem
      ''unsafe-inline'' ''self'' https://kibana.estccdn.com'
  custom_response_headers:
  - key: Content-Security-Policy
    value: 'script-src ''self'' https://kibana.estccdn.com; worker-src blob: ''self'';
      style-src ''unsafe-inline'' ''self'' https://kibana.estccdn.com; style-src-elem
      ''unsafe-inline'' ''self'' https://kibana.estccdn.com'
- id: ns5os71akjta
  title: Terminal
  type: terminal
  hostname: es3-api
difficulty: ""
timelimit: 0
enhanced_loading: null
---

# Database Monitoring — MySQL · PostgreSQL · SQL Server · MongoDB · Db2 · Oracle

## Part 1 — Explore the pre-built dashboards

Ten dashboards were deployed automatically when this track started (six database platforms plus SQL Server overview and three Spotlight-style views).
The lab opens on the **Elastic Serverless** tab first (the **Terminal** tab is for troubleshooting or optional Cursor steps). Open **Dashboards** from the left nav. Pre-built dashboards open with **Last 1 minute** so live OTLP charts populate quickly. For narrated walkthroughs, widen the time picker (for example **Last 2 hours**). The **AI recommendations** table at the bottom uses the same global time range as the rest of the dashboard—if it is empty after a workflow run, try **Last 15 minutes** or more (index **db-monitoring-recommendations**, filtered by **`database_platform`**). The workflow **Database Monitoring — AI recommendations** runs on a **10-minute schedule** and writes **six** recommendations per run (one per engine); you can also trigger it manually under **Management → Workflows**.

**Easy path:** finish **Part 1** (dashboards), then **Part 2** (create an alert from a panel—about two minutes). That is a complete lap for most audiences. **Optional:** the **Cursor + Elastic Agent Skills** walkthrough (rebuild a Datadog/Dynatrace-style dashboard) is **rolled up at the bottom**—expand it only when you have time and a laptop with Cursor.


---

### MySQL — Slow Query & Error Monitoring

**Dashboard:** `MySQL — Slow Query & Error Monitoring`

Walk through each panel:

1. **KPI row** — total slow queries, avg/max query time, error count. Notice that
   `ecommerce` and `analytics` produce the most slow queries.
2. **Slow Query Rate** — stacked area by database. Load peaks during business hours
   (9am–6pm weekdays) — same pattern your OLTP workload would show.
3. **Top Tables** — `orders`, `customers`, and `sessions` drive the most slow queries.
4. **Query vs Lock Time** — `analytics` has disproportionately high lock time relative
   to query time — a sign of write contention.
5. **Slowest Queries table** — full breakdown: operation type, table, avg execution time,
   max execution time, rows examined. Every field is in the OTel log record — no
   proprietary schema required.
6. **Error Log Trend** — stacked by severity (ERROR / WARNING). Correlate error spikes
   with the slow query rate above.

> **Talking point vs Datadog DBM:**
> Elastic captures identical fields — full query text, table, operation, row efficiency —
> ingested via standard OpenTelemetry log records. No `dd-agent` required.

---

### SQL Server — Performance & Health *(most important for this customer)*

**Dashboard:** `SQL Server — Performance & Health`

Walk through each panel:

1. **User Connections** — production peaks at 400+. The secondary instance stays under 200.
2. **Buffer Cache Hit %** — both instances stay above 96%. A dip below 95% is an early
   warning for memory pressure.
3. **Lock Wait Time** — spikes visible during simulated batch jobs. Correlate with the
   connection count chart above.
4. **I/O Read vs Write Latency by Database** — `SalesDB` and `ReportingDB` have the
   highest read latency. Candidates for index or storage tuning.
5. **Batch Requests** — throughput trend. Useful baseline for capacity planning.
6. **Instance Summary table** — side-by-side: max connections, cache hit %, avg lock wait,
   deadlocks.

> **Talking point vs Datadog DBM:**
> SQL Server monitoring is a **paid add-on** in Datadog Database Monitoring. In Elastic,
> it is the same price as any other OTel metric. The `sqlserverreceiver` pulls from
> standard SQL Server DMVs — no WMI poller, no Windows-only constraint.

**For reference — this is what the Datadog SQL Server dashboard looks like:**

![Datadog SQL Server Overview](https://raw.githubusercontent.com/poulsbopete/dbmonitoring/main/assets/sample-dashboards/datadog-sqlserver-overview.png)

Notice: Datadog exposes the same core KPIs (batch requests/s, user connections, buffer
cache %) but requires the Datadog Agent and a DBM add-on licence. The Elastic version
covers identical metrics via OpenTelemetry at no extra cost, with full ES|QL flexibility
for custom panels.

---

### Spotlight-style views (Quest Spotlight comparison)

Two dashboards approximate **Quest Spotlight** for customers evaluating “single-pane
SQL Server + host health” tools.

**Dashboard:** `Spotlight — Severity grid (SQL Server, Windows, MongoDB)`

1. **Severity grid (treemap)** — Same ES|QL a Lens **heat map** would use: **time bucket** ×
   **grid row** (SQL instance, **Windows** host row, **MongoDB** node), metric = max
   `spotlight.health.severity` (**0**–**3**). **POST /api/dashboards** on Serverless does not
   accept inline Lens **heat map**; the treemap is a supported 2D partition. **Edit in Lens**
   and switch to **Heat map** if your Kibana build supports ES|QL heat maps in the UI. Tune
   colours so higher severity reads hotter.
2. **Severity lines** — Same data as a multi-line trend for narration.
3. **Ranking + detail table** — Average / peak severity by row, with `cloud.platform`
   (on-premises, **Azure** VM, **Azure SQL Managed Instance**, **MongoDB Atlas** on AWS).

Synthetic data includes **four** SQL Server targets (two on-prem, Azure VM, Azure MI) and
**three** MongoDB nodes (two on-prem replica set, one Atlas-style primary).

**Dashboard:** `Spotlight — SQL Server Overview (synthetic)`

Filtered to **`mssql-prod-01`**. Walk the panels: **Sessions** (response time, counts,
utilisation bar), **Performance health** (gauge + system table: build, host, cloud,
virtualisation), **Processes** (total / system / user / blocked + batch counter),
**Virtualization overhead**, **CPU** gauge, **Memory** (total, buffer cache, PLE,
procedure cache), **Background** (error-log rate, services running).

**OTel coverage notes:** See `assets/spotlight-otel-gaps.md` in the repo for what the
OpenTelemetry SQL Server receiver covers today versus Spotlight-only depth (blocking
chains, ERRORLOG text, full Windows OS counters, PaaS SQL boundaries).

---

### PostgreSQL — Performance & Health

**Dashboard:** `PostgreSQL — Performance & Health`

1. **Active Connections** — primary vs replica, peaks during business hours.
2. **Database Size** — `warehouse` is substantially larger than `catalog` and `auth`.
3. **Rows Inserted / Updated / Deleted** — write volume trends over time.
4. **Deadlocks** — rare but visible spikes under heavy load, broken out by database.
5. **Database Summary table** — max connections, size, deadlocks, commits, rollbacks
   across all three databases at a glance.

---

### MongoDB — Operations & Health

**Dashboard:** `MongoDB — Operations & Health`

1. **Operations by Type** — `query` dominates; `insert`/`update`/`delete` clearly visible.
2. **Connections** — primary stays consistently higher; secondary tracks at ~30% of primary.
3. **Replication Lag** — secondary shows occasional lag spikes (1–5 s) under peak load.
4. **Memory** — resident vs virtual grows linearly with connection count.
5. **Document Operations** — insert/update/delete rates over time.
6. **Database Size** — `user_data` is the largest collection.
7. **Network In / Out** — overall throughput baseline.

> **Talking point vs Dynatrace:**
> MongoDB monitoring is limited in Dynatrace and a **paid add-on** in Datadog.
> Elastic supports it natively — same OTLP pipeline, same Kibana dashboards API.

---

### IBM Db2 — Performance & Health (LUW)

**Dashboard:** `IBM Db2 — Performance & Health (LUW)`

1. **Active connections** — production and standby instances; load follows the shared business-hours curve.
2. **Buffer pool hit ratio** — values on a 0–1 scale; the SLO workflow tracks samples ≥ 0.88.
3. **Log utilization %** — transaction log headroom; spikes correlate with write-heavy load.
4. **Avg lock wait (ms)** — concurrency pressure alongside connection counts.
5. **Connections over time** — stacked by `service.name` (`db2-production` vs `db2-standby`).
6. **Buffer pool hit ratio trend** — same signal as the KPI row, over time per instance.
7. **Tablespace footprint** — used vs total GB for USERSPACE1, TEMPSPACE1, SYSCATSPACE, WAREHOUSE_TS (where present).
8. **Deadlocks & sort overflows** — monotonic counters from the synthetic workload.
9. **Log utilization over time** — split by `host.name` for prod vs DR storytelling.

> **Talking point vs Datadog / Dynatrace:**
> Db2 monitoring is often a **paid add-on** or a separate module. In Elastic, LUW-style metrics
> flow through the same **OpenTelemetry → managed OTLP** path as the other engines, with ES|QL dashboards on
> `metrics-db2receiver.otel.otel-default`.

---

### Oracle — Performance & Health

**Dashboard:** `Oracle — Performance & Health`

1. **Active Sessions** — active vs inactive sessions over time. Alert fires at 250 active sessions.
2. **Processes** — total Oracle processes across both instances.
3. **Physical Reads** — cumulative physical I/O reads; spikes indicate storage pressure.
4. **User Commits** — transaction commit rate baseline.
5. **Sessions Over Time** — stacked area of active vs inactive sessions by instance.
6. **Tablespace Utilisation** — used vs total GB for all tablespaces (ANALYTICS, FINANCE,
   USERS, HR, SYSTEM, TEMP, UNDO). Useful for capacity planning conversations.
7. **Physical vs Logical Reads** — ratio indicates buffer cache efficiency. High physical
   reads relative to logical reads = undersized SGA.
8. **Parse Rate** — hard parses vs total parse calls. A high hard-parse ratio signals poor
   SQL plan cache reuse — an immediate tuning recommendation.
9. **Active Transactions** — in-flight transaction count per instance.
10. **PGA Memory** — Program Global Area memory consumption per instance.

> **Talking point vs Datadog / Dynatrace:**
> Oracle monitoring is a **paid add-on** in both Datadog and Dynatrace. In Elastic, the
> `oracledbreceiver` ships via the same standard OTLP pipeline at no extra cost.
> See: [elastic.co/docs/reference/integrations/oracle](https://www.elastic.co/docs/reference/integrations/oracle)

---

## Part 2 — Add an alert

When you are ready, add a threshold alert directly from Kibana:

1. In the **SQL Server** dashboard, hover over the **Lock Wait Time** panel → **⋮** → **Create alert**.
2. Set: **Lock wait avg > 50 ms** for **5 minutes**.
3. Optionally configure a Slack or email connector in **Stack Management → Connectors**.

> This takes ~2 minutes. Datadog charges per alert rule per host. In Elastic, alerts
> are unlimited and built on the same query engine as the dashboards.

### Cross-project search and cases

Pre-built alert rules can run the **Database Monitoring — Root Cause Analysis** workflow, which creates an **Observability case** with an AI investigation summary. After a case exists, you can **enrich** the investigation using Elastic **[Cross-project search](https://www.elastic.co/docs/explore-analyze/cross-project-search)** (technical preview): in the Elastic Cloud console, open your **Observability** Serverless project, go to **Cross-project search**, and **link** a **Security** Serverless project (or other projects you use). With projects linked, searches from Observability can span linked indices—so you can check for **security-relevant context** (for example detections or authentication anomalies) while triaging a database incident, without manually switching projects for every query.

---

## Troubleshooting

If charts are empty, verify the data pipeline:

```bash
source ~/.bashrc

# Check generator is running
ps aux | grep db_otel_generator | grep -v grep

# Restart if needed
nohup python3 /opt/dbmonitoring/tools/db_otel_generator.py \
  --otlp-endpoint "${WORKSHOP_OTLP_ENDPOINT}" \
  --otlp-auth "${WORKSHOP_OTLP_AUTH_HEADER}" \
  --live \
  >> /tmp/db-monitoring-logs/generator.log 2>&1 &

# Watch live output
tail -f /tmp/db-monitoring-logs/generator.log

# Confirm data is reaching Elastic (spot-check each stream)
curl -s -H "Authorization: ApiKey ${ES_API_KEY}" \
  "${ES_URL}/metrics-sqlserverreceiver.otel.otel-default/_count" | jq .count
curl -s -H "Authorization: ApiKey ${ES_API_KEY}" \
  "${ES_URL}/metrics-db2receiver.otel.otel-default/_count" | jq .count
curl -s -H "Authorization: ApiKey ${ES_API_KEY}" \
  "${ES_URL}/metrics-oracledbreceiver.otel.otel-default/_count" | jq .count
```

---

## Optional — Cursor + Elastic Agent Skills (expand to use)

<details>
<summary><strong>Optional: rebuild a competitor dashboard in Cursor</strong> (Agent + <code>kibana-dashboards</code> skill — laptop with this track’s credentials)</summary>

This is the **"WOW moment"** of the demo. You will take a description (or screenshot)
of an existing Datadog or Dynatrace dashboard and rebuild it in Elastic in under 2 minutes
using Claude in Cursor.

### Step 1 — Copy your credentials from the Instruqt terminal

In the **Terminal** tab, run:

```bash
source ~/.bashrc
echo "=== Paste these into Cursor ==="
grep -E '^export (KIBANA_URL|ES_URL|ES_API_KEY|WORKSHOP_OTLP_ENDPOINT|WORKSHOP_OTLP_AUTH_HEADER)=' ~/.bashrc
```

You will see output like:

```
export KIBANA_URL='https://otel-demo-a5630c.kb.us-east-1.aws.elastic.cloud'
export ES_URL='https://otel-demo-a5630c.es.us-east-1.aws.elastic.cloud'
export ES_API_KEY='X3JMeTZKa0Jq...'
export WORKSHOP_OTLP_ENDPOINT='https://otel-demo-a5630c.ingest.us-east-1.aws.elastic.cloud'
export WORKSHOP_OTLP_AUTH_HEADER='ApiKey X3JMeTZKa0Jq...'
```

**Select and copy all of those `export` lines.**

### Step 2 — Paste credentials into Cursor's integrated terminal

1. Open **Cursor** on your laptop.
2. Open the integrated terminal (`Ctrl+`` ` `` ` ` or `` ⌘+` ``).
3. **Paste** the `export` lines and press Enter — this sets the environment for the
   current terminal session so Cursor's Claude agent can authenticate to your Kibana.

```bash
# Verify the connection
curl -s -H "Authorization: ApiKey $ES_API_KEY" "$KIBANA_URL/api/status" | jq .status.overall.level
# Should return "available"
```

### Step 3 — Choose a dashboard to rebuild

**Option A — You have access to a real Datadog or Dynatrace environment:**

Take a **full-page screenshot** of any database monitoring dashboard in Datadog/Dynatrace.
Drag it into Cursor's chat window or attach it via the paperclip icon.

**Option B — Use a sample description from this repo:**

The repo includes ready-to-use descriptions at `assets/sample-dashboards/`:

| File | Simulates |
|---|---|
| `datadog-sqlserver-example.md` | Datadog SQL Server Overview dashboard |
| `dynatrace-postgres-example.md` | Dynatrace PostgreSQL Service Overview |
| `datadog-mongodb-example.md` | Datadog MongoDB Cluster Health dashboard |

Open one of those files in Cursor (or copy its contents) to use as your source.

### Step 4 — Ask Claude to build the dashboard

Open Cursor's **Agent** chat panel. Paste or describe the dashboard you want to rebuild,
then use this prompt template (adapt for your specific dashboard):

---

**Prompt for SQL Server (Option A — screenshot attached):**

```
I've attached a screenshot of our current SQL Server monitoring dashboard in Datadog.
Please rebuild it in Elastic Observability Serverless using the kibana-dashboards agent skill.

Use these data sources:
- Index: metrics-sqlserverreceiver.otel.otel-default
- Key fields: sqlserver.user.connection.count, sqlserver.page.buffer_cache.hit_ratio,
  sqlserver.lock.wait_time.avg, sqlserver.deadlock.count, sqlserver.batch_sql_request.count,
  sqlserver.database.io.read_latency, sqlserver.database.io.write_latency,
  sqlserver.database.name, service.name

Match the layout and panels from the screenshot as closely as possible.
Deploy the dashboard to Kibana when done.
```

---

**Prompt for SQL Server (Option B — sample description):**

```
I want to rebuild our Datadog SQL Server dashboard in Elastic. Here is a description
of the current layout:

[paste the contents of datadog-sqlserver-example.md here]

Please use the kibana-dashboards agent skill to recreate this dashboard.

Use these data sources:
- Index: metrics-sqlserverreceiver.otel.otel-default
- Key fields: sqlserver.user.connection.count, sqlserver.page.buffer_cache.hit_ratio,
  sqlserver.lock.wait_time.avg, sqlserver.deadlock.count, sqlserver.batch_sql_request.count,
  sqlserver.database.io.read_latency, sqlserver.database.io.write_latency,
  sqlserver.database.size, sqlserver.database.name, service.name

Deploy the dashboard to Kibana when done.
```

---

**Prompt for PostgreSQL (Dynatrace):**

```
I want to rebuild our Dynatrace PostgreSQL dashboard in Elastic. Here is the layout:

[paste the contents of dynatrace-postgres-example.md here]

Please use the kibana-dashboards agent skill to recreate this dashboard.

Use these data sources:
- Index: metrics-postgresqlreceiver.otel.otel-default
- Key fields: postgresql.backends, postgresql.commits, postgresql.rollbacks,
  postgresql.deadlocks, postgresql.blks_hit, postgresql.blks_read,
  postgresql.db_size, postgresql.tup_inserted, postgresql.tup_updated,
  postgresql.database.name, service.name

Deploy the dashboard to Kibana when done.
```

---

**Prompt for MongoDB (Datadog):**

```
I want to rebuild our Datadog MongoDB dashboard in Elastic. Here is the layout:

[paste the contents of datadog-mongodb-example.md here]

Please use the kibana-dashboards agent skill to recreate this dashboard.

Use these data sources:
- Index: metrics-mongodbatlas.otel.otel-default
- Key fields: mongodb.operation.count, mongodb.operation.type,
  mongodb.connection.count, mongodb.memory.usage, mongodb.memory.virtual,
  mongodb.document.operation.count, mongodb.replication.lag,
  mongodb.database.size, mongodb.database.collection.count,
  mongodb.network.io.receive, mongodb.network.io.transmit,
  service.name, host.name

Deploy the dashboard to Kibana when done.
```

---

**Prompt for IBM Db2:**

```
I want to build an IBM Db2 LUW monitoring dashboard in Elastic.

Use these data sources:
- Index: metrics-db2receiver.otel.otel-default
- Key fields: db2.connection.active, db2.bufferpool.hit_ratio, db2.log.utilization,
  db2.lock.wait_time.avg, db2.deadlock.count, db2.sort.overflow.count,
  db2.tablespace.size, db2.tablespace.used (with db2.tablespace.name attribute),
  service.name, host.name, db2.instance.name

Build panels for: connections over time, buffer pool hit ratio, log utilization,
lock waits, tablespace used vs size, and deadlock / sort overflow trends.
Deploy the dashboard to Kibana when done.
```

---

**Prompt for Oracle:**

```
I want to build an Oracle database monitoring dashboard in Elastic.

Use these data sources:
- Index: metrics-oracledbreceiver.otel.otel-default
- Key fields: oracledb.sessions.current (with session.type attribute: active/inactive),
  oracledb.processes.count, oracledb.transactions, oracledb.pga_memory,
  oracledb.logical_reads, oracledb.physical_reads,
  oracledb.hard_parses, oracledb.parse_calls,
  oracledb.user_commits, oracledb.user_rollbacks, oracledb.enqueue_deadlocks,
  oracledb.tablespace.size, oracledb.tablespace.used (with tablespace_name attribute),
  service.name, host.name

Build panels for: sessions over time, tablespace utilisation (used vs total GB),
physical vs logical reads, hard parse rate, active transactions, PGA memory trend.
Deploy the dashboard to Kibana when done.
```

### Step 5 — Watch Claude build and deploy

Claude will:

1. Read the `kibana-dashboards` skill to understand the Kibana as-code API format
2. Draft a dashboard JSON matching the layout you described
3. POST it to `$KIBANA_URL/api/dashboards` using your `$ES_API_KEY`
4. Return the dashboard URL

The entire process takes **60–120 seconds**.

### Step 6 — Open the new dashboard in Kibana

Open the **Elastic Serverless** tab (first tab). Click **Dashboards** in the left nav.
Your new dashboard appears at the top of the list.

Set the time picker to **Last 2 hours** to see the generated data populate all panels.

If any panel is empty, click **Edit** → inspect the ES|QL query → Claude can fix it
in a follow-up message:

```
Panel "Buffer Cache Hit %" is empty. The query is:
FROM metrics-sqlserverreceiver.otel.otel-default
| STATS avg_cache = AVG(sqlserver.page.buffer_cache.hit_ratio)

Please fix the field name or query syntax.
```

</details>
