---
slug: lab-03-database-monitoring
id: aeofkwtjakfd
type: challenge
title: Lab 3 — Database Monitoring (MySQL, PostgreSQL, MS SQL, MongoDB)
teaser: See how Elastic replaces Datadog and Dynatrace for database monitoring—slow
  queries, error rates, lock contention, and query hotspots via OpenTelemetry, with
  AI-assisted dashboard building in seconds.
notes:
- type: text
  contents: |
    ## Database Monitoring on Elastic Serverless

    **What this lab shows:**

    Elastic ingests database telemetry—slow query logs, error events, and performance
    metrics—via **OpenTelemetry** (the same pipeline already running in this track).
    No proprietary agents. No lock-in.

    ```
    MySQL / PostgreSQL / MS SQL / MongoDB
              │
              │  OpenTelemetry (OTLP)
              ▼
        Grafana Alloy (:4317)
              │
              ▼
      Elastic managed OTLP
              │
              ▼
    Observability Serverless
    logs-mysql.slowlog.otel-*
    logs-mysql.error.otel-*
    metrics-*.otel-*
              │
              ▼
         Kibana Dashboards
    ```

    **Key metrics surfaced:**
    - Slow query count, avg/max query time, lock time
    - Rows examined vs rows sent (index efficiency)
    - Top tables and operations generating load
    - ERROR / WARNING trend over time
- type: text
  contents: |
    ## How this compares to Datadog / Dynatrace

    | Capability | Datadog DBM | Dynatrace | **Elastic**  |
    |---|---|---|---|
    | Slow query capture | ✓ proprietary | ✓ proprietary | ✓ **OTel standard** |
    | Full query text | ✓ | Limited | ✓ |
    | Multi-DB (MySQL, PG, MSSQL, Mongo) | ✓ | ✓ | ✓ |
    | Custom dashboards | Limited | Limited | **Unlimited (Lens + ES\|QL)** |
    | AI-assisted dashboard building | ✗ | ✗ | **✓ Cursor + Agent Skills** |
    | Vendor lock-in | ✓ | ✓ | ✗ **Open standards** |
    | Data sovereignty | ✗ | ✗ | ✓ **Your data, your cluster** |

    **The WOW moment:** Take a screenshot of a customer's Datadog or Dynatrace DB dashboard.
    In Cursor, ask Claude to rebuild it for Elastic in minutes using the `kibana-dashboards` Agent Skill.
tabs:
- id: uyc1redcnchy
  title: Terminal
  type: terminal
  hostname: es3-api
- id: 6v681pcqelsj
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

# Lab 3 — Database Monitoring

A pre-built **MySQL Database Monitoring** dashboard is already deployed for you (created
by the lab setup). Open **Elastic Serverless → Dashboards** and look for **"MySQL Database Monitoring"**.

Pick **Path A** (explore the dashboard) or **Path B** (build your own with Cursor + Agent Skills).

---

## Path A — Explore the auto-deployed dashboard

1. Click the **Elastic Serverless** tab above.
2. Navigate to **Dashboards → MySQL Database Monitoring**.
3. Set the time range to **Last 40 days** (the data window for this lab).

The dashboard shows **10 panels** across 4 rows:

| Row | Panels |
|-----|--------|
| KPIs | Total Slow Queries · Avg Query Time · Max Query Time · DB Errors |
| Trends | Slow Query Rate Over Time · Avg Query Time by Database |
| Analysis | Top Tables by Slow Query Count · Query Time vs Lock Time |
| Deep dive | Slowest Queries by Table (data table) · Error Log Trend |

All panels use **ES\|QL** queries over `logs-mysql.slowlog.otel-*` and `logs-mysql.error.otel-*`—
the same indexes populated by the OTLP pipeline running since track bootstrap.

To check the pipeline is live:

```bash
cd /root/workshop
source ~/.bashrc
./scripts/check_workshop_otel_pipeline.sh
```

---

## Path B — Build your own with Cursor + Agent Skills

**The demo story:** A customer shows you their Datadog Database Monitoring dashboard.
You screenshot it, open Cursor, and ask Claude to rebuild it for Elastic in minutes.

### Prerequisites

Clone the workshop repo and open in Cursor (if not already done from Lab 1/2):

```bash
# From the Instruqt VM — copy your credentials:
cd /root/workshop && source ~/.bashrc
grep -E '^export (KIBANA_URL|ES_URL|ES_API_KEY)=' ~/.bashrc
```

Paste those `export` lines into **Cursor's integrated terminal** (not the AI chat).

### Build a custom DB dashboard with the `kibana-dashboards` skill

The **`kibana-dashboards`** Agent Skill is already installed in Cursor. Ask Claude:

> *"I want to build a PostgreSQL monitoring dashboard for Elastic. The data is in
> `logs-postgresql.slowlog.otel-*`. Show me the top slow queries, avg query time trend
> over time, and a table of slowest operations by database name."*

Or paste a screenshot of a competitor's DB dashboard and ask Claude to recreate it.

The skill uses ES\|QL queries and the Kibana Dashboards API to build and publish
the dashboard in one shot—no manual clicking.

### Add a database-specific alert

Use the **`kibana-alerting-rules`** Agent Skill to create an alert when avg query
time exceeds 500ms:

> *"Create a Kibana alert that fires when the average MySQL query time (from
> `logs-mysql.slowlog.otel-*`) exceeds 0.5 seconds over the last 10 minutes."*

---

## Done

**Check** when the **MySQL Database Monitoring** dashboard exists in Kibana.

On the VM, you can verify:

```bash
cd /root/workshop && source ~/.bashrc
cat build/db-monitoring/dashboard-id.txt
```
