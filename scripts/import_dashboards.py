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
        "FROM metrics-postgresqlreceiver.otel.otel-default | STATS backends = AVG(`postgresql.backends`) BY bucket = BUCKET(@timestamp, 1 hour), `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
        "area_stacked", "bucket", ["backends"], "postgresql.database.name"))
    size_b = create_lens("Database Size by Database", "lnsXY", esql_state_xy(
        "FROM metrics-postgresqlreceiver.otel.otel-default | STATS db_size = MAX(`postgresql.db_size`) BY `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL | SORT db_size DESC | LIMIT 10",
        "bar_horizontal", "postgresql.database.name", ["db_size"], x_type="string"))
    deadlocks = create_lens("Deadlocks Over Time by Database", "lnsXY", esql_state_xy(
        "FROM metrics-postgresqlreceiver.otel.otel-default | EVAL _dl = TO_DOUBLE(`postgresql.deadlocks`) | STATS deadlocks = MAX(_dl) BY bucket = BUCKET(@timestamp, 1 hour), `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
        "bar_stacked", "bucket", ["deadlocks"], "postgresql.database.name"))
    rows = create_lens("Rows Inserted / Updated / Deleted", "lnsXY", esql_state_xy(
        "FROM metrics-postgresqlreceiver.otel.otel-default | EVAL _ins = TO_DOUBLE(`postgresql.tup_inserted`), _upd = TO_DOUBLE(`postgresql.tup_updated`), _del = TO_DOUBLE(`postgresql.tup_deleted`) | STATS inserted = MAX(_ins), updated = MAX(_upd), deleted = MAX(_del) BY bucket = BUCKET(@timestamp, 1 hour)",
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
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS connections = AVG(`sqlserver.user.connection.count`) BY bucket = BUCKET(@timestamp, 1 hour), `service.name`",
        "area", "bucket", ["connections"], "service.name"))
    lock_t    = create_lens("Lock Wait Time (ms) Over Time", "lnsXY", esql_state_xy(
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS lock_wait = AVG(`sqlserver.lock.wait_time.avg`) BY bucket = BUCKET(@timestamp, 1 hour), `service.name`",
        "line", "bucket", ["lock_wait"], "service.name"))
    io_lat    = create_lens("I/O Read vs Write Latency by Database", "lnsXY", esql_state_xy(
        "FROM metrics-sqlserverreceiver.otel.otel-default | STATS read_lat = AVG(`sqlserver.database.io.read_latency`), write_lat = AVG(`sqlserver.database.io.write_latency`) BY `sqlserver.database.name` | WHERE `sqlserver.database.name` IS NOT NULL | SORT read_lat DESC | LIMIT 10",
        "bar", "sqlserver.database.name", ["read_lat", "write_lat"], x_type="string"))
    batches   = create_lens("Batch Requests Over Time", "lnsXY", esql_state_xy(
        "FROM metrics-sqlserverreceiver.otel.otel-default | EVAL _b = TO_DOUBLE(`sqlserver.batch_sql_request.count`) | STATS batches = MAX(_b) BY bucket = BUCKET(@timestamp, 1 hour), `service.name`",
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
        "FROM metrics-mongodbatlas.otel.otel-default | EVAL _ops = TO_DOUBLE(`mongodb.operation.count`) | STATS ops = MAX(_ops) BY bucket = BUCKET(@timestamp, 1 hour), `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
        "area_stacked", "bucket", ["ops"], "mongodb.operation.type"))
    conn_t   = create_lens("Connections by Instance", "lnsXY", esql_state_xy(
        "FROM metrics-mongodbatlas.otel.otel-default | STATS conns = AVG(`mongodb.connection.count`) BY bucket = BUCKET(@timestamp, 1 hour), `service.name`",
        "line", "bucket", ["conns"], "service.name"))
    mem_t    = create_lens("Memory: Resident vs Virtual (GB)", "lnsXY", esql_state_xy(
        "FROM metrics-mongodbatlas.otel.otel-default | EVAL _res = `mongodb.memory.usage` / 1073741824.0, _virt = `mongodb.memory.virtual` / 1073741824.0 | STATS resident = ROUND(AVG(_res), 2), virtual = ROUND(AVG(_virt), 2) BY bucket = BUCKET(@timestamp, 1 hour)",
        "area", "bucket", ["resident", "virtual"]))
    docs     = create_lens("Document Operations Over Time", "lnsXY", esql_state_xy(
        "FROM metrics-mongodbatlas.otel.otel-default | EVAL _docs = TO_DOUBLE(`mongodb.document.operation.count`) | STATS docs = MAX(_docs) BY bucket = BUCKET(@timestamp, 1 hour), `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
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


if __name__ == "__main__":
    dashboards = [
        ("MySQL \u2014 Slow Query & Error Monitoring", build_mysql),
        ("PostgreSQL \u2014 Performance & Health",    build_postgres),
        ("SQL Server \u2014 Performance & Health",    build_mssql),
        ("MongoDB \u2014 Operations & Health",        build_mongodb),
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
