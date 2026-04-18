#!/usr/bin/env python3
"""
Import DB monitoring dashboards into Kibana via the Dashboards API (Kibana 9.4+).

Uses POST /api/dashboards with inline type \"vis\" panels and declarative ES|QL (Kibana 9.4+ schema).
Aligns with the Elastic **kibana-dashboards** agent skill and Dashboard / Visualizations API.

Usage:  python3 scripts/import_dashboards.py
Env:    KIBANA_URL + KIBANA_API_KEY (preferred) or ES_API_KEY (+ optional ES_USERNAME/ES_PASSWORD).
        Optional KIBANA_ELASTIC_API_VERSION (default 2023-10-31) for the Dashboards API version header.

If a dashboard with the same title already exists, it is deleted first (GET /api/dashboards,
then DELETE /api/dashboards/{id}) so re-runs update in place without duplicate titles.
"""
import json, os, sys, uuid, urllib.parse, urllib.request, urllib.error, base64

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
API_KEY = (
    os.environ.get("KIBANA_API_KEY", "")
    or os.environ.get("ES_API_KEY", "")
    or os.environ.get("ELASTICSEARCH_API_KEY", "")
)
ES_PASS = os.environ.get("ES_PASSWORD", "") or os.environ.get("ELASTICSEARCH_PASSWORD", "")
ES_USER = os.environ.get("ES_USERNAME", "admin")

if not KIBANA_URL:
    sys.exit("ERROR: KIBANA_URL not set")
if not API_KEY and not ES_PASS:
    sys.exit("ERROR: KIBANA_API_KEY or ES_API_KEY or ES_PASSWORD not set")

HEADERS = {
    "Authorization": f"ApiKey {API_KEY}" if API_KEY
    else "Basic " + base64.b64encode(f"{ES_USER}:{ES_PASS}".encode()).decode(),
    "kbn-xsrf": "true",
    "x-elastic-internal-origin": "kibana",
    "Content-Type": "application/json",
    # Serverless / recent Kibana rejects "1"; public versioned APIs use a calendar version.
    "Elastic-Api-Version": os.environ.get("KIBANA_ELASTIC_API_VERSION", "2023-10-31"),
    "User-Agent": "elastic-agentic",
}

# ES|QL time buckets that scale with the dashboard time range (kibana-dashboards skill).
TB_AUTO = "BUCKET(@timestamp, 75, ?_tstart, ?_tend)"

# Workflow `db-recommendations-workflow.yaml` writes markdown rows here (see README).
REC_INDEX = "db-monitoring-recommendations"

# Kibana time picker default for every deployed dashboard (hot OTLP window).
DEFAULT_TIME_RANGE = ("now-1m", "now")


def gid():
    return str(uuid.uuid4())


def _request_json(method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    hdrs = {k: v for k, v in HEADERS.items() if k.lower() != "content-type" or body is not None}
    req = urllib.request.Request(f"{KIBANA_URL}{path}", data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            if not raw:
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        sys.exit(f"HTTP {e.code} on {path}: {msg[:500]}")


def post(path, body):
    return _request_json("POST", path, body)


def list_dashboard_ids_by_title():
    """Return {title: id} for dashboards from GET /api/dashboards (Serverless returns full list)."""
    path = "/api/dashboards"
    payload = _request_json("GET", path, None)
    out = {}
    for row in payload.get("dashboards") or []:
        if not isinstance(row, dict):
            continue
        did = row.get("id")
        data = row.get("data") or {}
        title = (data.get("title") or "").strip()
        if did and title:
            out[title] = did
    return out


def delete_dashboard_by_id(dash_id):
    """DELETE /api/dashboards/{id} — ignore 404."""
    qid = urllib.parse.quote(dash_id, safe="")
    hdrs = {k: v for k, v in HEADERS.items() if k.lower() != "content-type"}
    req = urllib.request.Request(f"{KIBANA_URL}/api/dashboards/{qid}", headers=hdrs, method="DELETE")
    try:
        with urllib.request.urlopen(req) as r:
            return 200 <= r.status < 300
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True
        return False


def create_dashboard_api(title, description, panels, time_from=None, time_to="now"):
    """POST /api/dashboards — one request per dashboard, inline vis panels."""
    if time_from is None:
        time_from = DEFAULT_TIME_RANGE[0]
    result = post(
        "/api/dashboards",
        {
            "title": title,
            "description": description,
            "panels": panels,
            "time_range": {"from": time_from, "to": time_to},
        },
    )
    return result["id"]


def vis_panel(panel_id, x, y, w, h, config):
    """Kibana 9.4+ Dashboards API: panels use type \"vis\" with flat chart config (not lens + attributes)."""
    return {
        "type": "vis",
        "id": panel_id,
        "grid": {"x": x, "y": y, "w": w, "h": h},
        "config": config,
    }


def markdown_panel(panel_id, x, y, w, h, content: str):
    """Static markdown strip (Kibana embeddable type DASHBOARD_MARKDOWN)."""
    return {
        "type": "DASHBOARD_MARKDOWN",
        "id": panel_id,
        "grid": {"x": x, "y": y, "w": w, "h": h},
        "config": {"content": content},
    }


def viz_metric(title, esql, column):
    return {
        "type": "metric",
        "title": title,
        "data_source": {"type": "esql", "query": esql},
        "metrics": [{"type": "primary", "column": column, "label": column}],
    }


def viz_xy(title, esql, layer_type, x_col, y_cols, breakdown_col=None):
    temporal = x_col == "bucket" or "BUCKET(" in x_col
    layer = {
        "type": layer_type,
        "data_source": {"type": "esql", "query": esql},
        "x": {"column": x_col, "label": "@timestamp" if temporal else x_col},
        "y": [{"column": c} for c in y_cols],
    }
    if breakdown_col:
        layer["breakdown_by"] = {"column": breakdown_col}
    cfg = {"type": "xy", "title": title, "layers": [layer]}
    if temporal:
        cfg["axis"] = {
            "x": {
                "title": {"visible": False},
                "scale": "temporal",
                "domain": {"type": "fit", "rounding": False},
            },
            "y": {"anchor": "start", "title": {"visible": False}},
        }
    return cfg


def viz_heatmap(title, esql, x_col, y_col, value_col):
    """Heat map (inline vis schema for Kibana 9.4+)."""
    return {
        "type": "heatmap",
        "title": title,
        "data_source": {"type": "esql", "query": esql},
        "x": {"column": x_col},
        "y": {"column": y_col},
        "metric": {"column": value_col},
    }


def viz_gauge(title, esql, column):
    return {
        "type": "gauge",
        "title": title,
        "data_source": {"type": "esql", "query": esql},
        "metric": {"column": column},
    }


def viz_datatable(title, esql, metric_columns, row_columns):
    """ES|QL-backed table (readable multi-line cells vs a single metric tile)."""
    return {
        "type": "data_table",
        "title": title,
        "data_source": {"type": "esql", "query": esql},
        "metrics": [{"column": c} for c in metric_columns],
        "rows": [{"column": c} for c in row_columns],
    }


def viz_treemap(title, esql, metric_column, group_by_columns):
    """Hierarchical partition chart (Quest Spotlight–style topology blocks)."""
    return {
        "type": "treemap",
        "title": title,
        "data_source": {"type": "esql", "query": esql},
        "metrics": [{"column": metric_column}],
        "group_by": [{"column": c} for c in group_by_columns],
    }


def P(box, title, chart_config):
    """One dashboard panel: (x,y,w,h), optional title override, flat vis chart config dict."""
    x, y, w, h = box
    cfg = dict(chart_config)
    if title is not None:
        cfg.setdefault("title", title)
    return vis_panel(gid(), x, y, w, h, cfg)


def P_md(box, markdown: str):
    """Markdown-only panel (no ES|QL)."""
    x, y, w, h = box
    return markdown_panel(gid(), x, y, w, h, markdown)


def _rec_platform_where(platform_key: str, include_legacy_null: bool) -> str:
    """ES|QL WHERE clause: filter recommendations index by workflow field database_platform."""
    if include_legacy_null:
        return f'(database_platform == "{platform_key}" OR database_platform IS NULL)'
    return f'database_platform == "{platform_key}"'


def ai_recommendation_panels(y_row, platform_key: str, include_legacy_null: bool = False):
    """Banner + readable table + run count (metric tiles truncate markdown)."""
    w = _rec_platform_where(platform_key, include_legacy_null)
    q_table = (
        f"FROM {REC_INDEX} | WHERE {w} | SORT @timestamp DESC | LIMIT 1 "
        "| EVAL __row = 1 "
        "| STATS `Run at` = MAX(@timestamp), `Recommendation` = SUBSTRING(TO_STRING(MAX(`recommendation`)), 0, 8000) "
        "BY __row"
    )
    ribbon = (
        "## AI recommendations\n\n"
        "Workflow **Database Monitoring \u2014 AI recommendations** (every **10 min** + manual) writes markdown into "
        f"**{REC_INDEX}** for this engine. If **Recommendation** is empty but **Stored runs** is not, widen the "
        "**time picker** (\u201cLast 1 minute\u201d often excludes the last workflow tick)."
    )
    y0 = y_row
    return [
        P_md((0, y0, 48, 4), ribbon),
        P((0, y0 + 4, 36, 12), "Latest recommendation", viz_datatable(
            "Latest recommendation",
            q_table,
            ["Run at", "Recommendation"],
            ["__row"],
        )),
        P((36, y0 + 4, 12, 12), "Stored recommendation runs", viz_metric(
            "",
            f"FROM {REC_INDEX} | WHERE {w} | STATS `Stored runs` = COUNT(*)",
            "Stored runs")),
    ]


# ---------------------------------------------------------------------------
# Dashboard builders
# ---------------------------------------------------------------------------


def build_mysql():
    print("  Building MySQL dashboard (Dashboards API)...")
    TB = TB_AUTO
    panels = [
        P((0, 0, 12, 5), "Total Slow Queries", viz_metric(
            "", "FROM logs-mysql.slowlog.otel.otel-default | STATS `Total Slow Queries` = COUNT(*)",
            "Total Slow Queries")),
        P((12, 0, 12, 5), "Avg Query Time (s)", viz_metric(
            "", "FROM logs-mysql.slowlog.otel.otel-default | STATS `Avg Query Time (s)` = AVG(`mysql.slowlog.query_time`)",
            "Avg Query Time (s)")),
        P((24, 0, 12, 5), "Max Query Time (s)", viz_metric(
            "", "FROM logs-mysql.slowlog.otel.otel-default | STATS `Max Query Time (s)` = MAX(`mysql.slowlog.query_time`)",
            "Max Query Time (s)")),
        P((36, 0, 12, 5), "DB Errors", viz_metric(
            "", "FROM logs-mysql.error.otel.otel-default | STATS `DB Errors` = COUNT(*)", "DB Errors")),
        P((0, 5, 24, 11), "Slow Query Rate by Database", viz_xy(
            "Slow Query Rate by Database",
            f"FROM logs-mysql.slowlog.otel.otel-default | STATS count = COUNT(*) BY bucket = {TB}, `db.name`",
            "area_stacked", "bucket", ["count"], "db.name")),
        P((24, 5, 24, 11), "Avg Query Time by Database (s)", viz_xy(
            "Avg Query Time by Database (s)",
            f"FROM logs-mysql.slowlog.otel.otel-default | STATS avg_time = AVG(`mysql.slowlog.query_time`) BY bucket = {TB}, `db.name`",
            "line", "bucket", ["avg_time"], "db.name")),
        P((0, 16, 24, 11), "Top Tables by Slow Query Count", viz_xy(
            "Top Tables by Slow Query Count",
            "FROM logs-mysql.slowlog.otel.otel-default | STATS count = COUNT(*) BY `db.sql.table` | SORT count DESC | LIMIT 15",
            "bar_horizontal", "db.sql.table", ["count"])),
        P((24, 16, 24, 11), "Avg Query vs Lock Time by Database", viz_xy(
            "Avg Query vs Lock Time by Database",
            "FROM logs-mysql.slowlog.otel.otel-default | STATS avg_query = AVG(`mysql.slowlog.query_time`), avg_lock = AVG(`mysql.slowlog.lock_time`) BY `db.name`",
            "bar", "db.name", ["avg_query", "avg_lock"])),
        P((0, 27, 48, 11), "Error Log Trend", viz_xy(
            "Error Log Trend",
            f"FROM logs-mysql.error.otel.otel-default | STATS count = COUNT(*) BY bucket = {TB}, `log.level`",
            "bar_stacked", "bucket", ["count"], "log.level")),
        *ai_recommendation_panels(38, "mysql"),
    ]
    return create_dashboard_api(
        "MySQL \u2014 Slow Query & Error Monitoring",
        "Slow queries, lock contention, error trends, top tables, and AI workflow output (index "
        f"{REC_INDEX}) via OpenTelemetry",
        panels,
    )


def build_postgres():
    print("  Building PostgreSQL dashboard (Dashboards API)...")
    TB = TB_AUTO
    panels = [
        P((0, 0, 12, 5), "Active Connections", viz_metric(
            "", "FROM metrics-postgresqlreceiver.otel.otel-default | STATS `Active Connections` = MAX(`postgresql.backends`)",
            "Active Connections")),
        P((12, 0, 12, 5), "Total Deadlocks", viz_metric(
            "", "FROM metrics-postgresqlreceiver.otel.otel-default | EVAL _dl = TO_DOUBLE(`postgresql.deadlocks`) | STATS `Total Deadlocks` = MAX(_dl)",
            "Total Deadlocks")),
        P((24, 0, 12, 5), "Max DB Size", viz_metric(
            "", "FROM metrics-postgresqlreceiver.otel.otel-default | STATS `Max DB Size` = MAX(`postgresql.db_size`)",
            "Max DB Size")),
        P((36, 0, 12, 5), "Connection Limit", viz_metric(
            "", "FROM metrics-postgresqlreceiver.otel.otel-default | STATS `Connection Limit` = MAX(`postgresql.connection.max`)",
            "Connection Limit")),
        P((0, 5, 24, 11), "Active Connections Over Time", viz_xy(
            "Active Connections Over Time",
            f"FROM metrics-postgresqlreceiver.otel.otel-default | STATS backends = AVG(`postgresql.backends`) BY bucket = {TB}, `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
            "area_stacked", "bucket", ["backends"], "postgresql.database.name")),
        P((24, 5, 24, 11), "Database Size", viz_xy(
            "Database Size by Database",
            "FROM metrics-postgresqlreceiver.otel.otel-default | STATS db_size = MAX(`postgresql.db_size`) BY `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL | SORT db_size DESC | LIMIT 10",
            "bar_horizontal", "postgresql.database.name", ["db_size"])),
        P((0, 16, 24, 11), "Deadlocks Over Time", viz_xy(
            "Deadlocks Over Time by Database",
            f"FROM metrics-postgresqlreceiver.otel.otel-default | EVAL _dl = TO_DOUBLE(`postgresql.deadlocks`) | STATS deadlocks = MAX(_dl) BY bucket = {TB}, `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
            "bar_stacked", "bucket", ["deadlocks"], "postgresql.database.name")),
        P((24, 16, 24, 11), "Row Operations", viz_xy(
            "Rows Inserted / Updated / Deleted",
            f"FROM metrics-postgresqlreceiver.otel.otel-default | EVAL _ins = TO_DOUBLE(`postgresql.tup_inserted`), _upd = TO_DOUBLE(`postgresql.tup_updated`), _del = TO_DOUBLE(`postgresql.tup_deleted`) | STATS inserted = MAX(_ins), updated = MAX(_upd), deleted = MAX(_del) BY bucket = {TB}",
            "line", "bucket", ["inserted", "updated", "deleted"])),
        *ai_recommendation_panels(27, "postgresql"),
    ]
    return create_dashboard_api(
        "PostgreSQL \u2014 Performance & Health",
        "Connections, deadlocks, database size, row operations, and AI workflow output (index "
        f"{REC_INDEX}) via OpenTelemetry",
        panels,
    )


def build_mssql():
    print("  Building SQL Server dashboard (Dashboards API)...")
    TB = TB_AUTO
    panels = [
        P((0, 0, 12, 5), "User Connections", viz_metric(
            "", "FROM metrics-sqlserverreceiver.otel.otel-default | STATS `User Connections` = MAX(`sqlserver.user.connection.count`)",
            "User Connections")),
        P((12, 0, 12, 5), "Buffer Cache Hit %", viz_metric(
            "", "FROM metrics-sqlserverreceiver.otel.otel-default | STATS `Buffer Cache Hit %` = AVG(`sqlserver.page.buffer_cache.hit_ratio`)",
            "Buffer Cache Hit %")),
        P((24, 0, 12, 5), "Avg Lock Wait (ms)", viz_metric(
            "", "FROM metrics-sqlserverreceiver.otel.otel-default | STATS `Avg Lock Wait (ms)` = AVG(`sqlserver.lock.wait_time.avg`)",
            "Avg Lock Wait (ms)")),
        P((36, 0, 12, 5), "Total Deadlocks", viz_metric(
            "", "FROM metrics-sqlserverreceiver.otel.otel-default | EVAL _dl = TO_DOUBLE(`sqlserver.deadlock.count`) | STATS `Total Deadlocks` = MAX(_dl)",
            "Total Deadlocks")),
        P((0, 5, 24, 11), "Connections Over Time", viz_xy(
            "User Connections Over Time",
            f"FROM metrics-sqlserverreceiver.otel.otel-default | STATS connections = AVG(`sqlserver.user.connection.count`) BY bucket = {TB}, `service.name`",
            "area", "bucket", ["connections"], "service.name")),
        P((24, 5, 24, 11), "Lock Wait Time Over Time", viz_xy(
            "Lock Wait Time (ms) Over Time",
            f"FROM metrics-sqlserverreceiver.otel.otel-default | STATS lock_wait = AVG(`sqlserver.lock.wait_time.avg`) BY bucket = {TB}, `service.name`",
            "line", "bucket", ["lock_wait"], "service.name")),
        P((0, 16, 24, 11), "I/O Latency by Database", viz_xy(
            "I/O Read vs Write Latency by Database",
            "FROM metrics-sqlserverreceiver.otel.otel-default | STATS read_lat = AVG(`sqlserver.database.io.read_latency`), write_lat = AVG(`sqlserver.database.io.write_latency`) BY `sqlserver.database.name` | WHERE `sqlserver.database.name` IS NOT NULL | SORT read_lat DESC | LIMIT 10",
            "bar", "sqlserver.database.name", ["read_lat", "write_lat"])),
        P((24, 16, 24, 11), "Batch Requests Over Time", viz_xy(
            "Batch Requests Over Time",
            f"FROM metrics-sqlserverreceiver.otel.otel-default | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) | STATS batches = MAX(_b) BY bucket = {TB}, `service.name`",
            "line", "bucket", ["batches"], "service.name")),
        *ai_recommendation_panels(27, "sqlserver"),
    ]
    return create_dashboard_api(
        "SQL Server \u2014 Performance & Health",
        "Connections, lock waits, batch requests, buffer cache, I/O latency, and AI workflow output (index "
        f"{REC_INDEX}) via OpenTelemetry",
        panels,
    )


def build_mssql_overview():
    print("  Building SQL Server Overview / Datadog-style dashboard (Dashboards API)...")
    IDX = "metrics-sqlserverreceiver.otel.otel-default"
    TB = TB_AUTO
    q_inst_conns = (
        f"FROM {IDX} | STATS `Max Connections` = MAX(`sqlserver.user.connection.count`) "
        "BY `Instance` = `service.instance.id` | SORT `Max Connections` DESC | LIMIT 20"
    )
    q_inst_cache = (
        f"FROM {IDX} | STATS `Buffer Cache %` = ROUND(AVG(`sqlserver.page.buffer_cache.hit_ratio`), 1) "
        "BY `Instance` = `service.instance.id` | WHERE `Instance` IS NOT NULL | SORT `Instance`"
    )
    panels = [
        P((0, 0, 12, 5), "Batch Requests/sec", viz_metric(
            "", f"FROM {IDX} | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) | STATS `Batch Requests/sec` = MAX(_b)",
            "Batch Requests/sec")),
        P((12, 0, 12, 5), "User Connections", viz_metric(
            "", f"FROM {IDX} | STATS `User Connections` = MAX(`sqlserver.user.connection.count`)", "User Connections")),
        P((24, 0, 12, 5), "Buffer Cache Hit %", viz_metric(
            "", f"FROM {IDX} | STATS `Buffer Cache Hit %` = ROUND(AVG(`sqlserver.page.buffer_cache.hit_ratio`), 1)",
            "Buffer Cache Hit %")),
        P((36, 0, 12, 5), "Deadlocks", viz_metric(
            "", f"FROM {IDX} | EVAL _d = TO_DOUBLE(`sqlserver.deadlock.count`) | STATS `Deadlocks` = MAX(_d)", "Deadlocks")),
        P((0, 5, 24, 11), "User Connections Over Time", viz_xy(
            "User Connections Over Time",
            f"FROM {IDX} | STATS conns = MAX(`sqlserver.user.connection.count`) BY bucket = {TB}, `service.instance.id`",
            "area_stacked", "bucket", ["conns"], "service.instance.id")),
        P((24, 5, 24, 11), "Batch Requests Over Time", viz_xy(
            "Batch Requests Over Time",
            f"FROM {IDX} | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) | STATS batch = MAX(_b) BY bucket = {TB}, `service.instance.id`",
            "line", "bucket", ["batch"], "service.instance.id")),
        P((0, 16, 24, 11), "Lock Wait Time (ms)", viz_xy(
            "Lock Wait Time (ms) Over Time",
            f"FROM {IDX} | STATS lock_ms = AVG(`sqlserver.lock.wait_time.avg`) BY bucket = {TB}, `service.instance.id`",
            "line", "bucket", ["lock_ms"], "service.instance.id")),
        P((24, 16, 24, 11), "Read vs Write I/O Latency", viz_xy(
            "Read vs Write I/O Latency (ms)",
            f"FROM {IDX} | STATS read_ms = AVG(`sqlserver.database.io.read_latency`), write_ms = AVG(`sqlserver.database.io.write_latency`) BY bucket = {TB}",
            "line", "bucket", ["read_ms", "write_ms"])),
        # Inline datatable is rejected by Serverless Dashboards API schema; use bar charts for per-instance KPIs.
        P((0, 27, 24, 10), "Instances by max connections", viz_xy(
            "Top instances — user connections (max)",
            q_inst_conns,
            "bar_horizontal", "Instance", ["Max Connections"])),
        P((24, 27, 24, 10), "Buffer cache hit % by instance", viz_xy(
            "Buffer cache hit % by instance",
            q_inst_cache,
            "bar_horizontal", "Instance", ["Buffer Cache %"])),
    ]
    return create_dashboard_api(
        "SQL Server \u2014 Overview (Datadog Equivalent)",
        "Mirrors the Datadog SQL Server Overview: batch requests, user connections, buffer cache, lock waits, I/O latency, and per-instance bar summaries (tables not supported inline on Serverless).",
        panels,
    )


def build_mongodb():
    print("  Building MongoDB dashboard (Dashboards API)...")
    TB = TB_AUTO
    panels = [
        P((0, 0, 12, 5), "Active Connections", viz_metric(
            "", "FROM metrics-mongodbatlas.otel.otel-default | STATS `Active Connections` = MAX(`mongodb.connection.count`)",
            "Active Connections")),
        P((12, 0, 12, 5), "Memory Usage (GB)", viz_metric(
            "", "FROM metrics-mongodbatlas.otel.otel-default | EVAL _mem_gb = `mongodb.memory.usage` / 1073741824.0 | STATS `Memory Usage (GB)` = ROUND(MAX(_mem_gb), 2)",
            "Memory Usage (GB)")),
        P((24, 0, 12, 5), "Total Operations", viz_metric(
            "", "FROM metrics-mongodbatlas.otel.otel-default | EVAL _ops = TO_DOUBLE(`mongodb.operation.count`) | STATS `Total Operations` = MAX(_ops)",
            "Total Operations")),
        P((36, 0, 12, 5), "Replication Lag (s)", viz_metric(
            "", "FROM metrics-mongodbatlas.otel.otel-default | STATS `Replication Lag (s)` = AVG(`mongodb.replication.lag`)",
            "Replication Lag (s)")),
        P((0, 5, 24, 11), "Operations Over Time", viz_xy(
            "Operations Over Time by Type",
            f"FROM metrics-mongodbatlas.otel.otel-default | EVAL _ops = TO_DOUBLE(`mongodb.operation.count`) | STATS ops = MAX(_ops) BY bucket = {TB}, `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
            "area_stacked", "bucket", ["ops"], "mongodb.operation.type")),
        P((24, 5, 24, 11), "Connections by Instance", viz_xy(
            "Connections by Instance",
            f"FROM metrics-mongodbatlas.otel.otel-default | STATS conns = AVG(`mongodb.connection.count`) BY bucket = {TB}, `service.name`",
            "line", "bucket", ["conns"], "service.name")),
        P((0, 16, 24, 11), "Memory Trend", viz_xy(
            "Memory: Resident vs Virtual (GB)",
            f"FROM metrics-mongodbatlas.otel.otel-default | EVAL _res = `mongodb.memory.usage` / 1073741824.0, _virt = `mongodb.memory.virtual` / 1073741824.0 | STATS resident = ROUND(AVG(_res), 2), virtual = ROUND(AVG(_virt), 2) BY bucket = {TB}",
            "area", "bucket", ["resident", "virtual"])),
        P((24, 16, 24, 11), "Document Operations", viz_xy(
            "Document Operations Over Time",
            f"FROM metrics-mongodbatlas.otel.otel-default | EVAL _docs = TO_DOUBLE(`mongodb.document.operation.count`) | STATS docs = MAX(_docs) BY bucket = {TB}, `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
            "line", "bucket", ["docs"], "mongodb.operation.type")),
        *ai_recommendation_panels(27, "mongodb"),
    ]
    return create_dashboard_api(
        "MongoDB \u2014 Operations & Health",
        "Operation throughput, connections, memory, replication lag, document stats, and AI workflow output (index "
        f"{REC_INDEX}) via OpenTelemetry",
        panels,
    )


_SPOTLIGHT_FROM = (
    "metrics-sqlserverreceiver.otel.otel-default, metrics-mongodbatlas.otel.otel-default"
)


def build_spotlight_heatmap():
    print("  Building Spotlight severity grid dashboard (Dashboards API)...")
    TB = TB_AUTO
    q_hm = (
        f"FROM {_SPOTLIGHT_FROM} | WHERE `spotlight.grid_row` IS NOT NULL "
        f"| STATS sev = MAX(`spotlight.health.severity`) BY bucket = {TB}, `spotlight.grid_row`"
    )
    q_line = (
        f"FROM {_SPOTLIGHT_FROM} | WHERE `spotlight.grid_row` IS NOT NULL "
        f"| STATS `Severity` = MAX(`spotlight.health.severity`) BY bucket = {TB}, `spotlight.grid_row`"
    )
    q_bar = (
        f"FROM {_SPOTLIGHT_FROM} | WHERE `spotlight.grid_row` IS NOT NULL "
        "| STATS `Avg severity` = AVG(`spotlight.health.severity`) BY `spotlight.grid_row` | SORT `Avg severity` DESC"
    )
    q_peak = (
        f"FROM {_SPOTLIGHT_FROM} | WHERE `spotlight.grid_row` IS NOT NULL "
        "| STATS `Peak` = MAX(`spotlight.health.severity`), `Samples` = COUNT(*) "
        "BY `spotlight.grid_row`, `cloud.platform`, `spotlight.entity_type` | SORT `Peak` DESC | LIMIT 20 "
        "| EVAL `Row` = CONCAT(`spotlight.grid_row`, \" | \", TO_STRING(COALESCE(`cloud.platform`, \"-\")), "
        "\" | \", COALESCE(`spotlight.entity_type`, \"-\")) | KEEP `Row`, `Peak`, `Samples`"
    )
    panels = [
        # Inline type "heatmap" is rejected by Serverless POST /api/dashboards; treemap is supported and
        # encodes the same dimensions (time bucket × grid_row) with area/color from severity.
        P((0, 0, 36, 14), "Severity grid (time × row)", viz_treemap(
            "Severity by time bucket and instance row (treemap — closest supported 2D grid on this API)",
            q_hm,
            "sev",
            ["bucket", "spotlight.grid_row"],
        )),
        P((36, 0, 12, 14), "Severity lines", viz_xy(
            "Severity trend by row", q_line, "line", "bucket", ["Severity"], "spotlight.grid_row")),
        P((0, 14, 24, 12), "Avg severity ranking", viz_xy(
            "Average severity by row", q_bar, "bar_horizontal", "spotlight.grid_row", ["Avg severity"])),
        P((24, 14, 24, 12), "Peak severity + cloud + entity", viz_xy(
            "Peak severity breakdown", q_peak, "bar_horizontal", "Row", ["Peak", "Samples"])),
    ]
    return create_dashboard_api(
        "Spotlight \u2014 Severity grid (SQL Server, Windows, MongoDB)",
        "Primary panel: treemap (time bucket × spotlight.grid_row, metric = max severity). "
        "True Lens heat maps are not available via inline Dashboard API on Serverless; scale 0–3 = informational → critical.",
        panels,
    )


def build_spotlight_flow():
    """Flow-style views inspired by Quest Spotlight (bars + treemap; not a true Sankey)."""
    print("  Building Spotlight flow / topology dashboard (Dashboards API)...")
    IDX = "metrics-sqlserverreceiver.otel.otel-default"
    TB = TB_AUTO
    # Top panel: avoid OTel attribute keys that may not map to ES|QL columns on all stacks
    # (e.g. legacy `spotlight.flow.from`). Uses core SQL Server metrics every instance has.
    q_flow = (
        f"FROM {IDX} | WHERE `host.name` IS NOT NULL "
        "| STATS `Load` = AVG(`sqlserver.user.connection.count`) BY `host.name` "
        "| EVAL `Flow` = CONCAT(\"Client connections \u2192 \", `host.name`) "
        "| SORT `Load` DESC"
    )
    q_tree = (
        f"FROM {IDX} | WHERE `sqlserver.database.name` IS NOT NULL "
        "| STATS `Database GB` = ROUND(MAX(`sqlserver.database.size`) / 1073741824.0, 3) "
        "BY `host.name`, `sqlserver.database.name`"
    )
    q_sessions = (
        f"FROM {IDX} | STATS sess = AVG(`sqlserver.spotlight.session.active.count`), "
        f"tx = AVG(`sqlserver.transaction.active.count`) BY bucket = {TB}"
    )
    panels = [
        P((0, 0, 48, 12), "Connection path by host", viz_xy(
            "Client connection load \u2192 SQL host (bar length \u2248 avg user connections)",
            q_flow, "bar_horizontal", "Flow", ["Load"])),
        P((0, 12, 48, 14), "Database footprint by host (treemap)", viz_treemap(
            "Host \u2192 database size (GB)",
            q_tree, "Database GB", ["host.name", "sqlserver.database.name"])),
        P((0, 26, 48, 10), "Sessions vs transactions over time", viz_xy(
            "Session pressure through the stack (time-aligned)",
            q_sessions, "area", "bucket", ["sess", "tx"])),
    ]
    return create_dashboard_api(
        "Spotlight \u2014 Flow & topology (SQL Server, synthetic)",
        "Top panel ranks hosts by avg user connections (always-available metrics). "
        "Treemap = host \u2192 database size. Optional OTel edges spotlight.flow_from / spotlight.flow_to exist in db_otel_generator "
        "if your index maps them for ES|QL. True Sankey = Vega (kibana-vega skill).",
        panels,
    )


def build_spotlight_sql_overview():
    print("  Building Spotlight SQL Server overview dashboard (Dashboards API)...")
    IDX = "metrics-sqlserverreceiver.otel.otel-default"
    H = 'host.name == "mssql-prod-01"'

    def w(q):
        return q.replace("__FILTER__", H)

    sess_bar_q = w(
        f"FROM {IDX} | WHERE __FILTER__ | STATS pct = MAX(`sqlserver.spotlight.session.active_pct`) "
        "| EVAL `Utilisation` = \"Active % of max\""
    )
    panels = [
        P((0, 0, 8, 5), "Response time (ms)", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Response time (ms)` = AVG(`sqlserver.spotlight.session.response_time_ms`)"),
            "Response time (ms)")),
        P((8, 0, 8, 5), "Active sessions", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Active sessions` = MAX(`sqlserver.spotlight.session.active.count`)"),
            "Active sessions")),
        P((16, 0, 8, 5), "Max sessions", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Max sessions` = MAX(`sqlserver.spotlight.session.max.count`)"),
            "Max sessions")),
        P((24, 0, 8, 5), "Computers", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Computers` = MAX(`sqlserver.spotlight.computers.count`)"),
            "Computers")),
        P((32, 0, 16, 5), "Active sessions %", viz_xy(
            "Active sessions % of max", sess_bar_q, "bar_horizontal", "Utilisation", ["pct"])),
        P((0, 5, 12, 8), "Performance health (gauge)", viz_gauge(
            "Performance health rating", w(
                f"FROM {IDX} | WHERE __FILTER__ | STATS `Health rating` = MAX(`sqlserver.spotlight.performance_health.rating`)"),
            "Health rating")),
        # Datatable (incl. empty rows) is rejected on Serverless; use metric tiles for the wide summary row.
        P((12, 5, 6, 4), "Rating", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Rating` = ROUND(MAX(`sqlserver.spotlight.performance_health.rating`), 1)"),
            "Rating")),
        P((18, 5, 6, 4), "SQL build", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `SQL build` = MAX(`sqlserver.build_version`)"),
            "SQL build")),
        P((24, 5, 6, 4), "Host", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Host` = MAX(`host.name`)"),
            "Host")),
        P((30, 5, 6, 4), "Cloud", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Cloud` = MAX(`cloud.platform`)"),
            "Cloud")),
        P((36, 5, 6, 4), "Custom status", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Custom status` = MAX(`sqlserver.spotlight.custom_status`)"),
            "Custom status")),
        P((42, 5, 6, 4), "Virtual host", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Virtual host` = MAX(`host.is_virtual`)"),
            "Virtual host")),
        P((0, 13, 8, 5), "Processes total", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Total` = MAX(`sqlserver.spotlight.processes.total`)"), "Total")),
        P((8, 13, 8, 5), "System procs", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `System` = MAX(`sqlserver.spotlight.processes.system`)"), "System")),
        P((16, 13, 8, 5), "User procs", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `User` = MAX(`sqlserver.spotlight.processes.user`)"), "User")),
        P((24, 13, 8, 5), "Blocked", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Blocked` = MAX(`sqlserver.spotlight.processes.blocked`)"), "Blocked")),
        P((32, 13, 16, 5), "Batch requests (counter)", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) "
            "| STATS `Batch requests` = MAX(_b)"), "Batch requests")),
        P((0, 18, 12, 8), "Virtualization overhead", viz_gauge(
            "Virtualization overhead %", w(
                f"FROM {IDX} | WHERE __FILTER__ | STATS `Overhead %` = AVG(`sqlserver.spotlight.virtualization.overhead_pct`)"),
            "Overhead %")),
        P((12, 18, 12, 8), "CPU usage", viz_gauge(
            "CPU usage %", w(
                f"FROM {IDX} | WHERE __FILTER__ | STATS `CPU %` = MAX(`sqlserver.spotlight.cpu.usage`)"), "CPU %")),
        P((24, 18, 24, 8), "Buffer cache hit %", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Hit %` = AVG(`sqlserver.page.buffer_cache.hit_ratio`)"), "Hit %")),
        P((0, 26, 12, 5), "Memory total", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Total bytes` = MAX(`sqlserver.spotlight.memory.server.total.bytes`)"),
            "Total bytes")),
        P((12, 26, 12, 5), "Buffer cache size", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Buffer cache` = MAX(`sqlserver.spotlight.memory.buffer_cache.bytes`)"),
            "Buffer cache")),
        P((24, 26, 12, 5), "Page life expectancy", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `PLE (s)` = MAX(`sqlserver.spotlight.memory.page_life_expectancy.seconds`)"),
            "PLE (s)")),
        P((36, 26, 12, 5), "Procedure cache", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Proc cache` = MAX(`sqlserver.spotlight.memory.procedure_cache.bytes`)"),
            "Proc cache")),
        P((0, 31, 12, 5), "Error log rate", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Error log/min` = AVG(`sqlserver.spotlight.background.errorlog.events_per_min`)"),
            "Error log/min")),
        P((12, 31, 12, 5), "SQL services running", viz_metric("", w(
            f"FROM {IDX} | WHERE __FILTER__ | STATS `Services` = MAX(`sqlserver.spotlight.services.running`)"),
            "Services")),
    ]
    return create_dashboard_api(
        "Spotlight \u2014 SQL Server Overview (synthetic)",
        "Widgets aligned to Quest Spotlight SQL Server Overview using sqlserver.spotlight.* metrics; filtered to host mssql-prod-01.",
        panels,
    )


def build_db2():
    print("  Building IBM Db2 dashboard (Dashboards API)...")
    IDX = "metrics-db2receiver.otel.otel-default"
    TB = TB_AUTO
    panels = [
        P((0, 0, 12, 5), "Active connections", viz_metric(
            "", f"FROM {IDX} | STATS `Active connections` = MAX(`db2.connection.active`)",
            "Active connections")),
        P((12, 0, 12, 5), "Buffer pool hit ratio", viz_metric(
            "", f"FROM {IDX} | STATS `Hit ratio` = ROUND(AVG(`db2.bufferpool.hit_ratio`), 4)",
            "Hit ratio")),
        P((24, 0, 12, 5), "Log utilization %", viz_metric(
            "", f"FROM {IDX} | STATS `Log util %` = ROUND(AVG(`db2.log.utilization`), 1)",
            "Log util %")),
        P((36, 0, 12, 5), "Avg lock wait (ms)", viz_metric(
            "", f"FROM {IDX} | STATS `Lock wait ms` = ROUND(AVG(`db2.lock.wait_time.avg`), 2)",
            "Lock wait ms")),
        P((0, 5, 24, 11), "Connections over time", viz_xy(
            "Active connections by instance",
            f"FROM {IDX} | STATS conns = AVG(`db2.connection.active`) BY bucket = {TB}, `service.name`",
            "area_stacked", "bucket", ["conns"], "service.name")),
        P((24, 5, 24, 11), "Buffer pool hit ratio trend", viz_xy(
            "Buffer pool hit ratio (0–1)",
            f"FROM {IDX} | STATS hit = AVG(`db2.bufferpool.hit_ratio`) BY bucket = {TB}, `service.name`",
            "line", "bucket", ["hit"], "service.name")),
        P((0, 16, 24, 11), "Tablespace used (GB)", viz_xy(
            "Tablespace footprint",
            f"FROM {IDX} | WHERE `db2.tablespace.used` IS NOT NULL "
            "| STATS used_gb = ROUND(MAX(`db2.tablespace.used`) / 1073741824.0, 2), "
            "total_gb = ROUND(MAX(`db2.tablespace.size`) / 1073741824.0, 2) BY `db2.tablespace.name` "
            "| WHERE `db2.tablespace.name` IS NOT NULL | SORT used_gb DESC | LIMIT 12",
            "bar_horizontal", "db2.tablespace.name", ["used_gb", "total_gb"])),
        P((24, 16, 24, 11), "Deadlocks & sort overflows", viz_xy(
            "Deadlocks vs sort overflows (cumulative-style counters)",
            f"FROM {IDX} | EVAL _d = TO_DOUBLE(`db2.deadlock.count`), _s = TO_DOUBLE(`db2.sort.overflow.count`) "
            f"| STATS deadlocks = MAX(_d), sort_ovf = MAX(_s) BY bucket = {TB}",
            "line", "bucket", ["deadlocks", "sort_ovf"])),
        P((0, 27, 48, 10), "Log utilization over time", viz_xy(
            "Transaction log utilization %",
            f"FROM {IDX} | STATS log_pct = AVG(`db2.log.utilization`) BY bucket = {TB}, `host.name`",
            "area", "bucket", ["log_pct"], "host.name")),
        *ai_recommendation_panels(37, "db2", include_legacy_null=True),
    ]
    return create_dashboard_api(
        "IBM Db2 \u2014 Performance & Health (LUW)",
        "Connections, buffer pool, log utilization, lock waits, tablespaces, and sort health via synthetic OpenTelemetry db2.* metrics. "
        f"Latest AI text is read from index {REC_INDEX} (written by the AI recommendations workflow).",
        panels,
    )


def build_oracle():
    print("  Building Oracle dashboard (Dashboards API)...")
    IDX = "metrics-oracledbreceiver.otel.otel-default"
    TB = TB_AUTO
    panels = [
        P((0, 0, 12, 5), "Active Sessions", viz_metric(
            "", f"FROM {IDX} | WHERE session.type == \"active\" | STATS `Active Sessions` = MAX(`oracledb.sessions.current`)",
            "Active Sessions")),
        P((12, 0, 12, 5), "Processes", viz_metric(
            "", f"FROM {IDX} | STATS `Processes` = MAX(`oracledb.processes.count`)", "Processes")),
        P((24, 0, 12, 5), "Physical Reads", viz_metric(
            "", f"FROM {IDX} | EVAL _p = TO_DOUBLE(`oracledb.physical_reads`) | STATS `Physical Reads` = MAX(_p)",
            "Physical Reads")),
        P((36, 0, 12, 5), "User Commits", viz_metric(
            "", f"FROM {IDX} | EVAL _c = TO_DOUBLE(`oracledb.user_commits`) | STATS `User Commits` = MAX(_c)",
            "User Commits")),
        P((0, 5, 24, 11), "Sessions Over Time", viz_xy(
            "Sessions Over Time (Active vs Inactive)",
            f"FROM {IDX} | STATS sessions = AVG(`oracledb.sessions.current`) BY bucket = {TB}, `session.type` | WHERE `session.type` IS NOT NULL",
            "area_stacked", "bucket", ["sessions"], "session.type")),
        P((24, 5, 24, 11), "Tablespace Utilisation", viz_xy(
            "Tablespace Utilisation (Used GB)",
            f"FROM {IDX} | WHERE `oracledb.tablespace.used` IS NOT NULL | STATS used_gb = ROUND(MAX(`oracledb.tablespace.used`) / 1073741824.0, 2), total_gb = ROUND(MAX(`oracledb.tablespace.size`) / 1073741824.0, 2) BY `tablespace_name` | WHERE `tablespace_name` IS NOT NULL | SORT used_gb DESC | LIMIT 10",
            "bar_horizontal", "tablespace_name", ["used_gb", "total_gb"])),
        P((0, 16, 24, 11), "Physical vs Logical Reads", viz_xy(
            "Physical vs Logical Reads Over Time",
            f"FROM {IDX} | EVAL _p = TO_DOUBLE(`oracledb.physical_reads`), _l = TO_DOUBLE(`oracledb.logical_reads`) | STATS physical = MAX(_p), logical = MAX(_l) BY bucket = {TB}, `service.name`",
            "line", "bucket", ["physical", "logical"], "service.name")),
        P((24, 16, 24, 11), "Parse Rate", viz_xy(
            "Hard vs Total Parses Over Time",
            f"FROM {IDX} | EVAL _h = TO_DOUBLE(`oracledb.hard_parses`), _t = TO_DOUBLE(`oracledb.parse_calls`) | STATS hard = MAX(_h), total = MAX(_t) BY bucket = {TB}",
            "line", "bucket", ["hard", "total"])),
        P((0, 27, 24, 11), "Active Transactions", viz_xy(
            "Active Transactions Over Time",
            f"FROM {IDX} | STATS txns = AVG(`oracledb.transactions`) BY bucket = {TB}, `service.name`",
            "area", "bucket", ["txns"], "service.name")),
        P((24, 27, 24, 11), "PGA Memory", viz_xy(
            "PGA Memory (GB) Over Time",
            f"FROM {IDX} | STATS pga_gb = ROUND(AVG(`oracledb.pga_memory`) / 1073741824.0, 2) BY bucket = {TB}, `service.name`",
            "line", "bucket", ["pga_gb"], "service.name")),
        *ai_recommendation_panels(38, "oracle"),
    ]
    return create_dashboard_api(
        "Oracle \u2014 Performance & Health",
        "Sessions, tablespace utilisation, parse efficiency, reads, transactions, PGA memory, and AI workflow output (index "
        f"{REC_INDEX}) via OpenTelemetry",
        panels,
    )


if __name__ == "__main__":
    dashboards = [
        ("MySQL \u2014 Slow Query & Error Monitoring", build_mysql),
        ("PostgreSQL \u2014 Performance & Health", build_postgres),
        ("SQL Server \u2014 Performance & Health", build_mssql),
        ("SQL Server \u2014 Overview (Datadog Equivalent)", build_mssql_overview),
        ("Spotlight \u2014 Severity grid (SQL Server, Windows, MongoDB)", build_spotlight_heatmap),
        ("Spotlight \u2014 Flow & topology (SQL Server, synthetic)", build_spotlight_flow),
        ("Spotlight \u2014 SQL Server Overview (synthetic)", build_spotlight_sql_overview),
        ("MongoDB \u2014 Operations & Health", build_mongodb),
        ("IBM Db2 \u2014 Performance & Health (LUW)", build_db2),
        ("Oracle \u2014 Performance & Health", build_oracle),
    ]
    existing = list_dashboard_ids_by_title()
    ids = []
    for name, builder in dashboards:
        print(f"\nDeploying: {name}")
        old_id = existing.get(name)
        if old_id:
            print(f"  Removing previous definition (id={old_id})…")
            if not delete_dashboard_by_id(old_id):
                print(f"  WARN: could not delete existing dashboard {old_id}", file=sys.stderr)
        dash_id = builder()
        ids.append((name, dash_id))
        print(f"  ✓ Dashboard ID: {dash_id}")

    print(f"\n{'='*60}")
    print("All dashboards deployed successfully!")
    print(f"{'='*60}")
    for name, dash_id in ids:
        print(f"  {name}")
        print(f"    {KIBANA_URL}/app/dashboards#/view/{dash_id}")
    print(f"\nDashboard list: {KIBANA_URL}/app/dashboards")
