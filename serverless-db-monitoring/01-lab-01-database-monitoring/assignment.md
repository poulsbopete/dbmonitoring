---
slug: lab-01-database-monitoring
id: lab01dbmonitoring
type: challenge
title: Database Monitoring — MySQL · PostgreSQL · SQL Server · MongoDB
teaser: Explore live database performance data across all four of your database platforms
  in Elastic Observability Serverless—slow queries, connections, lock waits, replication
  lag, and more. No proprietary agents. OpenTelemetry end to end.
notes:
- type: text
  contents: |
    ## Data is loading…

    The track bootstrap is generating **4 days of telemetry** for all four database
    platforms via OpenTelemetry → Elastic managed OTLP:

    ```
    MySQL · PostgreSQL · SQL Server · MongoDB
                │
                │  Python OTLP SDK  (db_otel_generator.py)
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
         Kibana Dashboards
    ```

    Four dashboards have been deployed automatically—one per database platform.
    Data generation continues in the background so charts stay live.
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
    | Data sovereignty | ✗ (Datadog cloud) | ✗ | ✓ **your cluster** |
    | Vendor lock-in | High | High | **None — open standards** |
tabs:
- id: lab01terminal
  title: Terminal
  type: terminal
  hostname: es3-api
- id: lab01kibana
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

Four dashboards are live in Kibana — one per database. Open **Elastic Serverless → Dashboards**
and explore each one. Set the time picker to **Last 7 days**.

---

## MySQL — Slow Query & Error Monitoring

**Dashboard:** `MySQL — Slow Query & Error Monitoring`

What to show:

- **KPIs** — total slow queries, avg/max query time, error count
- **Slow Query Rate** — stacked area by database, shows ecommerce and inventory peak together
- **Top Tables** — which tables are driving the most slow queries
- **Query vs Lock Time** — ecommerce/analytics have significantly higher lock contention
- **Slowest Queries table** — full breakdown: operation, table, avg time, rows examined
- **Error Log Trend** — correlate error spikes with slow query peaks

> **Talking point:** Elastic captures the full slow query text, table, operation, and
> row efficiency — the same data Datadog DBM surfaces, but ingested via OpenTelemetry
> with no proprietary agent.

---

## PostgreSQL — Performance & Health

**Dashboard:** `PostgreSQL — Performance & Health`

What to show:

- **Connections** — primary vs replica, peaks during business hours
- **Database Size** — warehouse is 50× larger than catalog
- **Rows Inserted / Updated / Deleted** — write volume trends
- **Deadlocks** — rare but visible spikes correlating with high load
- **Database Summary table** — side-by-side comparison of all three databases

> **Talking point:** Cache hit ratio, deadlock detection, and tuple throughput are all
> standard PostgreSQL OTel receiver metrics — no custom instrumentation required.

---

## SQL Server — Performance & Health

**Dashboard:** `SQL Server — Performance & Health`  *(most important for this customer)*

What to show:

- **User Connections** — production instance peaks at 400+ during business hours
- **Buffer Cache Hit %** — stays above 96%, dip below 95% is an early warning sign
- **Lock Wait Time** — spikes visible during batch jobs
- **I/O Read vs Write Latency by Database** — SalesDB and ReportingDB have the highest latency
- **Batch Requests** — throughput baseline and growth trend
- **Instance Summary table** — compare prod vs secondary at a glance

> **Talking point:** SQL Server monitoring in Datadog costs extra (Database Monitoring
> add-on). In Elastic it's the same price as any other OTel data. The `sqlserverreceiver`
> provides all standard DMV metrics — no WMI polling, no proprietary agent.

---

## MongoDB — Operations & Health

**Dashboard:** `MongoDB — Operations & Health`

What to show:

- **Operations by Type** — query dominates, insert/update/delete clearly visible
- **Connections** — primary stays consistently higher than secondary
- **Replication Lag** — secondary shows occasional lag spikes under load
- **Memory Usage** — resident vs virtual, tracks linearly with connection count
- **Document Operations** — insert/update/delete rates
- **Database Size** — user_data is the largest collection

> **Talking point:** MongoDB monitoring is a paid add-on in Datadog and limited in
> Dynatrace. Elastic supports it natively via the OTel mongodbatlas receiver — same
> pipeline, same dashboards API.

---

## Build a custom dashboard with Cursor + Agent Skills

**This is the "WOW moment":** Take a screenshot of the customer's existing Datadog or
Dynatrace database dashboard. Open it in Cursor and ask:

> *"Here's a screenshot of our current SQL Server monitoring dashboard in Datadog.
> Can you rebuild it in Elastic using the kibana-dashboards skill and the
> metrics-sqlserverreceiver.otel-* index?"*

Claude will generate and publish a matching Kibana dashboard in under 2 minutes —
using ES|QL queries over the live OTel data already in Elastic.

```bash
# From the VM — copy credentials to Cursor:
cd /root/workshop && source ~/.bashrc
grep -E '^export (KIBANA_URL|ES_URL|ES_API_KEY)=' ~/.bashrc
```

Paste those `export` lines into Cursor's integrated terminal, then let Claude build.

---

## Troubleshooting

If charts look empty, check the data pipeline:

```bash
cd /root/workshop && source ~/.bashrc
# Check generator status
ps aux | grep db_otel_generator
# Restart data generation
nohup python3 /root/workshop/tools/db_otel_generator.py \
  --otlp-endpoint "${WORKSHOP_OTLP_ENDPOINT}" \
  --otlp-auth "${WORKSHOP_OTLP_AUTH_HEADER}" \
  --historical-days 4 --live >> /tmp/db-generator.log 2>&1 &
# Check logs
tail -f /tmp/db-generator.log
```
