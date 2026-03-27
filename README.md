# Database Monitoring — Elastic Serverless

This repo contains the **Instruqt track** and **Kibana dashboard assets** for the
*Elastic Serverless Database Monitoring* workshop, used to demonstrate Elastic's
database monitoring capabilities vs. Datadog and Dynatrace.

## Live resources

| Resource | Link |
|---|---|
| Instruqt track | https://play.instruqt.com/manage/elastic/tracks/serverless-db-monitoring |
| Kibana (demo env) | https://otel-demo-a5630c.kb.us-east-1.aws.elastic.cloud/app/dashboards |
| MySQL DB Monitoring dashboard | https://otel-demo-a5630c.kb.us-east-1.aws.elastic.cloud/app/dashboards#/view/27dcd2f5-23ea-4bfe-a8ba-e6968640c4e0 |
| Workshop assets repo | https://github.com/poulsbopete/dashboard-alert-migration |

---

## Repository structure

```
dbmonitoring/
├── README.md
├── mysql-monitoring-dashboard.json      # Dashboard definition (Kibana as-code format)
├── package.json                         # kibana-dashboards script dependencies
├── scripts/
│   └── kibana-dashboards.js             # Kibana Dashboards as-code API CLI
└── serverless-db-monitoring/            # Instruqt track (pulled via instruqt track pull)
    ├── track.yml
    ├── config.yml
    ├── track_scripts/
    │   ├── setup-es3-api                # Track bootstrap: provision Serverless, start OTel
    │   └── cleanup-es3-api
    ├── 01-lab-01-grafana-to-elastic/    # Lab 1: Grafana → Elastic (20 dashboards)
    ├── 02-lab-02-datadog-dashboards-alerts-to-elastic/  # Lab 2: Datadog → Elastic (10 dashboards + 4 monitors)
    └── 03-lab-03-database-monitoring/  # Lab 3: Database monitoring (MySQL/PG/MSSQL/MongoDB)
```

---

## The Instruqt workshop

**Title:** Elastic Serverless Database Monitoring  
**Slug:** `elastic/serverless-db-monitoring`  
**Use case:** Migrate customers from Grafana and Datadog to Elastic Observability Serverless;
demonstrate database monitoring as a competitive differentiator vs. Datadog DBM and Dynatrace.

### Labs

| Lab | Topic | Check |
|-----|-------|-------|
| Lab 1 | Grafana → Elastic (20 dashboards, CLI or Cursor + Agent Skills) | 20 `*-elastic-draft.json` in `build/elastic-dashboards/` |
| Lab 2 | Datadog dashboards + monitors → Elastic (10 dashboards + 4 alert rules) | 10 dashboard + 4 alert drafts in `build/` |
| Lab 3 | **Database monitoring** — MySQL slow queries, errors, lock contention | `build/db-monitoring/dashboard-id.txt` exists |

### Track architecture

```
Python OTLP emitters (fleet, Datadog-style)
        │
        ▼
Grafana Alloy (:4317 / :4318)
        │  OTLP/HTTP + Authorization
        ▼
Elastic managed OTLP (mOTLP)
        │
        ▼
Observability Serverless project
  logs-*    metrics-*    traces-*
        │
        ▼
Kibana (proxied on :8080 in Instruqt)
```

The sandbox VM (`elastic/es3-api-v2`) provisions a fresh Serverless project on start,
wires nginx → Kibana on port 8080, and launches Alloy + OTLP emitters automatically.

---

## Lab 3 — Database Monitoring

Lab 3 was added to showcase Elastic's ability to replace Datadog DBM and Dynatrace
for database monitoring, using OpenTelemetry as the ingestion standard.

### Data indexed

| Index | Contents |
|---|---|
| `logs-mysql.slowlog.otel-*` | MySQL slow query logs — query time, lock time, rows examined/sent, SQL text, DB name, table, operation |
| `logs-mysql.error.otel-*` | MySQL error and warning events |

### Dashboard: MySQL Database Monitoring

10 panels built with ES|QL queries:

| Row | Panels |
|-----|--------|
| KPIs (row 1) | Total Slow Queries · Avg Query Time · Max Query Time · DB Errors |
| Trends (row 2) | Slow Query Rate Over Time (stacked by DB) · Avg Query Time by Database |
| Analysis (row 3) | Top Tables by Slow Query Count · Query Time vs Lock Time by Database |
| Deep dive (row 4) | Slowest Queries by Table (data table) · MySQL Error Log Trend |

The dashboard definition is in [`mysql-monitoring-dashboard.json`](./mysql-monitoring-dashboard.json).

### Competitive comparison

| Capability | Datadog DBM | Dynatrace | Elastic |
|---|---|---|---|
| Slow query capture | ✓ proprietary | ✓ proprietary | ✓ **OTel standard** |
| Full query text | ✓ | Limited | ✓ |
| Multi-DB (MySQL, PG, MSSQL, Mongo) | ✓ | ✓ | ✓ |
| Custom dashboards | Limited | Limited | **Unlimited (Lens + ES\|QL)** |
| AI-assisted dashboard building | ✗ | ✗ | **✓ Cursor + Agent Skills** |
| Vendor lock-in | ✓ | ✓ | ✗ Open standards |

---

## Publishing the MySQL dashboard

### Prerequisites

```bash
export KIBANA_URL="https://<your-kibana>.kb.<region>.aws.elastic.cloud"
export KIBANA_API_KEY="<your-api-key>"
npm install
```

### Deploy

```bash
node scripts/kibana-dashboards.js dashboard create mysql-monitoring-dashboard.json
```

The script prints the dashboard ID and URL on success.

### Test connection

```bash
node scripts/kibana-dashboards.js test
```

---

## Instruqt CLI operations

```bash
# Pull latest track
instruqt track pull elastic/serverless-db-monitoring

# Validate
instruqt track validate

# Push changes
instruqt track push

# Open in browser
instruqt track open elastic/serverless-db-monitoring
```

---

## Local development

The `scripts/kibana-dashboards.js` CLI wraps the [Kibana Dashboards as-code API](https://www.elastic.co/docs/api/doc/kibana)
(Kibana 9.4+). It is sourced from the
[elastic/agent-skills](https://github.com/elastic/agent-skills) `kibana-dashboards` skill.

```bash
npm install

# List existing dashboards
node scripts/kibana-dashboards.js dashboard list   # (uses lens list / dashboard get)

# Create from file
node scripts/kibana-dashboards.js dashboard create mysql-monitoring-dashboard.json

# Get a dashboard by ID
node scripts/kibana-dashboards.js dashboard get <id>
```
