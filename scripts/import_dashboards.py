#!/usr/bin/env python3
"""
Import DB monitoring dashboards into Kibana.
Uses POST /api/saved_objects/lens + /api/saved_objects/dashboard directly.
Works on all Kibana Serverless versions — no feature flags required.

Usage:  python3 scripts/import_dashboards.py
Env:    KIBANA_URL, ES_API_KEY (or ES_USERNAME + ES_PASSWORD)
"""
import json, os, sys, uuid, urllib.request, urllib.error, base64

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
API_KEY    = os.environ.get("ES_API_KEY", "") or os.environ.get("KIBANA_API_KEY", "")
ES_PASS    = os.environ.get("ES_PASSWORD", "") or os.environ.get("ELASTICSEARCH_PASSWORD", "")
ES_USER    = os.environ.get("ES_USERNAME", "admin")

if not KIBANA_URL:
    sys.exit("ERROR: KIBANA_URL not set")
if not API_KEY and not ES_PASS:
    sys.exit("ERROR: ES_API_KEY or ES_PASSWORD not set")

HEADERS = {
    "Authorization": f"ApiKey {API_KEY}" if API_KEY
                     else "Basic " + base64.b64encode(f"{ES_USER}:{ES_PASS}".encode()).decode(),
    "kbn-xsrf": "true",
    "x-elastic-internal-origin": "kibana",
    "Content-Type": "application/json",
}


def gid(): return str(uuid.uuid4())


def post(path, body):
    req = urllib.request.Request(
        f"{KIBANA_URL}{path}", data=json.dumps(body).encode(), headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        sys.exit(f"HTTP {e.code} on {path}: {msg[:400]}")


def create_lens(title, vis_type, state):
    result = post("/api/saved_objects/lens", {"attributes": {
        "title": title, "visualizationType": vis_type, "state": state,
    }})
    return result["id"]


def esql_state_metric(esql_query, col_name):
    lid, cid = gid(), gid()
    return {
        "visualization": {"layerId": lid, "layerType": "data", "metricAccessor": cid},
        "query": {"language": "kuery", "query": ""}, "filters": [],
        "datasourceStates": {"textBased": {"layers": {lid: {
            "query": {"esql": esql_query},
            "columns": [{"columnId": cid, "fieldName": col_name, "meta": {"type": "number"}}],
        }}}},
    }


def esql_state_xy(esql_query, series_type, x_col, y_cols, breakdown_col=None, x_type="date"):
    lid = gid()
    x_cid = gid()
    y_cids = [gid() for _ in y_cols]
    bd_cid = gid() if breakdown_col else None

    columns = [{"columnId": x_cid, "fieldName": x_col, "meta": {"type": x_type}}]
    for i, y in enumerate(y_cols):
        columns.append({"columnId": y_cids[i], "fieldName": y, "meta": {"type": "number"}})
    if breakdown_col:
        columns.append({"columnId": bd_cid, "fieldName": breakdown_col, "meta": {"type": "string"}})

    layer = {"layerId": lid, "layerType": "data", "seriesType": series_type,
             "xAccessor": x_cid, "accessors": y_cids}
    if breakdown_col:
        layer["splitAccessor"] = bd_cid

    return {
        "visualization": {
            "legend": {"isVisible": True, "position": "right"},
            "valueLabels": "hide", "preferredSeriesType": series_type,
            "layers": [layer],
        },
        "query": {"language": "kuery", "query": ""}, "filters": [],
        "datasourceStates": {"textBased": {"layers": {lid: {
            "query": {"esql": esql_query},
            "columns": columns,
        }}}},
    }


def esql_state_heatmap(esql_query, x_col, y_col, metric_col, x_type="date", y_type="string"):
    """Lens heat map: X = time bucket, Y = host row, color = numeric severity."""
    lid = gid()
    x_cid, y_cid, m_cid = gid(), gid(), gid()
    columns = [
        {"columnId": x_cid, "fieldName": x_col, "meta": {"type": x_type}},
        {"columnId": y_cid, "fieldName": y_col, "meta": {"type": y_type}},
        {"columnId": m_cid, "fieldName": metric_col, "meta": {"type": "number"}},
    ]
    return {
        "visualization": {
            "legend": {"isVisible": True, "position": "right", "shouldTruncate": True},
            "shape": "heatmap",
            "layers": [{
                "layerId": lid,
                "layerType": "data",
                "xAccessor": x_cid,
                "yAccessor": y_cid,
                "metricAccessor": m_cid,
            }],
        },
        "query": {"language": "kuery", "query": ""},
        "filters": [],
        "datasourceStates": {"textBased": {"layers": {lid: {
            "query": {"esql": esql_query},
            "columns": columns,
        }}}},
    }


def esql_state_gauge(esql_query, col_name):
    """Horizontal bullet-style gauge (CPU %, health rating)."""
    lid, cid = gid(), gid()
    return {
        "visualization": {
            "layerId": lid,
            "layerType": "data",
            "metricAccessor": cid,
            "shape": "horizontalBullet",
        },
        "query": {"language": "kuery", "query": ""},
        "filters": [],
        "datasourceStates": {"textBased": {"layers": {lid: {
            "query": {"esql": esql_query},
            "columns": [{"columnId": cid, "fieldName": col_name, "meta": {"type": "number"}}],
        }}}},
    }


def esql_state_table(esql_query, columns):
    """columns: list of (field_name, col_type) — col_type is 'string' or 'number'"""
    lid = gid()
    col_defs = []
    vis_cols = []
    for fname, ctype in columns:
        cid = gid()
        col_defs.append({"columnId": cid, "fieldName": fname, "meta": {"type": ctype}})
        vis_cols.append({"columnId": cid, "summaryRow": "none"})
    return {
        "visualization": {
            "layerId": lid, "layerType": "data",
            "columns": vis_cols, "sorting": None,
        },
        "query": {"language": "kuery", "query": ""}, "filters": [],
        "datasourceStates": {"textBased": {"layers": {lid: {
            "query": {"esql": esql_query},
            "columns": col_defs,
        }}}},
    }


def create_dashboard(title, description, panels_grids, time_from="now-2h"):
    """panels_grids: list of (lens_id, (x,y,w,h), panel_title)"""
    panels_json = []
    references  = []
    for lens_id, (x, y, w, h), ptitle in panels_grids:
        pid = gid()
        panels_json.append({
            "version": "10.1.0", "type": "lens",
            "gridData": {"x": x, "y": y, "w": w, "h": h, "i": pid},
            "panelIndex": pid,
            "embeddableConfig": {"enhancements": {}, "title": ptitle},
            "panelRefName": f"panel_{pid}",
        })
        references.append({"name": f"panel_{pid}", "type": "lens", "id": lens_id})

    result = post("/api/saved_objects/dashboard", {
        "attributes": {
            "title": title, "description": description,
            "panelsJSON": json.dumps(panels_json),
            "optionsJSON": json.dumps({"useMargins": True, "syncColors": False,
                                       "syncCursor": True, "syncTooltips": False,
                                       "hidePanelTitles": False}),
            "version": 1, "timeRestore": True, "timeFrom": time_from, "timeTo": "now",
            "kibanaSavedObjectMeta": {"searchSourceJSON": json.dumps(
                {"query": {"language": "kuery", "query": ""}, "filter": []})},
        },
        "references": references,
    })
    return result["id"]


# ---------------------------------------------------------------------------
# Dashboard builders
# ---------------------------------------------------------------------------

def build_mysql():
    print("  Creating MySQL Lens panels...")
    kpi_slow = create_lens("Total Slow Queries", "lnsMetric", esql_state_metric(
        "FROM logs-mysql.slowlog.otel.otel-default | STATS `Total Slow Queries` = COUNT(*)", "Total Slow Queries"))
    kpi_avg = create_lens("Avg Query Time (s)", "lnsMetric", esql_state_metric(
        "FROM logs-mysql.slowlog.otel.otel-default | STATS `Avg Query Time (s)` = AVG(`mysql.slowlog.query_time`)", "Avg Query Time (s)"))
    kpi_max = create_lens("Max Query Time (s)", "lnsMetric", esql_state_metric(
        "FROM logs-mysql.slowlog.otel.otel-default | STATS `Max Query Time (s)` = MAX(`mysql.slowlog.query_time`)", "Max Query Time (s)"))
    kpi_err = create_lens("DB Errors", "lnsMetric", esql_state_metric(
        "FROM logs-mysql.error.otel.otel-default | STATS `DB Errors` = COUNT(*)", "DB Errors"))
    slow_rate = create_lens("Slow Query Rate by Database", "lnsXY", esql_state_xy(
        "FROM logs-mysql.slowlog.otel.otel-default | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1 hour), `db.name`",
        "area_stacked", "bucket", ["count"], "db.name"))
    query_time = create_lens("Avg Query Time by Database (s)", "lnsXY", esql_state_xy(
        "FROM logs-mysql.slowlog.otel.otel-default | STATS avg_time = AVG(`mysql.slowlog.query_time`) BY bucket = BUCKET(@timestamp, 1 hour), `db.name`",
        "line", "bucket", ["avg_time"], "db.name"))
    top_tables = create_lens("Top Tables by Slow Query Count", "lnsXY", esql_state_xy(
        "FROM logs-mysql.slowlog.otel.otel-default | STATS count = COUNT(*) BY `db.sql.table` | SORT count DESC | LIMIT 15",
        "bar_horizontal", "db.sql.table", ["count"], x_type="string"))
    lock_vs_q = create_lens("Avg Query vs Lock Time by Database", "lnsXY", esql_state_xy(
        "FROM logs-mysql.slowlog.otel.otel-default | STATS avg_query = AVG(`mysql.slowlog.query_time`), avg_lock = AVG(`mysql.slowlog.lock_time`) BY `db.name`",
        "bar", "db.name", ["avg_query", "avg_lock"], x_type="string"))
    err_trend = create_lens("Error Log Trend", "lnsXY", esql_state_xy(
        "FROM logs-mysql.error.otel.otel-default | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1 hour), `log.level`",
        "bar_stacked", "bucket", ["count"], "log.level"))

    return create_dashboard(
        "MySQL \u2014 Slow Query & Error Monitoring",
        "Slow queries, lock contention, error trends, and top tables via OpenTelemetry",
        [
            (kpi_slow,   (0,  0, 12, 5), "Total Slow Queries"),
            (kpi_avg,    (12, 0, 12, 5), "Avg Query Time (s)"),
            (kpi_max,    (24, 0, 12, 5), "Max Query Time (s)"),
            (kpi_err,    (36, 0, 12, 5), "DB Errors"),
            (slow_rate,  (0,  5, 24, 11), "Slow Query Rate by Database"),
            (query_time, (24, 5, 24, 11), "Avg Query Time by Database (s)"),
            (top_tables, (0,  16, 24, 11), "Top Tables by Slow Query Count"),
            (lock_vs_q,  (24, 16, 24, 11), "Avg Query vs Lock Time by Database"),
            (err_trend,  (0,  27, 48, 11), "Error Log Trend"),
        ],
        time_from="now-4d")


def build_postgres():
    print("  Creating PostgreSQL Lens panels...")
    kpi_conn = create_lens("Active Connections", "lnsMetric", esql_state_metric(
        "FROM metrics-postgresqlreceiver.otel.otel-default | STATS `Active Connections` = MAX(`postgresql.backends`)", "Active Connections"))
    kpi_dead = create_lens("Total Deadlocks", "lnsMetric", esql_state_metric(
        "FROM metrics-postgresqlreceiver.otel.otel-default | EVAL _dl = TO_DOUBLE(`postgresql.deadlocks`) | STATS `Total Deadlocks` = MAX(_dl)", "Total Deadlocks"))
    kpi_size = create_lens("Max DB Size (bytes)", "lnsMetric", esql_state_metric(
        "FROM metrics-postgresqlreceiver.otel.otel-default | STATS `Max DB Size` = MAX(`postgresql.db_size`)", "Max DB Size"))
    kpi_lim = create_lens("Connection Limit", "lnsMetric", esql_state_metric(
        "FROM metrics-postgresqlreceiver.otel.otel-default | STATS `Connection Limit` = MAX(`postgresql.connection.max`)", "Connection Limit"))
    conn_t = create_lens("Active Connections Over Time", "lnsXY", esql_state_xy(
        "FROM metrics-postgresqlreceiver.otel.otel-default | STATS backends = AVG(`postgresql.backends`) BY bucket = BUCKET(@timestamp, 5 minute), `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
        "area_stacked", "bucket", ["backends"], "postgresql.database.name"))
    size_b = create_lens("Database Size by Database", "lnsXY", esql_state_xy(
        "FROM metrics-postgresqlreceiver.otel.otel-default | STATS db_size = MAX(`postgresql.db_size`) BY `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL | SORT db_size DESC | LIMIT 10",
        "bar_horizontal", "postgresql.database.name", ["db_size"], x_type="string"))
    deadlocks = create_lens("Deadlocks Over Time by Database", "lnsXY", esql_state_xy(
        "FROM metrics-postgresqlreceiver.otel.otel-default | EVAL _dl = TO_DOUBLE(`postgresql.deadlocks`) | STATS deadlocks = MAX(_dl) BY bucket = BUCKET(@timestamp, 5 minute), `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
        "bar_stacked", "bucket", ["deadlocks"], "postgresql.database.name"))
    rows = create_lens("Rows Inserted / Updated / Deleted", "lnsXY", esql_state_xy(
        "FROM metrics-postgresqlreceiver.otel.otel-default | EVAL _ins = TO_DOUBLE(`postgresql.tup_inserted`), _upd = TO_DOUBLE(`postgresql.tup_updated`), _del = TO_DOUBLE(`postgresql.tup_deleted`) | STATS inserted = MAX(_ins), updated = MAX(_upd), deleted = MAX(_del) BY bucket = BUCKET(@timestamp, 5 minute)",
        "line", "bucket", ["inserted", "updated", "deleted"]))

    return create_dashboard(
        "PostgreSQL \u2014 Performance & Health",
        "Connections, deadlocks, database size, and row operations via OpenTelemetry",
        [
            (kpi_conn,  (0,  0, 12, 5), "Active Connections"),
            (kpi_dead,  (12, 0, 12, 5), "Total Deadlocks"),
            (kpi_size,  (24, 0, 12, 5), "Max DB Size"),
            (kpi_lim,   (36, 0, 12, 5), "Connection Limit"),
            (conn_t,    (0,  5, 24, 11), "Active Connections Over Time"),
            (size_b,    (24, 5, 24, 11), "Database Size"),
            (deadlocks, (0,  16, 24, 11), "Deadlocks Over Time"),
            (rows,      (24, 16, 24, 11), "Row Operations"),
        ])


def build_mssql():
    print("  Creating SQL Server Lens panels...")
    kpi_conn  = create_lens("User Connections", "lnsMetric", esql_state_metric(
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS `User Connections` = MAX(`sqlserver.user.connection.count`)", "User Connections"))
    kpi_cache = create_lens("Buffer Cache Hit %", "lnsMetric", esql_state_metric(
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS `Buffer Cache Hit %` = AVG(`sqlserver.page.buffer_cache.hit_ratio`)", "Buffer Cache Hit %"))
    kpi_lock  = create_lens("Avg Lock Wait (ms)", "lnsMetric", esql_state_metric(
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS `Avg Lock Wait (ms)` = AVG(`sqlserver.lock.wait_time.avg`)", "Avg Lock Wait (ms)"))
    kpi_dead  = create_lens("Total Deadlocks", "lnsMetric", esql_state_metric(
        "FROM metrics-sqlserverreceiver.otel.otel-default | EVAL _dl = TO_DOUBLE(`sqlserver.deadlock.count`) | STATS `Total Deadlocks` = MAX(_dl)", "Total Deadlocks"))
    conn_t    = create_lens("User Connections Over Time", "lnsXY", esql_state_xy(
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS connections = AVG(`sqlserver.user.connection.count`) BY bucket = BUCKET(@timestamp, 5 minute), `service.name`",
        "area", "bucket", ["connections"], "service.name"))
    lock_t    = create_lens("Lock Wait Time (ms) Over Time", "lnsXY", esql_state_xy(
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS lock_wait = AVG(`sqlserver.lock.wait_time.avg`) BY bucket = BUCKET(@timestamp, 5 minute), `service.name`",
        "line", "bucket", ["lock_wait"], "service.name"))
    io_lat    = create_lens("I/O Read vs Write Latency by Database", "lnsXY", esql_state_xy(
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS read_lat = AVG(`sqlserver.database.io.read_latency`), write_lat = AVG(`sqlserver.database.io.write_latency`) BY `sqlserver.database.name` | WHERE `sqlserver.database.name` IS NOT NULL | SORT read_lat DESC | LIMIT 10",
        "bar", "sqlserver.database.name", ["read_lat", "write_lat"], x_type="string"))
    batches   = create_lens("Batch Requests Over Time", "lnsXY", esql_state_xy(
        "FROM metrics-sqlserverreceiver.otel.otel-default | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) | STATS batches = MAX(_b) BY bucket = BUCKET(@timestamp, 5 minute), `service.name`",
        "line", "bucket", ["batches"], "service.name"))

    return create_dashboard(
        "SQL Server \u2014 Performance & Health",
        "Connections, lock waits, batch requests, buffer cache, and I/O latency via OpenTelemetry",
        [
            (kpi_conn,  (0,  0, 12, 5), "User Connections"),
            (kpi_cache, (12, 0, 12, 5), "Buffer Cache Hit %"),
            (kpi_lock,  (24, 0, 12, 5), "Avg Lock Wait (ms)"),
            (kpi_dead,  (36, 0, 12, 5), "Total Deadlocks"),
            (conn_t,    (0,  5, 24, 11), "Connections Over Time"),
            (lock_t,    (24, 5, 24, 11), "Lock Wait Time Over Time"),
            (io_lat,    (0,  16, 24, 11), "I/O Latency by Database"),
            (batches,   (24, 16, 24, 11), "Batch Requests Over Time"),
        ])


def build_mssql_overview():
    """Datadog SQL Server Overview equivalent — same layout as the Datadog screenshot."""
    print("  Creating SQL Server Overview (Datadog-equivalent) Lens panels...")
    IDX = "metrics-sqlserverreceiver.otel.otel-default"

    # ── KPI row (mirrors Datadog: Batch reqs/s · User conns · Buffer cache % · Deadlocks) ──
    kpi_batch = create_lens("Batch Requests/sec", "lnsMetric", esql_state_metric(
        f"FROM {IDX} | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) | STATS `Batch Requests/sec` = MAX(_b)",
        "Batch Requests/sec"))
    kpi_conn  = create_lens("User Connections", "lnsMetric", esql_state_metric(
        f"FROM {IDX} | STATS `User Connections` = MAX(`sqlserver.user.connection.count`)",
        "User Connections"))
    kpi_cache = create_lens("Buffer Cache Hit %", "lnsMetric", esql_state_metric(
        f"FROM {IDX} | STATS `Buffer Cache Hit %` = ROUND(AVG(`sqlserver.page.buffer_cache.hit_ratio`), 1)",
        "Buffer Cache Hit %"))
    kpi_dead  = create_lens("Deadlocks", "lnsMetric", esql_state_metric(
        f"FROM {IDX} | EVAL _d = TO_DOUBLE(`sqlserver.deadlock.count`) | STATS `Deadlocks` = MAX(_d)",
        "Deadlocks"))

    # ── Row 2: User Connections stacked area + Batch Requests line (Datadog "Usage" section) ──
    conn_area = create_lens("User Connections Over Time", "lnsXY", esql_state_xy(
        f"FROM {IDX} | STATS conns = MAX(`sqlserver.user.connection.count`) BY bucket = BUCKET(@timestamp, 5 minute), `service.instance.id`",
        "area_stacked", "bucket", ["conns"], "service.instance.id"))
    batch_line = create_lens("Batch Requests Over Time", "lnsXY", esql_state_xy(
        f"FROM {IDX} | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) | STATS batch = MAX(_b) BY bucket = BUCKET(@timestamp, 5 minute), `service.instance.id`",
        "line", "bucket", ["batch"], "service.instance.id"))

    # ── Row 3: Lock wait time + I/O latency (Datadog "Page splits" / "SQL compilations" equiv) ──
    lock_line = create_lens("Lock Wait Time (ms) Over Time", "lnsXY", esql_state_xy(
        f"FROM {IDX} | STATS lock_ms = AVG(`sqlserver.lock.wait_time.avg`) BY bucket = BUCKET(@timestamp, 5 minute), `service.instance.id`",
        "line", "bucket", ["lock_ms"], "service.instance.id"))
    io_line = create_lens("Read vs Write I/O Latency (ms)", "lnsXY", esql_state_xy(
        f"FROM {IDX} | STATS read_ms = AVG(`sqlserver.database.io.read_latency`), write_ms = AVG(`sqlserver.database.io.write_latency`) BY bucket = BUCKET(@timestamp, 5 minute)",
        "line", "bucket", ["read_ms", "write_ms"]))

    # ── Row 4: Instance summary table (mirrors Datadog "Top Databases" table) ──
    summary = create_lens("Instance Summary Table", "lnsTable", esql_state_table(
        f"FROM {IDX} | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`), _d = TO_DOUBLE(`sqlserver.deadlock.count`) | STATS `Max Connections` = MAX(`sqlserver.user.connection.count`), `Buffer Cache %` = ROUND(AVG(`sqlserver.page.buffer_cache.hit_ratio`), 1), `Avg Lock Wait (ms)` = ROUND(AVG(`sqlserver.lock.wait_time.avg`), 2), `Deadlocks` = MAX(_d), `Batch Requests` = MAX(_b) BY `Instance` = `service.instance.id` | SORT `Max Connections` DESC",
        [("Instance", "string"), ("Max Connections", "number"), ("Buffer Cache %", "number"),
         ("Avg Lock Wait (ms)", "number"), ("Deadlocks", "number"), ("Batch Requests", "number")]))

    return create_dashboard(
        "SQL Server \u2014 Overview (Datadog Equivalent)",
        "Mirrors the Datadog SQL Server Overview: batch requests, user connections, buffer cache, lock waits, I/O latency, and per-instance summary table.",
        [
            (kpi_batch,  (0,  0, 12, 5), "Batch Requests/sec"),
            (kpi_conn,   (12, 0, 12, 5), "User Connections"),
            (kpi_cache,  (24, 0, 12, 5), "Buffer Cache Hit %"),
            (kpi_dead,   (36, 0, 12, 5), "Deadlocks"),
            (conn_area,  (0,  5, 24, 11), "User Connections Over Time"),
            (batch_line, (24, 5, 24, 11), "Batch Requests Over Time"),
            (lock_line,  (0,  16, 24, 11), "Lock Wait Time (ms)"),
            (io_line,    (24, 16, 24, 11), "Read vs Write I/O Latency"),
            (summary,    (0,  27, 48, 10), "Instance Summary"),
        ])


def build_mongodb():
    print("  Creating MongoDB Lens panels...")
    kpi_conn = create_lens("Active Connections", "lnsMetric", esql_state_metric(
        "FROM metrics-mongodbatlas.otel.otel-default | STATS `Active Connections` = MAX(`mongodb.connection.count`)", "Active Connections"))
    kpi_mem  = create_lens("Memory Usage (GB)", "lnsMetric", esql_state_metric(
        "FROM metrics-mongodbatlas.otel.otel-default | EVAL _mem_gb = `mongodb.memory.usage` / 1073741824.0 | STATS `Memory Usage (GB)` = ROUND(MAX(_mem_gb), 2)", "Memory Usage (GB)"))
    kpi_ops  = create_lens("Total Operations", "lnsMetric", esql_state_metric(
        "FROM metrics-mongodbatlas.otel.otel-default | EVAL _ops = TO_DOUBLE(`mongodb.operation.count`) | STATS `Total Operations` = MAX(_ops)", "Total Operations"))
    kpi_repl = create_lens("Replication Lag (s)", "lnsMetric", esql_state_metric(
        "FROM metrics-mongodbatlas.otel.otel-default | STATS `Replication Lag (s)` = AVG(`mongodb.replication.lag`)", "Replication Lag (s)"))
    ops_t    = create_lens("Operations Over Time by Type", "lnsXY", esql_state_xy(
        "FROM metrics-mongodbatlas.otel.otel-default | EVAL _ops = TO_DOUBLE(`mongodb.operation.count`) | STATS ops = MAX(_ops) BY bucket = BUCKET(@timestamp, 5 minute), `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
        "area_stacked", "bucket", ["ops"], "mongodb.operation.type"))
    conn_t   = create_lens("Connections by Instance", "lnsXY", esql_state_xy(
        "FROM metrics-mongodbatlas.otel.otel-default | STATS conns = AVG(`mongodb.connection.count`) BY bucket = BUCKET(@timestamp, 5 minute), `service.name`",
        "line", "bucket", ["conns"], "service.name"))
    mem_t    = create_lens("Memory: Resident vs Virtual (GB)", "lnsXY", esql_state_xy(
        "FROM metrics-mongodbatlas.otel.otel-default | EVAL _res = `mongodb.memory.usage` / 1073741824.0, _virt = `mongodb.memory.virtual` / 1073741824.0 | STATS resident = ROUND(AVG(_res), 2), virtual = ROUND(AVG(_virt), 2) BY bucket = BUCKET(@timestamp, 5 minute)",
        "area", "bucket", ["resident", "virtual"]))
    docs     = create_lens("Document Operations Over Time", "lnsXY", esql_state_xy(
        "FROM metrics-mongodbatlas.otel.otel-default | EVAL _docs = TO_DOUBLE(`mongodb.document.operation.count`) | STATS docs = MAX(_docs) BY bucket = BUCKET(@timestamp, 5 minute), `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
        "line", "bucket", ["docs"], "mongodb.operation.type"))

    return create_dashboard(
        "MongoDB \u2014 Operations & Health",
        "Operation throughput, connections, memory, replication lag, and document stats via OpenTelemetry",
        [
            (kpi_conn, (0,  0, 12, 5), "Active Connections"),
            (kpi_mem,  (12, 0, 12, 5), "Memory Usage"),
            (kpi_ops,  (24, 0, 12, 5), "Total Operations"),
            (kpi_repl, (36, 0, 12, 5), "Replication Lag (s)"),
            (ops_t,    (0,  5, 24, 11), "Operations Over Time"),
            (conn_t,   (24, 5, 24, 11), "Connections by Instance"),
            (mem_t,    (0,  16, 24, 11), "Memory Trend"),
            (docs,     (24, 16, 24, 11), "Document Operations"),
        ])


# Indices union for Spotlight heat map (SQL Server + Windows + MongoDB rows)
_SPOTLIGHT_FROM = (
    "metrics-sqlserverreceiver.otel.otel-default, metrics-mongodbatlas.otel.otel-default"
)


def build_spotlight_heatmap():
    """Quest Spotlight–style health grid: severity 0–3 over time × host row (SQL / Windows / Mongo)."""
    print("  Creating Spotlight heat map Lens panels...")
    q_hm = (
        f"FROM {_SPOTLIGHT_FROM} "
        "| WHERE `spotlight.grid_row` IS NOT NULL "
        "| STATS `sev` = MAX(`spotlight.health.severity`) "
        "BY bucket = BUCKET(@timestamp, 5 minute), `spotlight.grid_row`"
    )
    heat = create_lens("Spotlight Health Heat Map", "lnsHeatmap", esql_state_heatmap(
        q_hm, "bucket", "spotlight.grid_row", "sev"))

    q_line = (
        f"FROM {_SPOTLIGHT_FROM} "
        "| WHERE `spotlight.grid_row` IS NOT NULL "
        "| STATS `Severity` = MAX(`spotlight.health.severity`) "
        "BY bucket = BUCKET(@timestamp, 5 minute), `spotlight.grid_row`"
    )
    lines = create_lens("Severity trend by row", "lnsXY", esql_state_xy(
        q_line, "line", "bucket", ["Severity"], "spotlight.grid_row"))

    q_bar = (
        f"FROM {_SPOTLIGHT_FROM} "
        "| WHERE `spotlight.grid_row` IS NOT NULL "
        "| STATS `Avg severity` = AVG(`spotlight.health.severity`) BY `spotlight.grid_row` "
        "| SORT `Avg severity` DESC"
    )
    rank = create_lens("Average severity by row", "lnsXY", esql_state_xy(
        q_bar, "bar_horizontal", "spotlight.grid_row", ["Avg severity"], x_type="string"))

    q_tbl = (
        f"FROM {_SPOTLIGHT_FROM} "
        "| WHERE `spotlight.grid_row` IS NOT NULL "
        "| STATS `Peak` = MAX(`spotlight.health.severity`), `Samples` = COUNT(*) "
        "BY `spotlight.grid_row`, `cloud.platform`, `spotlight.entity_type` "
        "| SORT `Peak` DESC"
    )
    tbl = create_lens("Health grid detail", "lnsTable", esql_state_table(
        q_tbl,
        [("spotlight.grid_row", "string"), ("cloud.platform", "string"),
         ("spotlight.entity_type", "string"), ("Peak", "number"), ("Samples", "number")],
    ))

    return create_dashboard(
        "Spotlight \u2014 Health Heat Map (SQL Server, Windows, MongoDB)",
        "Color scale: 0 = informational (blue), 1 = healthy (green), 2 = warning (yellow), "
        "3 = critical (red). Rows = SQL Server instance, Windows host, or MongoDB node; "
        "includes on-premises and Azure/AWS (Atlas) synthetic labels.",
        [
            (heat,  (0,  0, 36, 14), "Health heat map (time \u00d7 host row)"),
            (lines, (36, 0, 12, 14), "Severity lines"),
            (rank,  (0,  14, 24, 12), "Avg severity ranking"),
            (tbl,   (24, 14, 24, 12), "Peak severity + cloud platform"),
        ],
    )


def build_spotlight_sql_overview():
    """Mirrors Spotlight SQL Server Overview widgets using synthetic sqlserver.spotlight.* metrics."""
    print("  Creating Spotlight SQL Server Overview Lens panels...")
    IDX = "metrics-sqlserverreceiver.otel.otel-default"
    H = 'host.name == "mssql-prod-01"'

    def w(q):
        return q.replace("__FILTER__", H)

    sess_rt = create_lens("Session response time", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Response time (ms)` = AVG(`sqlserver.spotlight.session.response_time_ms`)"),
        "Response time (ms)"))
    sess_ct = create_lens("Session count", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Active sessions` = MAX(`sqlserver.spotlight.session.active.count`)"),
        "Active sessions"))
    sess_max = create_lens("Max sessions", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Max sessions` = MAX(`sqlserver.spotlight.session.max.count`)"),
        "Max sessions"))
    computers = create_lens("Computers", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Computers` = MAX(`sqlserver.spotlight.computers.count`)"),
        "Computers"))
    sess_bar = create_lens("Active sessions % of max", "lnsXY", esql_state_xy(
        w(f"FROM {IDX} | WHERE __FILTER__ "
          "| STATS pct = MAX(`sqlserver.spotlight.session.active_pct`) "
          "| EVAL `Utilisation` = \"Active % of max\""),
        "bar_horizontal", "Utilisation", ["pct"], x_type="string"))

    perf_g = create_lens("Performance health rating", "lnsGauge", esql_state_gauge(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Health rating` = MAX(`sqlserver.spotlight.performance_health.rating`)"),
        "Health rating"))

    sys_tbl = create_lens("System & performance status", "lnsTable", esql_state_table(
        w(f"FROM {IDX} | WHERE __FILTER__ "
          "| STATS `Rating` = ROUND(MAX(`sqlserver.spotlight.performance_health.rating`), 1), "
          "`SQL build` = MAX(`sqlserver.build_version`), "
          "`Host` = MAX(`host.name`), "
          "`Cloud` = MAX(`cloud.platform`), "
          "`Custom status` = MAX(`sqlserver.spotlight.custom_status`), "
          "`Virtual host` = MAX(`host.is_virtual`)"),
        [("Rating", "number"), ("SQL build", "string"), ("Host", "string"),
         ("Cloud", "string"), ("Custom status", "string"), ("Virtual host", "string")],
    ))

    pr_tot = create_lens("Processes total", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Total` = MAX(`sqlserver.spotlight.processes.total`)"),
        "Total"))
    pr_sys = create_lens("Processes system", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `System` = MAX(`sqlserver.spotlight.processes.system`)"),
        "System"))
    pr_usr = create_lens("Processes user", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `User` = MAX(`sqlserver.spotlight.processes.user`)"),
        "User"))
    pr_blk = create_lens("Blocked", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Blocked` = MAX(`sqlserver.spotlight.processes.blocked`)"),
        "Blocked"))
    batches = create_lens("Batch requests (counter)", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) "
          "| STATS `Batch requests` = MAX(_b)"),
        "Batch requests"))

    virt_g = create_lens("Virtualization overhead %", "lnsGauge", esql_state_gauge(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Overhead %` = AVG(`sqlserver.spotlight.virtualization.overhead_pct`)"),
        "Overhead %"))

    cpu_g = create_lens("CPU usage %", "lnsGauge", esql_state_gauge(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `CPU %` = MAX(`sqlserver.spotlight.cpu.usage`)"),
        "CPU %"))

    mem_total = create_lens("Server memory (bytes)", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Total bytes` = MAX(`sqlserver.spotlight.memory.server.total.bytes`)"),
        "Total bytes"))
    mem_buf = create_lens("Buffer cache (bytes)", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Buffer cache` = MAX(`sqlserver.spotlight.memory.buffer_cache.bytes`)"),
        "Buffer cache"))
    mem_ple = create_lens("Page life expectancy (s)", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `PLE (s)` = MAX(`sqlserver.spotlight.memory.page_life_expectancy.seconds`)"),
        "PLE (s)"))
    mem_proc = create_lens("Procedure cache (bytes)", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Proc cache` = MAX(`sqlserver.spotlight.memory.procedure_cache.bytes`)"),
        "Proc cache"))

    bg_err = create_lens("Error log events/min", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Error log/min` = AVG(`sqlserver.spotlight.background.errorlog.events_per_min`)"),
        "Error log/min"))
    bg_svc = create_lens("Services running", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Services` = MAX(`sqlserver.spotlight.services.running`)"),
        "Services"))

    buf_hit = create_lens("Buffer cache hit ratio (receiver)", "lnsMetric", esql_state_metric(
        w(f"FROM {IDX} | WHERE __FILTER__ | STATS `Hit %` = AVG(`sqlserver.page.buffer_cache.hit_ratio`)"),
        "Hit %"))

    return create_dashboard(
        "Spotlight \u2014 SQL Server Overview (synthetic)",
        "Widgets aligned to Quest Spotlight SQL Server Overview using custom sqlserver.spotlight.* gauges; "
        "filtered to host mssql-prod-01. See assets/spotlight-otel-gaps.md for OTel coverage notes.",
        [
            (sess_rt,   (0,   0, 8, 5), "Response time (ms)"),
            (sess_ct,   (8,   0, 8, 5), "Active sessions"),
            (sess_max,  (16,  0, 8, 5), "Max sessions"),
            (computers, (24,  0, 8, 5), "Computers"),
            (sess_bar,  (32,  0, 16, 5), "Active sessions %"),
            (perf_g,    (0,   5, 12, 8), "Performance health (gauge)"),
            (sys_tbl,   (12,  5, 36, 8), "System + health table"),
            (pr_tot,    (0,   13, 8, 5), "Processes total"),
            (pr_sys,    (8,   13, 8, 5), "System procs"),
            (pr_usr,    (16,  13, 8, 5), "User procs"),
            (pr_blk,    (24,  13, 8, 5), "Blocked"),
            (batches,   (32,  13, 16, 5), "Batch requests (counter)"),
            (virt_g,    (0,   18, 12, 8), "Virtualization overhead"),
            (cpu_g,     (12,  18, 12, 8), "CPU usage"),
            (buf_hit,   (24,  18, 24, 8), "Buffer cache hit %"),
            (mem_total, (0,   26, 12, 5), "Memory total"),
            (mem_buf,   (12,  26, 12, 5), "Buffer cache size"),
            (mem_ple,   (24,  26, 12, 5), "Page life expectancy"),
            (mem_proc,  (36,  26, 12, 5), "Procedure cache"),
            (bg_err,    (0,   31, 12, 5), "Error log rate"),
            (bg_svc,    (12,  31, 12, 5), "SQL services running"),
        ],
    )


def build_oracle():
    print("  Creating Oracle Lens panels...")
    IDX = "metrics-oracledbreceiver.otel.otel-default"

    kpi_sess = create_lens("Active Sessions", "lnsMetric", esql_state_metric(
        f"FROM {IDX} | WHERE session.type == \"active\" | STATS `Active Sessions` = MAX(`oracledb.sessions.current`)",
        "Active Sessions"))
    kpi_proc = create_lens("Processes", "lnsMetric", esql_state_metric(
        f"FROM {IDX} | STATS `Processes` = MAX(`oracledb.processes.count`)",
        "Processes"))
    kpi_phys = create_lens("Physical Reads", "lnsMetric", esql_state_metric(
        f"FROM {IDX} | EVAL _p = TO_DOUBLE(`oracledb.physical_reads`) | STATS `Physical Reads` = MAX(_p)",
        "Physical Reads"))
    kpi_comm = create_lens("User Commits", "lnsMetric", esql_state_metric(
        f"FROM {IDX} | EVAL _c = TO_DOUBLE(`oracledb.user_commits`) | STATS `User Commits` = MAX(_c)",
        "User Commits"))

    sess_t = create_lens("Sessions Over Time (Active vs Inactive)", "lnsXY", esql_state_xy(
        f"FROM {IDX} | STATS sessions = AVG(`oracledb.sessions.current`) BY bucket = BUCKET(@timestamp, 5 minute), `session.type` | WHERE `session.type` IS NOT NULL",
        "area_stacked", "bucket", ["sessions"], "session.type"))

    ts_bar = create_lens("Tablespace Utilisation (Used GB)", "lnsXY", esql_state_xy(
        f"FROM {IDX} | WHERE `oracledb.tablespace.used` IS NOT NULL | STATS used_gb = ROUND(MAX(`oracledb.tablespace.used`) / 1073741824.0, 2), total_gb = ROUND(MAX(`oracledb.tablespace.size`) / 1073741824.0, 2) BY `tablespace_name` | WHERE `tablespace_name` IS NOT NULL | SORT used_gb DESC | LIMIT 10",
        "bar_horizontal", "tablespace_name", ["used_gb", "total_gb"], x_type="string"))

    reads_t = create_lens("Physical vs Logical Reads Over Time", "lnsXY", esql_state_xy(
        f"FROM {IDX} | EVAL _p = TO_DOUBLE(`oracledb.physical_reads`), _l = TO_DOUBLE(`oracledb.logical_reads`) | STATS physical = MAX(_p), logical = MAX(_l) BY bucket = BUCKET(@timestamp, 5 minute), `service.name`",
        "line", "bucket", ["physical", "logical"], "service.name"))

    parse_t = create_lens("Hard vs Total Parses Over Time", "lnsXY", esql_state_xy(
        f"FROM {IDX} | EVAL _h = TO_DOUBLE(`oracledb.hard_parses`), _t = TO_DOUBLE(`oracledb.parse_calls`) | STATS hard = MAX(_h), total = MAX(_t) BY bucket = BUCKET(@timestamp, 5 minute)",
        "line", "bucket", ["hard", "total"]))

    txn_t = create_lens("Active Transactions Over Time", "lnsXY", esql_state_xy(
        f"FROM {IDX} | STATS txns = AVG(`oracledb.transactions`) BY bucket = BUCKET(@timestamp, 5 minute), `service.name`",
        "area", "bucket", ["txns"], "service.name"))

    pga_t = create_lens("PGA Memory (GB) Over Time", "lnsXY", esql_state_xy(
        f"FROM {IDX} | STATS pga_gb = ROUND(AVG(`oracledb.pga_memory`) / 1073741824.0, 2) BY bucket = BUCKET(@timestamp, 5 minute), `service.name`",
        "line", "bucket", ["pga_gb"], "service.name"))

    return create_dashboard(
        "Oracle \u2014 Performance & Health",
        "Sessions, tablespace utilisation, parse efficiency, reads, transactions and PGA memory via OpenTelemetry",
        [
            (kpi_sess, (0,  0, 12, 5), "Active Sessions"),
            (kpi_proc, (12, 0, 12, 5), "Processes"),
            (kpi_phys, (24, 0, 12, 5), "Physical Reads"),
            (kpi_comm, (36, 0, 12, 5), "User Commits"),
            (sess_t,   (0,  5, 24, 11), "Sessions Over Time"),
            (ts_bar,   (24, 5, 24, 11), "Tablespace Utilisation"),
            (reads_t,  (0,  16, 24, 11), "Physical vs Logical Reads"),
            (parse_t,  (24, 16, 24, 11), "Parse Rate"),
            (txn_t,    (0,  27, 24, 11), "Active Transactions"),
            (pga_t,    (24, 27, 24, 11), "PGA Memory"),
        ])


if __name__ == "__main__":
    dashboards = [
        ("MySQL \u2014 Slow Query & Error Monitoring", build_mysql),
        ("PostgreSQL \u2014 Performance & Health",    build_postgres),
        ("SQL Server \u2014 Performance & Health",    build_mssql),
        ("SQL Server \u2014 Overview (Datadog Equivalent)", build_mssql_overview),
        ("Spotlight \u2014 Health Heat Map (SQL Server, Windows, MongoDB)", build_spotlight_heatmap),
        ("Spotlight \u2014 SQL Server Overview (synthetic)", build_spotlight_sql_overview),
        ("MongoDB \u2014 Operations & Health",        build_mongodb),
        ("Oracle \u2014 Performance & Health",        build_oracle),
    ]
    ids = []
    for name, builder in dashboards:
        print(f"\nDeploying: {name}")
        dash_id = builder()
        ids.append((name, dash_id))
        print(f"  ✓ Dashboard ID: {dash_id}")

    print(f"\n{'='*60}")
    print("All dashboards created successfully!")
    print(f"{'='*60}")
    for name, dash_id in ids:
        print(f"  {name}")
        print(f"    {KIBANA_URL}/app/dashboards#/view/{dash_id}")
    print(f"\nDashboard list: {KIBANA_URL}/app/dashboards")
