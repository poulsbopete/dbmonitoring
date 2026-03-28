#!/usr/bin/env python3
"""
Import DB monitoring dashboards into Kibana using the Saved Objects _import API.
Uses full Kibana internal Lens format — works on all Kibana versions without feature flags.

Usage:
  python3 scripts/import_dashboards.py
  KIBANA_URL=https://... ES_API_KEY=... python3 scripts/import_dashboards.py
"""
import json
import os
import sys
import uuid
import urllib.request
import urllib.error
import io

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
API_KEY = os.environ.get("ES_API_KEY", "") or os.environ.get("KIBANA_API_KEY", "")
ES_PASSWORD = os.environ.get("ES_PASSWORD", "") or os.environ.get("ELASTICSEARCH_PASSWORD", "")
ES_USERNAME = os.environ.get("ES_USERNAME", "admin")

if not KIBANA_URL:
    print("ERROR: KIBANA_URL not set", file=sys.stderr)
    sys.exit(1)
if not API_KEY and not ES_PASSWORD:
    print("ERROR: ES_API_KEY or ES_PASSWORD not set", file=sys.stderr)
    sys.exit(1)


def gid():
    return str(uuid.uuid4())


def auth_header():
    if API_KEY:
        return f"ApiKey {API_KEY}"
    import base64
    creds = base64.b64encode(f"{ES_USERNAME}:{ES_PASSWORD}".encode()).decode()
    return f"Basic {creds}"


# ---------------------------------------------------------------------------
# Lens object builders
# ---------------------------------------------------------------------------

def metric_lens(title, esql_query, col_name):
    """Single-value metric panel."""
    layer_id = gid()
    col_id = gid()
    index = esql_query.split("FROM")[1].split("|")[0].strip()
    return {
        "type": "lens",
        "id": gid(),
        "attributes": {
            "title": title,
            "visualizationType": "lnsMetric",
            "state": {
                "visualization": {
                    "layerId": layer_id,
                    "layerType": "data",
                    "metricAccessor": col_id,
                },
                "query": {"language": "kuery", "query": ""},
                "filters": [],
                "datasourceStates": {
                    "textBased": {
                        "layers": {
                            layer_id: {
                                "query": {"esql": esql_query},
                                "index": index,
                                "columns": [
                                    {"columnId": col_id, "fieldName": col_name, "meta": {"type": "number"}}
                                ],
                            }
                        }
                    }
                },
            },
        },
        "references": [],
    }


def xy_lens(title, esql_query, series_type, x_col, y_cols, breakdown_col=None, x_type="date"):
    """XY chart panel (line, bar, area variants)."""
    layer_id = gid()
    x_col_id = gid()
    y_col_ids = [gid() for _ in y_cols]
    bd_col_id = gid() if breakdown_col else None
    index = esql_query.split("FROM")[1].split("|")[0].strip()

    columns = [{"columnId": x_col_id, "fieldName": x_col, "meta": {"type": x_type}}]
    for i, y in enumerate(y_cols):
        columns.append({"columnId": y_col_ids[i], "fieldName": y, "meta": {"type": "number"}})
    if breakdown_col:
        columns.append({"columnId": bd_col_id, "fieldName": breakdown_col, "meta": {"type": "string"}})

    layer = {
        "layerId": layer_id,
        "layerType": "data",
        "seriesType": series_type,
        "xAccessor": x_col_id,
        "accessors": y_col_ids,
    }
    if breakdown_col:
        layer["splitAccessor"] = bd_col_id

    return {
        "type": "lens",
        "id": gid(),
        "attributes": {
            "title": title,
            "visualizationType": "lnsXY",
            "state": {
                "visualization": {
                    "legend": {"isVisible": True, "position": "right"},
                    "valueLabels": "hide",
                    "preferredSeriesType": series_type,
                    "layers": [layer],
                },
                "query": {"language": "kuery", "query": ""},
                "filters": [],
                "datasourceStates": {
                    "textBased": {
                        "layers": {
                            layer_id: {
                                "query": {"esql": esql_query},
                                "index": index,
                                "columns": columns,
                            }
                        }
                    }
                },
            },
        },
        "references": [],
    }


def dashboard_obj(title, description, panels_grids, time_from="now-7d", time_to="now"):
    """
    panels_grids: list of (lens_obj, (x, y, w, h))
    Returns (dashboard_saved_object, [lens_saved_objects])
    """
    panels_json = []
    references = []

    for lens_obj, (x, y, w, h) in panels_grids:
        panel_id = gid()
        panels_json.append({
            "version": "9.4.0",
            "type": "lens",
            "gridData": {"x": x, "y": y, "w": w, "h": h, "i": panel_id},
            "panelIndex": panel_id,
            "embeddableConfig": {"enhancements": {}},
            "title": lens_obj["attributes"]["title"],
            "panelRefName": f"panel_{panel_id}",
        })
        references.append({"name": f"panel_{panel_id}", "type": "lens", "id": lens_obj["id"]})

    dash = {
        "type": "dashboard",
        "id": gid(),
        "attributes": {
            "title": title,
            "description": description,
            "panelsJSON": json.dumps(panels_json),
            "optionsJSON": json.dumps({
                "useMargins": True,
                "syncColors": False,
                "syncCursor": True,
                "syncTooltips": False,
                "hidePanelTitles": False,
            }),
            "version": 1,
            "timeRestore": True,
            "timeTo": time_to,
            "timeFrom": time_from,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({"query": {"language": "kuery", "query": ""}, "filter": []})
            },
        },
        "references": references,
    }
    lens_objects = [lo for lo, _ in panels_grids]
    return dash, lens_objects


# ---------------------------------------------------------------------------
# Dashboard definitions
# ---------------------------------------------------------------------------

def build_mysql():
    kpi_slow = metric_lens(
        "Total Slow Queries",
        "FROM logs-mysql.slowlog.otel-default | STATS `Total Slow Queries` = COUNT(*)",
        "Total Slow Queries",
    )
    kpi_avg = metric_lens(
        "Avg Query Time (s)",
        "FROM logs-mysql.slowlog.otel-default | STATS `Avg Query Time (s)` = AVG(`mysql.slowlog.query_time`)",
        "Avg Query Time (s)",
    )
    kpi_max = metric_lens(
        "Max Query Time (s)",
        "FROM logs-mysql.slowlog.otel-default | STATS `Max Query Time (s)` = MAX(`mysql.slowlog.query_time`)",
        "Max Query Time (s)",
    )
    kpi_err = metric_lens(
        "DB Errors",
        "FROM logs-mysql.error.otel-default | STATS `DB Errors` = COUNT(*)",
        "DB Errors",
    )
    slow_rate = xy_lens(
        "Slow Query Rate by Database",
        "FROM logs-mysql.slowlog.otel-default | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `db.name`",
        "area_stacked", "bucket", ["count"], "db.name",
    )
    query_time = xy_lens(
        "Avg Query Time by Database (s)",
        "FROM logs-mysql.slowlog.otel-default | STATS avg_time = AVG(`mysql.slowlog.query_time`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `db.name`",
        "line", "bucket", ["avg_time"], "db.name",
    )
    top_tables = xy_lens(
        "Top Tables by Slow Query Count",
        "FROM logs-mysql.slowlog.otel-default | STATS count = COUNT(*) BY `db.sql.table` | SORT count DESC | LIMIT 15",
        "bar_horizontal", "db.sql.table", ["count"], x_type="string",
    )
    lock_vs_query = xy_lens(
        "Avg Query vs Lock Time by Database",
        "FROM logs-mysql.slowlog.otel-default | STATS avg_query = AVG(`mysql.slowlog.query_time`), avg_lock = AVG(`mysql.slowlog.lock_time`) BY `db.name`",
        "bar", "db.name", ["avg_query", "avg_lock"], x_type="string",
    )
    error_trend = xy_lens(
        "Error Log Trend",
        "FROM logs-mysql.error.otel-default | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `log.level`",
        "bar_stacked", "bucket", ["count"], "log.level",
    )

    panels = [
        (kpi_slow,      (0,  0, 12, 5)),
        (kpi_avg,       (12, 0, 12, 5)),
        (kpi_max,       (24, 0, 12, 5)),
        (kpi_err,       (36, 0, 12, 5)),
        (slow_rate,     (0,  5, 24, 11)),
        (query_time,    (24, 5, 24, 11)),
        (top_tables,    (0,  16, 24, 11)),
        (lock_vs_query, (24, 16, 24, 11)),
        (error_trend,   (0,  27, 48, 11)),
    ]
    return dashboard_obj(
        "MySQL \u2014 Slow Query & Error Monitoring",
        "Slow queries, lock contention, error trends, and top tables via OpenTelemetry",
        panels,
    )


def build_postgres():
    kpi_conn = metric_lens(
        "Active Connections",
        "FROM metrics-postgresqlreceiver.otel-default | STATS `Active Connections` = MAX(`postgresql.backends`)",
        "Active Connections",
    )
    kpi_dead = metric_lens(
        "Total Deadlocks",
        "FROM metrics-postgresqlreceiver.otel-default | STATS `Total Deadlocks` = MAX(`postgresql.deadlocks`)",
        "Total Deadlocks",
    )
    kpi_size = metric_lens(
        "Max DB Size (bytes)",
        "FROM metrics-postgresqlreceiver.otel-default | STATS `Max DB Size` = MAX(`postgresql.db_size`)",
        "Max DB Size",
    )
    kpi_max_conn = metric_lens(
        "Connection Limit",
        "FROM metrics-postgresqlreceiver.otel-default | STATS `Connection Limit` = MAX(`postgresql.connection.max`)",
        "Connection Limit",
    )
    conn_trend = xy_lens(
        "Active Connections Over Time",
        "FROM metrics-postgresqlreceiver.otel-default | STATS backends = AVG(`postgresql.backends`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
        "area_stacked", "bucket", ["backends"], "postgresql.database.name",
    )
    size_bars = xy_lens(
        "Database Size by Database",
        "FROM metrics-postgresqlreceiver.otel-default | STATS db_size = MAX(`postgresql.db_size`) BY `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL | SORT db_size DESC | LIMIT 10",
        "bar_horizontal", "postgresql.database.name", ["db_size"], x_type="string",
    )
    deadlocks = xy_lens(
        "Deadlocks Over Time by Database",
        "FROM metrics-postgresqlreceiver.otel-default | STATS deadlocks = MAX(`postgresql.deadlocks`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
        "bar_stacked", "bucket", ["deadlocks"], "postgresql.database.name",
    )
    rows = xy_lens(
        "Rows Inserted / Updated / Deleted",
        "FROM metrics-postgresqlreceiver.otel-default | STATS inserted = MAX(`postgresql.tup_inserted`), updated = MAX(`postgresql.tup_updated`), deleted = MAX(`postgresql.tup_deleted`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend)",
        "line", "bucket", ["inserted", "updated", "deleted"],
    )

    panels = [
        (kpi_conn,      (0,  0, 12, 5)),
        (kpi_dead,      (12, 0, 12, 5)),
        (kpi_size,      (24, 0, 12, 5)),
        (kpi_max_conn,  (36, 0, 12, 5)),
        (conn_trend,    (0,  5, 24, 11)),
        (size_bars,     (24, 5, 24, 11)),
        (deadlocks,     (0,  16, 24, 11)),
        (rows,          (24, 16, 24, 11)),
    ]
    return dashboard_obj(
        "PostgreSQL \u2014 Performance & Health",
        "Connections, deadlocks, database size, and row operations via OpenTelemetry",
        panels,
    )


def build_mssql():
    kpi_conn = metric_lens(
        "User Connections",
        "FROM metrics-sqlserverreceiver.otel-default | STATS `User Connections` = MAX(`sqlserver.user.connection.count`)",
        "User Connections",
    )
    kpi_cache = metric_lens(
        "Buffer Cache Hit %",
        "FROM metrics-sqlserverreceiver.otel-default | STATS `Buffer Cache Hit %` = AVG(`sqlserver.page.buffer_cache.hit_ratio`)",
        "Buffer Cache Hit %",
    )
    kpi_lock = metric_lens(
        "Avg Lock Wait (ms)",
        "FROM metrics-sqlserverreceiver.otel-default | STATS `Avg Lock Wait (ms)` = AVG(`sqlserver.lock.wait_time.avg`)",
        "Avg Lock Wait (ms)",
    )
    kpi_dead = metric_lens(
        "Total Deadlocks",
        "FROM metrics-sqlserverreceiver.otel-default | STATS `Total Deadlocks` = MAX(`sqlserver.deadlock.count`)",
        "Total Deadlocks",
    )
    conn_trend = xy_lens(
        "User Connections Over Time",
        "FROM metrics-sqlserverreceiver.otel-default | STATS connections = AVG(`sqlserver.user.connection.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `service.name`",
        "area", "bucket", ["connections"], "service.name",
    )
    lock_trend = xy_lens(
        "Lock Wait Time (ms) Over Time",
        "FROM metrics-sqlserverreceiver.otel-default | STATS lock_wait = AVG(`sqlserver.lock.wait_time.avg`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `service.name`",
        "line", "bucket", ["lock_wait"], "service.name",
    )
    io_lat = xy_lens(
        "I/O Read vs Write Latency by Database (ms)",
        "FROM metrics-sqlserverreceiver.otel-default | STATS read_lat = AVG(`sqlserver.database.io.read_latency`), write_lat = AVG(`sqlserver.database.io.write_latency`) BY `sqlserver.database.name` | WHERE `sqlserver.database.name` IS NOT NULL | SORT read_lat DESC | LIMIT 10",
        "bar", "sqlserver.database.name", ["read_lat", "write_lat"], x_type="string",
    )
    batches = xy_lens(
        "Batch Requests Over Time",
        "FROM metrics-sqlserverreceiver.otel-default | STATS batches = MAX(`sqlserver.batch_sql_request.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `service.name`",
        "line", "bucket", ["batches"], "service.name",
    )

    panels = [
        (kpi_conn,   (0,  0, 12, 5)),
        (kpi_cache,  (12, 0, 12, 5)),
        (kpi_lock,   (24, 0, 12, 5)),
        (kpi_dead,   (36, 0, 12, 5)),
        (conn_trend, (0,  5, 24, 11)),
        (lock_trend, (24, 5, 24, 11)),
        (io_lat,     (0,  16, 24, 11)),
        (batches,    (24, 16, 24, 11)),
    ]
    return dashboard_obj(
        "SQL Server \u2014 Performance & Health",
        "Connections, lock waits, batch requests, buffer cache, and I/O latency via OpenTelemetry",
        panels,
    )


def build_mongodb():
    kpi_conn = metric_lens(
        "Active Connections",
        "FROM metrics-mongodbatlas.otel-default | STATS `Active Connections` = MAX(`mongodb.connection.count`)",
        "Active Connections",
    )
    kpi_mem = metric_lens(
        "Memory Usage (bytes)",
        "FROM metrics-mongodbatlas.otel-default | STATS `Memory Usage` = MAX(`mongodb.memory.usage`)",
        "Memory Usage",
    )
    kpi_ops = metric_lens(
        "Total Operations",
        "FROM metrics-mongodbatlas.otel-default | STATS `Total Operations` = MAX(`mongodb.operation.count`)",
        "Total Operations",
    )
    kpi_repl = metric_lens(
        "Replication Lag (s)",
        "FROM metrics-mongodbatlas.otel-default | STATS `Replication Lag (s)` = AVG(`mongodb.replication.lag`)",
        "Replication Lag (s)",
    )
    ops_trend = xy_lens(
        "Operations Over Time by Type",
        "FROM metrics-mongodbatlas.otel-default | STATS ops = MAX(`mongodb.operation.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
        "area_stacked", "bucket", ["ops"], "mongodb.operation.type",
    )
    conn_trend = xy_lens(
        "Connections by Instance",
        "FROM metrics-mongodbatlas.otel-default | STATS conns = AVG(`mongodb.connection.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `service.name`",
        "line", "bucket", ["conns"], "service.name",
    )
    mem_trend = xy_lens(
        "Memory: Resident vs Virtual (bytes)",
        "FROM metrics-mongodbatlas.otel-default | STATS resident = AVG(`mongodb.memory.usage`), virtual = AVG(`mongodb.memory.virtual`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend)",
        "area", "bucket", ["resident", "virtual"],
    )
    docs = xy_lens(
        "Document Operations Over Time",
        "FROM metrics-mongodbatlas.otel-default | STATS docs = MAX(`mongodb.document.operation.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
        "line", "bucket", ["docs"], "mongodb.operation.type",
    )

    panels = [
        (kpi_conn,   (0,  0, 12, 5)),
        (kpi_mem,    (12, 0, 12, 5)),
        (kpi_ops,    (24, 0, 12, 5)),
        (kpi_repl,   (36, 0, 12, 5)),
        (ops_trend,  (0,  5, 24, 11)),
        (conn_trend, (24, 5, 24, 11)),
        (mem_trend,  (0,  16, 24, 11)),
        (docs,       (24, 16, 24, 11)),
    ]
    return dashboard_obj(
        "MongoDB \u2014 Operations & Health",
        "Operation throughput, connections, memory, replication lag, and document stats via OpenTelemetry",
        panels,
    )


# ---------------------------------------------------------------------------
# Import via Saved Objects _import API
# ---------------------------------------------------------------------------

def import_objects(objects):
    """POST to /api/saved_objects/_import as multipart/form-data NDJSON."""
    ndjson = "\n".join(json.dumps(o) for o in objects).encode("utf-8")

    boundary = "----KibanaDashboardImport"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="dashboards.ndjson"\r\n'
        f"Content-Type: application/ndjson\r\n\r\n"
    ).encode("utf-8") + ndjson + f"\r\n--{boundary}--\r\n".encode("utf-8")

    url = f"{KIBANA_URL}/api/saved_objects/_import?overwrite=true"
    headers = {
        "Authorization": auth_header(),
        "kbn-xsrf": "true",
        "x-elastic-internal-origin": "kibana",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    builders = [
        ("MySQL \u2014 Slow Query & Error Monitoring", build_mysql),
        ("PostgreSQL \u2014 Performance & Health", build_postgres),
        ("SQL Server \u2014 Performance & Health", build_mssql),
        ("MongoDB \u2014 Operations & Health", build_mongodb),
    ]

    all_objects = []
    for name, builder in builders:
        dash, lenses = builder()
        all_objects.extend(lenses)
        all_objects.append(dash)

    print(f"Importing {len(all_objects)} saved objects ({len(builders)} dashboards + Lens panels)...")
    result = import_objects(all_objects)

    if result.get("success"):
        created = result.get("successCount", 0)
        print(f"✓ Import successful — {created} objects created")
        for b in builders:
            print(f"  • {b[0]}")
        print(f"\nDashboards: {KIBANA_URL}/app/dashboards")
    else:
        errors = result.get("errors", [])
        print(f"✗ Import failed with {len(errors)} error(s):", file=sys.stderr)
        for e in errors[:5]:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
