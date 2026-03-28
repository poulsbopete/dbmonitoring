#!/usr/bin/env python3
"""
Deploy DB monitoring dashboards to Kibana via the Saved Objects API.
Works with all Kibana versions (does not require the 9.4+ as-code API).

Usage:
  source ~/.bashrc
  python3 tools/deploy_dashboards.py
"""
import json
import os
import sys
import requests

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY  = os.environ.get("ES_API_KEY", "")

if not KIBANA_URL or not ES_API_KEY:
    print("ERROR: KIBANA_URL and ES_API_KEY must be set in the environment.")
    sys.exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "kbn-xsrf": "true",
    "Authorization": f"ApiKey {ES_API_KEY}",
}

# ── panel builders ────────────────────────────────────────────────────────────

def _layer_cols(x_col, y_cols, split_col=None):
    cols = [{"columnId": "cx", "fieldName": x_col}]
    for i, c in enumerate(y_cols):
        cols.append({"columnId": f"cy{i}", "fieldName": c})
    if split_col:
        cols.append({"columnId": "cs", "fieldName": split_col})
    return cols


def metric_panel(uid, x, y, w, h, esql, col_name):
    """Single-value metric panel backed by ES|QL."""
    return {
        "type": "lens",
        "panelIndex": uid,
        "gridData": {"x": x, "y": y, "w": w, "h": h, "i": uid},
        "embeddableConfig": {
            "attributes": {
                "title": "",
                "visualizationType": "lnsMetric",
                "type": "lens",
                "references": [],
                "state": {
                    "visualization": {
                        "layerId": "l1",
                        "layerType": "data",
                        "metricAccessor": "c0",
                    },
                    "query": {"language": "kuery", "query": ""},
                    "filters": [],
                    "datasourceStates": {
                        "textBased": {
                            "layers": {
                                "l1": {
                                    "columns": [{"columnId": "c0", "fieldName": col_name}],
                                    "allColumns": [{"columnId": "c0", "fieldName": col_name}],
                                    "query": {"esql": esql},
                                    "index": esql,
                                }
                            }
                        }
                    },
                    "adHocDataViews": {},
                },
            },
            "enhancements": {},
        },
    }


def xy_panel(uid, x, y, w, h, title, series_type, esql, x_col, y_cols, split_col=None):
    """XY chart (line / area / bar) backed by ES|QL."""
    cols = _layer_cols(x_col, y_cols, split_col)
    layer = {
        "layerId": "l1",
        "seriesType": series_type,
        "xAccessor": "cx",
        "accessors": [f"cy{i}" for i in range(len(y_cols))],
        "layerType": "data",
    }
    if split_col:
        layer["splitAccessor"] = "cs"

    return {
        "type": "lens",
        "panelIndex": uid,
        "title": title,
        "gridData": {"x": x, "y": y, "w": w, "h": h, "i": uid},
        "embeddableConfig": {
            "attributes": {
                "title": title,
                "visualizationType": "lnsXY",
                "type": "lens",
                "references": [],
                "state": {
                    "visualization": {
                        "legend": {"isVisible": True, "position": "right"},
                        "valueLabels": "hide",
                        "layers": [layer],
                    },
                    "query": {"language": "kuery", "query": ""},
                    "filters": [],
                    "datasourceStates": {
                        "textBased": {
                            "layers": {
                                "l1": {
                                    "columns": cols,
                                    "allColumns": cols,
                                    "query": {"esql": esql},
                                    "index": esql,
                                }
                            }
                        }
                    },
                    "adHocDataViews": {},
                },
            },
            "enhancements": {},
        },
    }


def table_panel(uid, x, y, w, h, title, esql, all_cols):
    """Datatable panel backed by ES|QL. all_cols is list of field names."""
    def safe_id(name):
        return name.replace(".", "_").replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct")

    cols = [{"columnId": safe_id(c), "fieldName": c} for c in all_cols]
    return {
        "type": "lens",
        "panelIndex": uid,
        "title": title,
        "gridData": {"x": x, "y": y, "w": w, "h": h, "i": uid},
        "embeddableConfig": {
            "attributes": {
                "title": title,
                "visualizationType": "lnsDatatable",
                "type": "lens",
                "references": [],
                "state": {
                    "visualization": {
                        "layerId": "l1",
                        "layerType": "data",
                        "columns": [{"columnId": safe_id(c)} for c in all_cols],
                    },
                    "query": {"language": "kuery", "query": ""},
                    "filters": [],
                    "datasourceStates": {
                        "textBased": {
                            "layers": {
                                "l1": {
                                    "columns": cols,
                                    "allColumns": cols,
                                    "query": {"esql": esql},
                                    "index": esql,
                                }
                            }
                        }
                    },
                    "adHocDataViews": {},
                },
            },
            "enhancements": {},
        },
    }


# ── saved-object deploy via _import (works on all Kibana Serverless versions) ─

_import_headers = {
    "kbn-xsrf": "true",
    "Authorization": f"ApiKey {ES_API_KEY}",
}

def _slug(title):
    """Generate a stable ID from a title."""
    return title.lower().replace(" ", "-").replace("—", "").replace("&", "").replace("/", "").replace(".", "").replace("  ", "-")[:60].strip("-")


def deploy_dashboard(title, description, panels, time_from="now-7d"):
    dash_id = _slug(title)
    obj = {
        "type": "dashboard",
        "id": dash_id,
        "managed": False,
        "references": [],
        "attributes": {
            "title": title,
            "description": description,
            "panelsJSON": json.dumps(panels),
            "optionsJSON": json.dumps({
                "useMargins": True,
                "syncColors": False,
                "hidePanelTitles": False,
            }),
            "timeRestore": True,
            "timeTo": "now",
            "timeFrom": time_from,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "query": {"language": "kuery", "query": ""},
                    "filter": [],
                })
            },
        },
    }
    ndjson_bytes = (json.dumps(obj) + "\n").encode("utf-8")
    r = requests.post(
        f"{KIBANA_URL}/api/saved_objects/_import?overwrite=true",
        headers=_import_headers,
        files={"file": ("export.ndjson", ndjson_bytes, "application/ndjson")},
        timeout=30,
    )
    data = r.json()
    if r.status_code == 200 and data.get("success"):
        print(f"  ✓  {title} (id={dash_id})")
        return dash_id
    else:
        print(f"  ✗  {title}: HTTP {r.status_code}")
        print(f"     {r.text[:400]}")
        return None


# ── dashboard definitions ─────────────────────────────────────────────────────

def build_mysql():
    panels = [
        metric_panel("m1", 0,  0, 12, 5,
            "FROM logs-mysql.slowlog.otel-default | STATS `Total Slow Queries` = COUNT(*)",
            "Total Slow Queries"),
        metric_panel("m2", 12, 0, 12, 5,
            "FROM logs-mysql.slowlog.otel-default | STATS `Avg Query Time (s)` = AVG(`mysql.slowlog.query_time`)",
            "Avg Query Time (s)"),
        metric_panel("m3", 24, 0, 12, 5,
            "FROM logs-mysql.slowlog.otel-default | STATS `Max Query Time (s)` = MAX(`mysql.slowlog.query_time`)",
            "Max Query Time (s)"),
        metric_panel("m4", 36, 0, 12, 5,
            "FROM logs-mysql.error.otel-default | STATS `DB Errors` = COUNT(*)",
            "DB Errors"),
        xy_panel("c1", 0, 5, 24, 11, "Slow Query Rate by Database", "area_stacked",
            "FROM logs-mysql.slowlog.otel-default | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `db.name`",
            "bucket", ["count"], "db.name"),
        xy_panel("c2", 24, 5, 24, 11, "Avg Query Time by Database (s)", "line",
            "FROM logs-mysql.slowlog.otel-default | STATS avg_time = AVG(`mysql.slowlog.query_time`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `db.name`",
            "bucket", ["avg_time"], "db.name"),
        xy_panel("c3", 0, 16, 24, 11, "Top Tables by Slow Query Count", "bar_horizontal",
            "FROM logs-mysql.slowlog.otel-default | STATS count = COUNT(*) BY `db.sql.table` | SORT count DESC | LIMIT 15",
            "db.sql.table", ["count"]),
        xy_panel("c4", 24, 16, 24, 11, "Avg Query vs Lock Time by Database", "bar",
            "FROM logs-mysql.slowlog.otel-default | STATS avg_query = AVG(`mysql.slowlog.query_time`), avg_lock = AVG(`mysql.slowlog.lock_time`) BY `db.name`",
            "db.name", ["avg_query", "avg_lock"]),
        table_panel("t1", 0, 27, 32, 12, "Slowest Queries by Table",
            "FROM logs-mysql.slowlog.otel-default | STATS count = COUNT(*), avg_time = AVG(`mysql.slowlog.query_time`), max_time = MAX(`mysql.slowlog.query_time`), avg_rows_examined = AVG(`mysql.slowlog.rows_examined`) BY `db.sql.table`, `db.operation`, `db.name` | SORT avg_time DESC | LIMIT 15",
            ["db.sql.table", "db.operation", "db.name", "count", "avg_time", "max_time", "avg_rows_examined"]),
        xy_panel("c5", 32, 27, 16, 12, "Error Log Trend", "bar_stacked",
            "FROM logs-mysql.error.otel-default | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `log.level`",
            "bucket", ["count"], "log.level"),
    ]
    deploy_dashboard(
        "MySQL — Slow Query & Error Monitoring",
        "Slow queries, lock contention, error trends, and top tables via OpenTelemetry",
        panels,
    )


def build_postgres():
    panels = [
        metric_panel("m1", 0,  0, 12, 5,
            "FROM metrics-postgresqlreceiver.otel-default | STATS `Active Connections` = MAX(`postgresql.backends`)",
            "Active Connections"),
        metric_panel("m2", 12, 0, 12, 5,
            "FROM metrics-postgresqlreceiver.otel-default | STATS `Total Deadlocks` = MAX(`postgresql.deadlocks`)",
            "Total Deadlocks"),
        metric_panel("m3", 24, 0, 12, 5,
            "FROM metrics-postgresqlreceiver.otel-default | STATS `Max DB Size` = MAX(`postgresql.db_size`)",
            "Max DB Size"),
        metric_panel("m4", 36, 0, 12, 5,
            "FROM metrics-postgresqlreceiver.otel-default | STATS `Connection Limit` = MAX(`postgresql.connection.max`)",
            "Connection Limit"),
        xy_panel("c1", 0, 5, 24, 11, "Active Connections Over Time", "area_stacked",
            "FROM metrics-postgresqlreceiver.otel-default | STATS backends = AVG(`postgresql.backends`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
            "bucket", ["backends"], "postgresql.database.name"),
        xy_panel("c2", 24, 5, 24, 11, "Database Size by Database", "bar_horizontal",
            "FROM metrics-postgresqlreceiver.otel-default | STATS db_size = MAX(`postgresql.db_size`) BY `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL | SORT db_size DESC | LIMIT 10",
            "postgresql.database.name", ["db_size"]),
        xy_panel("c3", 0, 16, 24, 11, "Rows Inserted / Updated / Deleted", "line",
            "FROM metrics-postgresqlreceiver.otel-default | STATS inserted = MAX(`postgresql.tup_inserted`), updated = MAX(`postgresql.tup_updated`), deleted = MAX(`postgresql.tup_deleted`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend)",
            "bucket", ["inserted", "updated", "deleted"]),
        xy_panel("c4", 24, 16, 24, 11, "Deadlocks Over Time by Database", "bar_stacked",
            "FROM metrics-postgresqlreceiver.otel-default | STATS deadlocks = MAX(`postgresql.deadlocks`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL",
            "bucket", ["deadlocks"], "postgresql.database.name"),
        table_panel("t1", 0, 27, 48, 10, "Database Summary",
            "FROM metrics-postgresqlreceiver.otel-default | STATS max_backends = MAX(`postgresql.backends`), max_size = MAX(`postgresql.db_size`), max_deadlocks = MAX(`postgresql.deadlocks`), max_commits = MAX(`postgresql.commits`), max_rollbacks = MAX(`postgresql.rollbacks`) BY `postgresql.database.name` | WHERE `postgresql.database.name` IS NOT NULL | SORT max_backends DESC",
            ["postgresql.database.name", "max_backends", "max_size", "max_deadlocks", "max_commits", "max_rollbacks"]),
    ]
    deploy_dashboard(
        "PostgreSQL — Performance & Health",
        "Connections, cache hit ratio, commits, deadlocks, and database size via OpenTelemetry",
        panels,
    )


def build_mssql():
    panels = [
        metric_panel("m1", 0,  0, 12, 5,
            "FROM metrics-sqlserverreceiver.otel-default | STATS `User Connections` = MAX(`sqlserver.user.connection.count`)",
            "User Connections"),
        metric_panel("m2", 12, 0, 12, 5,
            "FROM metrics-sqlserverreceiver.otel-default | STATS `Buffer Cache Hit %` = AVG(`sqlserver.page.buffer_cache.hit_ratio`)",
            "Buffer Cache Hit %"),
        metric_panel("m3", 24, 0, 12, 5,
            "FROM metrics-sqlserverreceiver.otel-default | STATS `Avg Lock Wait (ms)` = AVG(`sqlserver.lock.wait_time.avg`)",
            "Avg Lock Wait (ms)"),
        metric_panel("m4", 36, 0, 12, 5,
            "FROM metrics-sqlserverreceiver.otel-default | STATS `Total Deadlocks` = MAX(`sqlserver.deadlock.count`)",
            "Total Deadlocks"),
        xy_panel("c1", 0, 5, 24, 11, "User Connections Over Time", "area",
            "FROM metrics-sqlserverreceiver.otel-default | STATS connections = AVG(`sqlserver.user.connection.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `service.name`",
            "bucket", ["connections"], "service.name"),
        xy_panel("c2", 24, 5, 24, 11, "Lock Wait Time (ms) Over Time", "line",
            "FROM metrics-sqlserverreceiver.otel-default | STATS lock_wait = AVG(`sqlserver.lock.wait_time.avg`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `service.name`",
            "bucket", ["lock_wait"], "service.name"),
        xy_panel("c3", 0, 16, 24, 11, "I/O Read vs Write Latency by Database (ms)", "bar",
            "FROM metrics-sqlserverreceiver.otel-default | STATS read_lat = AVG(`sqlserver.database.io.read_latency`), write_lat = AVG(`sqlserver.database.io.write_latency`) BY `sqlserver.database.name` | WHERE `sqlserver.database.name` IS NOT NULL | SORT read_lat DESC | LIMIT 10",
            "sqlserver.database.name", ["read_lat", "write_lat"]),
        xy_panel("c4", 24, 16, 24, 11, "Batch Requests Over Time", "line",
            "FROM metrics-sqlserverreceiver.otel-default | STATS batches = MAX(`sqlserver.batch_sql_request.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `service.name`",
            "bucket", ["batches"], "service.name"),
        table_panel("t1", 0, 27, 48, 10, "Instance Summary",
            "FROM metrics-sqlserverreceiver.otel-default | STATS max_conns = MAX(`sqlserver.user.connection.count`), avg_cache = AVG(`sqlserver.page.buffer_cache.hit_ratio`), avg_lock_wait = AVG(`sqlserver.lock.wait_time.avg`), total_deadlocks = MAX(`sqlserver.deadlock.count`) BY `service.name` | SORT max_conns DESC",
            ["service.name", "max_conns", "avg_cache", "avg_lock_wait", "total_deadlocks"]),
    ]
    deploy_dashboard(
        "SQL Server — Performance & Health",
        "Connections, lock waits, batch requests, buffer cache, and I/O latency via OpenTelemetry",
        panels,
    )


def build_mongodb():
    panels = [
        metric_panel("m1", 0,  0, 12, 5,
            "FROM metrics-mongodbatlas.otel-default | STATS `Active Connections` = MAX(`mongodb.connection.count`)",
            "Active Connections"),
        metric_panel("m2", 12, 0, 12, 5,
            "FROM metrics-mongodbatlas.otel-default | STATS `Memory Usage` = MAX(`mongodb.memory.usage`)",
            "Memory Usage"),
        metric_panel("m3", 24, 0, 12, 5,
            "FROM metrics-mongodbatlas.otel-default | STATS `Total Operations` = MAX(`mongodb.operation.count`)",
            "Total Operations"),
        metric_panel("m4", 36, 0, 12, 5,
            "FROM metrics-mongodbatlas.otel-default | STATS `Replication Lag (s)` = AVG(`mongodb.replication.lag`)",
            "Replication Lag (s)"),
        xy_panel("c1", 0, 5, 24, 11, "Operations Over Time by Type", "area_stacked",
            "FROM metrics-mongodbatlas.otel-default | STATS ops = MAX(`mongodb.operation.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
            "bucket", ["ops"], "mongodb.operation.type"),
        xy_panel("c2", 24, 5, 24, 11, "Connections by Instance", "line",
            "FROM metrics-mongodbatlas.otel-default | STATS conns = AVG(`mongodb.connection.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `service.name`",
            "bucket", ["conns"], "service.name"),
        xy_panel("c3", 0, 16, 24, 11, "Document Operations Over Time", "line",
            "FROM metrics-mongodbatlas.otel-default | STATS docs = MAX(`mongodb.document.operation.count`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend), `mongodb.operation.type` | WHERE `mongodb.operation.type` IS NOT NULL",
            "bucket", ["docs"], "mongodb.operation.type"),
        xy_panel("c4", 24, 16, 24, 11, "Memory: Resident vs Virtual (bytes)", "area",
            "FROM metrics-mongodbatlas.otel-default | STATS resident = AVG(`mongodb.memory.usage`), virtual = AVG(`mongodb.memory.virtual`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend)",
            "bucket", ["resident", "virtual"]),
        xy_panel("c5", 0, 27, 24, 10, "Database Size", "bar_horizontal",
            "FROM metrics-mongodbatlas.otel-default | STATS size = MAX(`mongodb.database.size`) BY `mongodb.database.name` | WHERE `mongodb.database.name` IS NOT NULL | SORT size DESC | LIMIT 10",
            "mongodb.database.name", ["size"]),
        xy_panel("c6", 24, 27, 24, 10, "Network In / Out (bytes)", "line",
            "FROM metrics-mongodbatlas.otel-default | STATS net_in = MAX(`mongodb.network.io.receive`), net_out = MAX(`mongodb.network.io.transmit`) BY bucket = BUCKET(@timestamp, 75, ?_tstart, ?_tend)",
            "bucket", ["net_in", "net_out"]),
    ]
    deploy_dashboard(
        "MongoDB — Operations & Health",
        "Operation throughput, connections, memory, replication lag, and document stats via OpenTelemetry",
        panels,
    )


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Deploying dashboards to {KIBANA_URL} ...")
    build_mysql()
    build_postgres()
    build_mssql()
    build_mongodb()
    print("\nDone! Open Kibana → Dashboards to view.")
