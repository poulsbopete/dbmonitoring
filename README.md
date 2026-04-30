# Elastic Database Monitoring

**Instruqt** demo: **Elastic Observability Serverless** with synthetic OpenTelemetry data,
positioned against **Datadog Database Monitoring (DBM)** and **Dynatrace** across six
database platforms.

**Try the hands-on sandbox:** [Instruqt invite — Database monitoring](https://play.instruqt.com/elastic/invite/m33cztpvt73h)

---

## Customer Context

| Database | Priority |
|---|---|
| Microsoft SQL Server | Highest |
| PostgreSQL | High |
| MySQL | High |
| MongoDB | Medium |
| Oracle | Medium |
| IBM Db2 | Medium |

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
        ├── metrics-db2receiver.otel.otel-default         ← IBM Db2 LUW metrics
        └── metrics-oracledbreceiver.otel.otel-default    ← Oracle metrics
        │
        ▼
Kibana Dashboards (6 × platform + Datadog-style SQL overview + 3 × Spotlight-style incl. flow/topology,
  deployed on track start)
Alert Rules      (7 × pre-wired rules with AI RCA workflow)
SLOs             (7 × service level objectives, managed via workflow)
```

No Grafana Alloy, no proprietary agent — pure Python + OTLP HTTP.

---

## Repository Structure

```
dbmonitoring/
├── tools/
│   ├── db_otel_generator.py      # Synthetic telemetry for all 6 DB types
│   └── requirements.txt          # requests>=2.31.0
├── scripts/
│   └── import_dashboards.py      # Deploys all dashboards (platform + Spotlight) via Dashboards API (9.4+)
├── alert-rules/
│   └── deploy-alert-rules.py     # Deploys 7 alert rules + RCA/SLO workflows
├── workflows/
│   ├── rca-workflow.yaml         # AI-powered Root Cause Analysis workflow
│   ├── db-slo-workflow.yaml      # Idempotent SLO management workflow (runs every 24h)
│   └── db-recommendations-workflow.yaml  # Agent → index db-monitoring-recommendations (per-DB dashboards)
├── assets/
│   ├── sample-dashboards/        # Datadog/Dynatrace prompt examples + screenshots
│   └── spotlight-otel-gaps.md    # Spotlight vs OpenTelemetry coverage (PaaS, OS, logs)
├── slides/                       # Customer-facing slide deck (React + Vite + Tailwind)
│   └── src/slides/               # 13 slides, deployed to GitHub Pages
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
- **4 instances**: two on-premises, **Azure VM**, **Azure SQL Managed Instance** (synthetic);
  **4 databases** each where applicable
- Standard receiver-style: `sqlserver.user.connection.count`,
  `sqlserver.page.buffer_cache.hit_ratio`, `sqlserver.lock.wait_time.avg`,
  `sqlserver.lock.wait.count`, `sqlserver.deadlock.count`,
  `sqlserver.batch_sql_request.count`, `sqlserver.database.io.read_latency`,
  `sqlserver.database.io.write_latency`, `sqlserver.database.size`
- **Spotlight-style (synthetic)**: `spotlight.health.severity` (per SQL + Windows row),
  `spotlight.flow.edge_load` with `spotlight.flow_from` / `spotlight.flow_to` (optional OTel edges; Flow dashboard top panel uses `sqlserver.user.connection.count` by host for reliable ES|QL),
  `sqlserver.spotlight.*` (sessions, CPU, memory, processes, PLE, procedure cache,
  virtualization overhead, error-log rate, services)
- Resource attributes: `cloud.provider`, `cloud.platform`, `sqlserver.build_version`,
  `host.is_virtual`
- **Storage**: TSDB (live timestamps only, ~2h window)

### IBM Db2 (metrics)
- **2 instances** (`db2-prod-luw-01` production, `db2-dr-luw-02` standby)
- **Tablespaces** (per instance): USERSPACE1, TEMPSPACE1, SYSCATSPACE, WAREHOUSE_TS (prod only)
- Connection and health: `db2.connection.active`, `db2.bufferpool.hit_ratio`, `db2.log.utilization`,
  `db2.lock.wait_time.avg`, `db2.deadlock.count`, `db2.sort.overflow.count`
- Capacity: `db2.tablespace.size`, `db2.tablespace.used` (by `db2.tablespace.name`)
- **Storage**: TSDB (live timestamps only, ~2h window)

### MongoDB (metrics)
- **3 nodes**: **2** on-premises (replica set `rs0`) + **1** Atlas-style primary
  (`mongo-atlas-shard0`, `cloud.provider=aws`)
- `mongodb.operation.count` (by type: insert/query/update/delete/getmore/command),
  `mongodb.connection.count`, `mongodb.memory.usage`, `mongodb.memory.virtual`,
  `mongodb.document.operation.count`, `mongodb.network.io.receive/transmit`,
  `mongodb.replication.lag` (secondary only), `mongodb.database.size/collection.count`
- **Storage**: TSDB (live timestamps only, ~2h window)
- **Spotlight severity grid** (treemap in Kibana): `spotlight.health.severity` with `spotlight.grid_row` =
  `"{host} · MongoDB"`; attributes `mongo.deployment`, `cloud.provider`, `cloud.platform`

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
| 🗄️ IBM Db2 — High Connection Count | `custom_threshold` | avg connections > 350 |
| 🔴 Oracle — High Active Sessions | `custom_threshold` | avg sessions > 250 |

All rules are deployed by `alert-rules/deploy-alert-rules.py` and wired to the AI RCA workflow.

When the RCA workflow opens an **Observability case**, analysts can go further in Kibana by searching across linked Serverless projects. **[Cross-project search](https://www.elastic.co/docs/explore-analyze/cross-project-search)** (Elastic Cloud → your Observability project → **Cross-project search**) lets you link another project—such as a **Serverless Security** project—so Discover, ES\|QL, and investigations can include security signals while you work the case. That is useful when you want to correlate a database alert with **potential security issues** (failed logins, detections, endpoint events) that live in Security rather than Observability.

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
| Db2 Buffer Pool Health | 95% | `db2.bufferpool.hit_ratio >= 0.88` |

The SLO workflow (`db-slo-workflow.yaml`) is idempotent and runs every 24h automatically.

### AI recommendations → Elasticsearch → database dashboards

The workflow **`workflows/db-recommendations-workflow.yaml`** (deployed with the alert script) runs on a **10-minute schedule** (and supports a **manual** run). Each execution calls the **default Elastic AI agent** (Agent Builder; `POST /api/agent_builder/converse` with no `agent_id`) six times—once per engine (MySQL, PostgreSQL, SQL Server, MongoDB, Db2, Oracle)—with an engine-specific improvement prompt, then indexes each markdown answer into **`db-monitoring-recommendations`** with **`database_platform`** set so only the matching dashboard shows that text.

1. Ensure the workflow is **enabled** in Kibana (**Management → Workflows** → **Database Monitoring — AI recommendations**). New lab projects pick it up from `deploy-alert-rules.py`; the first scheduled tick may take up to 10 minutes.
2. Open the **MySQL**, **PostgreSQL**, **SQL Server**, **MongoDB**, **IBM Db2**, or **Oracle** performance dashboard: the bottom **AI recommendations** block is a **Markdown** panel backed by a **library** saved object (`dbmon-ai-rec-<engine>`; the panel’s ``ref_id`` is that same id string). `import_dashboards.py` creates those objects; the **Database Monitoring — AI recommendations** workflow **overwrites their Markdown** after each run, so recommendations update in the UI without re-importing dashboards. If saved-object creation fails during import, the strip falls back to a live **metric** (plain ES|QL text). Deployed dashboards default to **Last 1 minute** (dense OTLP); widen the time picker (e.g. **Last 15 minutes**) if charts look empty. Older rows without **`database_platform`** still match the **Db2** dashboard only.

The track bootstrap **creates the index** with mappings before dashboards deploy. Requires **Elastic Workflows** with Elasticsearch action steps (Serverless preview / Stack 9.3+ per Elastic docs).

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
| **IBM Db2** | ✓ extra cost | ✓ extra cost | ✓ **same price** |
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

# Generate live data for all 6 DB types
python3 tools/db_otel_generator.py \
  --otlp-endpoint "$WORKSHOP_OTLP_ENDPOINT" \
  --otlp-auth "$WORKSHOP_OTLP_AUTH_HEADER" \
  --live

# Deploy all dashboards (10 total)
export KIBANA_URL="https://xxx.kb.us-east-1.aws.elastic.cloud"
export ES_API_KEY="<your-api-key>"
python3 scripts/import_dashboards.py

# Deploy alert rules + RCA and SLO workflows (workflows are upserted by YAML `name`)
python3 alert-rules/deploy-alert-rules.py

# Update only the AI recommendations workflow on an already-running Kibana project
python3 alert-rules/deploy-alert-rules.py deploy-workflow db-recommendations-workflow.yaml
```

---

## Publishing the Instruqt Track

Sandboxes **clone this Git repo** at runtime, but the Instruqt **track page** (title, description, challenges) only updates when you **push the track definition** to Instruqt. After workshop-related changes, do **both**:

1. **`git push`** — so new plays get the latest `import_dashboards.py`, generator, workflows, etc.
2. **`instruqt track push`** — so the Instruqt UI and challenge metadata match the repo.

```bash
# One-time login
instruqt auth login

# From repo root: push current branch + Instruqt track (after committing)
./serverless-db-monitoring/publish-track.sh
```

Or manually:

```bash
git push origin main   # or your branch
cd serverless-db-monitoring
instruqt track push    # no --force unless you intend to overwrite remote track state
```

The track slug is `serverless-db-monitoring` under the `elastic` organization.

Each **Instruqt play** spins up a **temporary** Observability Serverless project and host. That environment is **torn down when the play ends**—Kibana URLs, API keys, dashboard IDs, and data do not persist. This repo and the Instruqt track definition are the durable artifacts.

---

## Live Resources

| Resource | URL |
|---|---|
| **Instruqt invite (play)** | https://play.instruqt.com/elastic/invite/m33cztpvt73h |
| Instruqt track (manage) | https://play.instruqt.com/elastic/tracks/serverless-db-monitoring |
| Slide Deck | https://poulsbopete.github.io/dbmonitoring/ |
| GitHub | https://github.com/poulsbopete/dbmonitoring |
