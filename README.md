# Elastic Database Monitoring — POC Track

Instruqt workshop demonstrating **Elastic Observability Serverless** as a drop-in
replacement for **Datadog Database Monitoring (DBM)** and **Dynatrace** across five
database platforms.

---

## Customer Context

| Database | Priority |
|---|---|
| Microsoft SQL Server | Highest |
| PostgreSQL | High |
| MySQL | High |
| MongoDB | Medium |
| Oracle | Medium |

Competitors in scope: **Datadog DBM**, **Dynatrace**.

---

## How It Works

```
Python OTLP generator (db_otel_generator.py)
        │
        │  OTLP HTTP  (requests library, no proprietary SDK)
        ▼
Elastic Managed OTLP endpoint
        │
        ├── logs-mysql.slowlog.otel.otel-default         ← slow queries
        ├── logs-mysql.error.otel.otel-default            ← error logs
        ├── metrics-postgresqlreceiver.otel.otel-default  ← PG metrics
        ├── metrics-sqlserverreceiver.otel.otel-default   ← SQL Server metrics
        ├── metrics-mongodbatlas.otel.otel-default        ← MongoDB metrics
        └── metrics-oracledbreceiver.otel.otel-default    ← Oracle metrics
        │
        ▼
Kibana Dashboards (5 × platform dashboards, deployed on track start)
Alert Rules      (6 × pre-wired rules with AI RCA workflow)
SLOs             (6 × service level objectives, managed via workflow)
```

No Grafana Alloy, no proprietary agent — pure Python + OTLP HTTP.

---

## Repository Structure

```
dbmonitoring/
├── tools/
│   ├── db_otel_generator.py      # Synthetic telemetry for all 5 DB types
│   └── requirements.txt          # requests>=2.31.0
├── scripts/
│   └── import_dashboards.py      # Deploys all 5 dashboards via Kibana Saved Objects API
├── alert-rules/
│   └── deploy-alert-rules.py     # Deploys 6 alert rules + RCA/SLO workflows
├── workflows/
│   ├── rca-workflow.yaml         # AI-powered Root Cause Analysis workflow
│   └── db-slo-workflow.yaml      # Idempotent SLO management workflow (runs every 24h)
├── slides/                       # Customer-facing slide deck (React + Vite + Tailwind)
│   └── src/slides/               # 11 slides, deployed to GitHub Pages
└── serverless-db-monitoring/     # Instruqt track
    ├── track.yml
    ├── config.yml
    ├── track_scripts/
    │   ├── setup-es3-api         # Creates Serverless project, starts generator, deploys all resources
    │   └── cleanup-es3-api       # Stops generator, deletes project
    └── 01-lab-01-database-monitoring/
        ├── assignment.md         # Lab content: walk-through + competitive comparison
        ├── setup-es3-api         # (no-op — track_scripts/setup-es3-api does all work)
        ├── check-es3-api         # Validates generator running + dashboards deployed
        └── solve-es3-api         # Restarts generator + re-deploys dashboards
```

---

## Data Generated

### MySQL (logs)
- **4 databases**: ecommerce, inventory, analytics, reporting
- **Slow query logs** (`logs-mysql.slowlog.otel.otel-default`): query_time, lock_time,
  rows_examined, rows_sent, db.name, db.operation, db.sql.table, db.user, db.statement
- **Error logs** (`logs-mysql.error.otel.otel-default`): lock timeouts, connection errors,
  disk warnings — correlated with load spikes
- **Pattern**: business-hours load curve (9am–6pm weekdays = peak)
- **Storage**: LogsDB (accepts historical timestamps)

### PostgreSQL (metrics)
- **2 instances** (primary + replica), **3 databases** each
- `postgresql.backends`, `postgresql.db_size`, `postgresql.commits`, `postgresql.rollbacks`,
  `postgresql.deadlocks`, `postgresql.blks_hit`, `postgresql.blks_read`,
  `postgresql.tup_inserted/updated/deleted/fetched/returned`
- **Storage**: TSDB (live timestamps only, ~2h window)

### SQL Server (metrics) — highest priority
- **2 instances** (production + secondary), **4 databases** each
- `sqlserver.user.connection.count`, `sqlserver.page.buffer_cache.hit_ratio`,
  `sqlserver.lock.wait_time.avg`, `sqlserver.lock.wait.count`, `sqlserver.deadlock.count`,
  `sqlserver.batch_sql_request.count`, `sqlserver.database.io.read_latency`,
  `sqlserver.database.io.write_latency`, `sqlserver.database.size`
- **Storage**: TSDB (live timestamps only, ~2h window)

### MongoDB (metrics)
- **2 instances** (primary + secondary, replica set `rs0`), **4 databases**
- `mongodb.operation.count` (by type: insert/query/update/delete/getmore/command),
  `mongodb.connection.count`, `mongodb.memory.usage`, `mongodb.memory.virtual`,
  `mongodb.document.operation.count`, `mongodb.network.io.receive/transmit`,
  `mongodb.replication.lag` (secondary only), `mongodb.database.size/collection.count`
- **Storage**: TSDB (live timestamps only, ~2h window)

### Oracle (metrics)
- **2 instances** (`oracle-prod-01` production, `oracle-prod-02` standby)
- **7 tablespaces** per primary instance: SYSTEM, USERS, FINANCE, HR, ANALYTICS, TEMP, UNDO
- Session metrics: `oracledb.sessions.current` (by `session.type`: active/inactive),
  `oracledb.processes.count`, `oracledb.transactions`, `oracledb.pga_memory`
- Parse efficiency: `oracledb.hard_parses`, `oracledb.parse_calls`
- I/O: `oracledb.logical_reads`, `oracledb.physical_reads`
- Transactions: `oracledb.user_commits`, `oracledb.user_rollbacks`, `oracledb.enqueue_deadlocks`
- Tablespace capacity: `oracledb.tablespace.size`, `oracledb.tablespace.used` (by `tablespace_name`)
- **Storage**: TSDB (live timestamps only, ~2h window)
- **Reference**: [elastic.co/docs/reference/integrations/oracle](https://www.elastic.co/docs/reference/integrations/oracle)

---

## Alert Rules

| Rule | Type | Threshold |
|---|---|---|
| 🐢 MySQL — Slow Query Spike | `.es-query` | > 10 events / 5m |
| 🔴 MySQL — Error Log Spike | `.es-query` | > 3 events / 5m |
| 🐘 PostgreSQL — High Connection Count | `custom_threshold` | avg backends > 80 |
| 💾 SQL Server — High Active Transactions | `custom_threshold` | avg active txns > 100 |
| 🍃 MongoDB — High Operations Rate | `custom_threshold` | avg ops > 5000 |
| 🔴 Oracle — High Active Sessions | `custom_threshold` | avg sessions > 250 |

All rules are deployed by `alert-rules/deploy-alert-rules.py` and wired to the AI RCA workflow.

---

## SLOs (managed by workflow)

| SLO | Target | Indicator |
|---|---|---|
| MySQL Error-Free Log Rate | 99% | `NOT log.level: Error` |
| MySQL Slow Query Compliance | 85% | `mysql.slowlog.query_time <= 10` |
| PostgreSQL Connection Health | 95% | `postgresql.backends <= 160` |
| SQL Server Lock Wait Health | 95% | `sqlserver.lock.wait_time.avg <= 100` |
| MongoDB Memory Health | 95% | `mongodb.memory.usage <= 2 GB` |
| Oracle Session Health | 95% | `oracledb.sessions.current <= 250` |

The SLO workflow (`db-slo-workflow.yaml`) is idempotent and runs every 24h automatically.

---

## Competitive Comparison

| Capability | Datadog DBM | Dynatrace | **Elastic** |
|---|---|---|---|
| Slow query capture | ✓ proprietary | ✓ OneAgent | ✓ **OpenTelemetry** |
| Full query text | ✓ | Limited | ✓ |
| MySQL | ✓ | ✓ | ✓ |
| PostgreSQL | ✓ | ✓ | ✓ |
| **SQL Server** | ✓ extra cost | ✓ | ✓ **same price** |
| **MongoDB** | ✓ extra cost | Limited | ✓ |
| **Oracle** | ✓ extra cost | ✓ extra cost | ✓ **same price** |
| Custom dashboards | Template-only | Template-only | **Unlimited — Lens + ES\|QL** |
| AI-assisted dashboard building | ✗ | ✗ | ✓ **Cursor + Agent Skills** |
| AI Root Cause Analysis | Limited | Limited | ✓ **built-in workflow** |
| Bring your own telemetry (OTel) | Limited | Limited | **Native** |
| Vendor lock-in | High | High | **None** |

---

## Running Locally

```bash
# Install dependencies
pip install -r tools/requirements.txt

# Point at any Elastic Observability deployment
export WORKSHOP_OTLP_ENDPOINT="https://xxx.ingest.us-east-1.aws.elastic.cloud"
export WORKSHOP_OTLP_AUTH_HEADER="ApiKey <your-api-key>"

# Generate live data for all 5 DB types
python3 tools/db_otel_generator.py \
  --otlp-endpoint "$WORKSHOP_OTLP_ENDPOINT" \
  --otlp-auth "$WORKSHOP_OTLP_AUTH_HEADER" \
  --live

# Deploy all 5 dashboards
export KIBANA_URL="https://xxx.kb.us-east-1.aws.elastic.cloud"
export ES_API_KEY="<your-api-key>"
python3 scripts/import_dashboards.py

# Deploy alert rules + RCA and SLO workflows
python3 alert-rules/deploy-alert-rules.py
```

---

## Publishing the Instruqt Track

```bash
# One-time login
instruqt auth login

# Push track (no --force to preserve sandbox config)
cd serverless-db-monitoring
instruqt track push
```

The track slug is `serverless-db-monitoring` under the `elastic` organization.

---

## Live Resources

| Resource | URL |
|---|---|
| Instruqt Track | https://play.instruqt.com/elastic/tracks/serverless-db-monitoring |
| Slide Deck | https://poulsbopete.github.io/dbmonitoring/ |
| GitHub | https://github.com/poulsbopete/dbmonitoring |
