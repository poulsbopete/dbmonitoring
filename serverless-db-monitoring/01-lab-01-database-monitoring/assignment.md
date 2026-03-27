---
slug: lab-01-database-monitoring
id: wpfcpdfhckxi
type: challenge
title: Database Monitoring — MySQL · PostgreSQL · SQL Server · MongoDB
teaser: Explore live database performance data across all four of your database platforms
  in Elastic Observability Serverless—slow queries, connections, lock waits, replication
  lag, and more. No proprietary agents. OpenTelemetry end to end.
notes:
- type: text
  contents: |
    ## While you wait… 🧛

    <iframe src="https://poulsbopete.github.io/Vampire-Clone/"
      width="100%" height="520" frameborder="0"
      allow="autoplay" style="border-radius:8px">
    </iframe>

    *Your Elastic environment and 4 days of database telemetry are generating in the background.*
- type: text
  contents: |
    ## Data is loading…

    The track bootstrap is generating **4 days of telemetry** for all four database
    platforms via OpenTelemetry → Elastic managed OTLP:

    ```
    MySQL · PostgreSQL · SQL Server · MongoDB
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
                │
                ▼
         Kibana Dashboards  (4 deployed automatically)
    ```

    No Grafana Alloy. No proprietary agent. Pure OpenTelemetry.
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
    | Custom dashboards | Template-only | Template-only | **Unlimited — Lens + ES\|QL** |
    | AI-assisted dashboard building | ✗ | ✗ | **✓ Cursor + Agent Skills** |
    | Bring your own telemetry (OTel) | Limited | Limited | **Native** |
    | Data sovereignty | ✗ (vendor cloud) | ✗ | ✓ **your cluster** |
    | Vendor lock-in | High | High | **None — open standards** |
tabs:
- id: 1mqitrfzb5hr
  title: Terminal
  type: terminal
  hostname: es3-api
- id: eapiw1vxqwe9
  title: Elastic Serverless
  type: service
  hostname: es3-api
  path: /app/dashboards#/list?_g=(filters:!(),refreshInterval:(pause:!f,value:30000),time:(from:now-7d,to:now))
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
difficulty: ""
timelimit: 0
enhanced_loading: null
---

# Database Monitoring — MySQL · PostgreSQL · SQL Server · MongoDB

## Part 1 — Explore the pre-built dashboards

Four dashboards were deployed automatically when this track started.
Open **Elastic Serverless → Dashboards** and set the time picker to **Last 7 days**.

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

---

### PostgreSQL — Performance & Health

**Dashboard:** `PostgreSQL — Performance & Health`

1. **Active Connections** — primary vs replica, peaks during business hours.
2. **Database Size** — `warehouse` is substantially larger than `catalog` and `auth`.
3. **Rows Inserted / Updated / Deleted** — write volume trends over 7 days.
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

## Part 2 — Build a custom dashboard with Cursor + Elastic Agent Skills

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
- Index: metrics-sqlserverreceiver.otel-default
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
- Index: metrics-sqlserverreceiver.otel-default
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
- Index: metrics-postgresqlreceiver.otel-default
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
- Index: metrics-mongodbatlas.otel-default
- Key fields: mongodb.operation.count, mongodb.operation.type,
  mongodb.connection.count, mongodb.memory.usage, mongodb.memory.virtual,
  mongodb.document.operation.count, mongodb.replication.lag,
  mongodb.database.size, mongodb.database.collection.count,
  mongodb.network.io.receive, mongodb.network.io.transmit,
  service.name, host.name

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

Switch back to the **Elastic Serverless** tab. Click **Dashboards** in the left nav.
Your new dashboard appears at the top of the list.

Set the time picker to **Last 7 days** to see the generated data populate all panels.

If any panel is empty, click **Edit** → inspect the ES|QL query → Claude can fix it
in a follow-up message:

```
Panel "Buffer Cache Hit %" is empty. The query is:
FROM metrics-sqlserverreceiver.otel-default
| STATS avg_cache = AVG(sqlserver.page.buffer_cache.hit_ratio)

Please fix the field name or query syntax.
```

---

## Part 3 — Add an alert

Once the dashboard looks right, add a threshold alert directly from Kibana:

1. In the **SQL Server** dashboard, hover over the **Lock Wait Time** panel → **⋮** → **Create alert**.
2. Set: **Lock wait avg > 50 ms** for **5 minutes**.
3. Optionally configure a Slack or email connector in **Stack Management → Connectors**.

> This takes ~2 minutes. Datadog charges per alert rule per host. In Elastic, alerts
> are unlimited and built on the same query engine as the dashboards.

---

## Troubleshooting

If charts are empty, verify the data pipeline:

```bash
source ~/.bashrc

# Check generator is running
ps aux | grep db_otel_generator | grep -v grep

# Restart if needed
nohup python3 /root/workshop/tools/db_otel_generator.py \
  --otlp-endpoint "${WORKSHOP_OTLP_ENDPOINT}" \
  --otlp-auth "${WORKSHOP_OTLP_AUTH_HEADER}" \
  --historical-days 4 --live \
  >> /tmp/db-monitoring-logs/generator.log 2>&1 &

# Watch live output
tail -f /tmp/db-monitoring-logs/generator.log

# Confirm data is reaching Elastic
curl -s -H "Authorization: ApiKey ${ES_API_KEY}" \
  "${ES_URL}/metrics-sqlserverreceiver.otel-default/_count" | jq .count
```
