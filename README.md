# Elastic Database Monitoring — POC Track

Instruqt workshop demonstrating **Elastic Observability Serverless** as a drop-in
replacement for **Datadog Database Monitoring (DBM)** and **Dynatrace** across four
database platforms.

---

## Customer Context

| Database | Priority |
|---|---|
| Microsoft SQL Server | Highest |
| PostgreSQL | High |
| MySQL | High |
| MongoDB | Medium |

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
        ├── logs-mysql.slowlog.otel-default        ← slow queries
        ├── logs-mysql.error.otel-default          ← error logs
        ├── metrics-postgresqlreceiver.otel-default ← PG metrics
        ├── metrics-sqlserverreceiver.otel-default  ← SQL Server metrics
        └── metrics-mongodbatlas.otel-default       ← MongoDB metrics
        │
        ▼
Kibana Dashboards (4 × platform dashboards, deployed on track start)
```

No Grafana Alloy, no proprietary agent — pure Python + OTLP HTTP.

---

## Repository Structure

```
dbmonitoring/
├── tools/
│   ├── db_otel_generator.py    # Generates synthetic telemetry for all 4 DB types
│   └── requirements.txt        # requests>=2.31.0
├── dashboards/
│   ├── mysql-monitoring.json   # Kibana as-code dashboard — MySQL
│   ├── postgres-monitoring.json # Kibana as-code dashboard — PostgreSQL
│   ├── mssql-monitoring.json   # Kibana as-code dashboard — SQL Server
│   └── mongodb-monitoring.json  # Kibana as-code dashboard — MongoDB
└── serverless-db-monitoring/   # Instruqt track
    ├── track.yml
    ├── config.yml
    ├── track_scripts/
    │   ├── setup-es3-api       # Creates Serverless project, starts generator, deploys dashboards
    │   └── cleanup-es3-api     # Stops generator, deletes project
    └── 01-lab-01-database-monitoring/
        ├── assignment.md       # Lab content: walk-through + competitive comparison
        ├── setup-es3-api       # (no-op — track_scripts/setup-es3-api does all work)
        ├── check-es3-api       # Validates generator running + dashboards deployed
        └── solve-es3-api       # Restarts generator + re-deploys dashboards
```

---

## Data Generated

### MySQL (logs)
- **4 databases**: ecommerce, inventory, analytics, reporting
- **Slow query logs** (`logs-mysql.slowlog.otel-default`): query_time, lock_time,
  rows_examined, rows_sent, db.name, db.operation, db.sql.table, db.user, db.statement
- **Error logs** (`logs-mysql.error.otel-default`): lock timeouts, connection errors,
  disk warnings — correlated with load spikes
- **Pattern**: business-hours load curve (9am–6pm weekdays = peak)

### PostgreSQL (metrics)
- **2 instances** (primary + replica), **3 databases** each
- `postgresql.backends`, `postgresql.db_size`, `postgresql.commits`, `postgresql.rollbacks`,
  `postgresql.deadlocks`, `postgresql.blks_hit`, `postgresql.blks_read`,
  `postgresql.tup_inserted/updated/deleted/fetched/returned`

### SQL Server (metrics) — highest priority
- **2 instances** (production + secondary)
- `sqlserver.user.connection.count`, `sqlserver.page.buffer_cache.hit_ratio`,
  `sqlserver.lock.wait_time.avg`, `sqlserver.lock.wait.count`, `sqlserver.deadlock.count`,
  `sqlserver.batch_sql_request.count`, `sqlserver.database.io.read_latency`,
  `sqlserver.database.io.write_latency`, `sqlserver.database.size`

### MongoDB (metrics)
- **2 instances** (primary + secondary, replica set `rs0`), **4 databases**
- `mongodb.operation.count` (by type: insert/query/update/delete/getmore/command),
  `mongodb.connection.count`, `mongodb.memory.usage`, `mongodb.memory.virtual`,
  `mongodb.document.operation.count`, `mongodb.network.io.receive/transmit`,
  `mongodb.replication.lag` (secondary only), `mongodb.database.size/collection.count`

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
| Custom dashboards | Template-only | Template-only | **Unlimited — Lens + ES\|QL** |
| AI-assisted dashboard building | ✗ | ✗ | ✓ **Cursor + Agent Skills** |
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

# Generate 4 days historical + keep running live
python3 tools/db_otel_generator.py \
  --otlp-endpoint "$WORKSHOP_OTLP_ENDPOINT" \
  --otlp-auth "$WORKSHOP_OTLP_AUTH_HEADER" \
  --historical-days 4 \
  --live
```

---

## Publishing the Instruqt Track

```bash
# One-time login
instruqt auth login

# Push track
cd serverless-db-monitoring
instruqt track push --force
```

The track slug is `serverless-db-monitoring` under the `elastic` organization.

---

## Live Resources

| Resource | URL |
|---|---|
| Instruqt Track | https://play.instruqt.com/elastic/tracks/serverless-db-monitoring |
| GitHub | https://github.com/poulsbopete/dbmonitoring |
