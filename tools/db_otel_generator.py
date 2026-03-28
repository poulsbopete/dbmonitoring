#!/usr/bin/env python3
"""
db_otel_generator.py
Generates synthetic database monitoring telemetry via OTLP HTTP for
MySQL, PostgreSQL, MS SQL (SQL Server), and MongoDB.

Sends:
  - Historical data: last N days at 5-min intervals (burst on startup)
  - Live data: every 60 s in background (--live flag)

Usage:
  python3 db_otel_generator.py \\
      --otlp-endpoint https://xxx.ingest.us-east-1.aws.elastic.cloud \\
      --otlp-auth "ApiKey <key>" \\
      [--historical-days 4] [--live]
"""

import argparse
import json
import math
import random
import sys
import time
from datetime import datetime, timedelta, timezone

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ns(dt: datetime) -> str:
    """Unix epoch nanoseconds as string (OTLP JSON expects string for int64)."""
    return str(int(dt.timestamp() * 1_000_000_000))


def attr(key: str, value) -> dict:
    if isinstance(value, str):
        return {"key": key, "value": {"stringValue": value}}
    if isinstance(value, bool):
        return {"key": key, "value": {"boolValue": value}}
    if isinstance(value, int):
        return {"key": key, "value": {"intValue": str(value)}}
    if isinstance(value, float):
        return {"key": key, "value": {"doubleValue": value}}
    return {"key": key, "value": {"stringValue": str(value)}}


def post(endpoint: str, auth: str, path: str, payload: dict, retries: int = 2):
    url = endpoint.rstrip("/") + path
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth,
    }
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
            if r.status_code in (200, 204):
                return True
            print(f"  WARN {path} → HTTP {r.status_code}: {r.text[:120]}", file=sys.stderr)
            return False
        except Exception as exc:
            if attempt == retries:
                print(f"  ERROR {path}: {exc}", file=sys.stderr)
    return False


def business_load(dt: datetime) -> float:
    """Return a 0-1 load multiplier: peak during weekday business hours."""
    hour = dt.hour
    wd = dt.weekday()  # 0=Mon … 6=Sun
    if wd >= 5:
        return 0.15 + 0.1 * math.sin(math.pi * hour / 24)
    if 9 <= hour <= 17:
        return 0.7 + 0.3 * math.sin(math.pi * (hour - 9) / 8)
    if 6 <= hour < 9 or 17 < hour <= 20:
        return 0.35
    return 0.1


# ---------------------------------------------------------------------------
# MySQL — slow query logs + error logs
# ---------------------------------------------------------------------------

MYSQL_DBS = ["ecommerce", "inventory", "analytics", "reporting"]
MYSQL_TABLES = {
    "ecommerce":  ["orders", "customers", "cart_items", "payments", "product_reviews"],
    "inventory":  ["stock_levels", "warehouses", "shipments", "suppliers", "purchase_orders"],
    "analytics":  ["events", "sessions", "funnel_steps", "attribution", "revenue_daily"],
    "reporting":  ["report_cache", "aggregations", "dashboard_configs", "scheduled_jobs", "audit_log"],
}
MYSQL_OPS = ["SELECT"] * 7 + ["UPDATE"] * 2 + ["INSERT", "DELETE"]
MYSQL_USERS = ["app_user", "reporting_user", "batch_user", "replication_user"]
MYSQL_HOST = "mysql-primary-001"
MYSQL_SERVICE = "mysql-primary"


def _mysql_slow_record(dt: datetime, load: float) -> dict:
    db = random.choice(MYSQL_DBS)
    table = random.choice(MYSQL_TABLES[db])
    op = random.choice(MYSQL_OPS)
    user = random.choice(MYSQL_USERS)
    # query_time: 0.1–3 s, skewed by load
    base_qt = random.lognormvariate(-1.5, 0.8)
    query_time = max(0.1, min(base_qt * (0.5 + load), 3.0))
    lock_time = query_time * random.uniform(0.0, 0.25)
    rows_examined = int(random.lognormvariate(9, 1.5))
    rows_sent = max(1, int(rows_examined * random.uniform(0.0001, 0.05)))
    severity = "ERROR" if query_time > 2.0 else "WARN"
    severity_num = 17 if severity == "ERROR" else 13
    sql = f"{op} * FROM {table} WHERE id = {random.randint(1, 9_999_999)}"
    body = (f"# Time: {dt.strftime('%Y-%m-%dT%H:%M:%S')}Z\n"
            f"# User@Host: {user}[{user}] @ app-server:{random.randint(40000, 59999)}\n"
            f"# Query_time: {query_time:.3f}  Lock_time: {lock_time:.3f}"
            f"  Rows_sent: {rows_sent}  Rows_examined: {rows_examined}\n"
            f"use {db};\n{sql};")
    return {
        "timeUnixNano": ns(dt),
        "observedTimeUnixNano": ns(dt),
        "severityNumber": severity_num,
        "severityText": severity,
        "body": {"stringValue": body},
        "attributes": [
            attr("db.system", "mysql"),
            attr("db.name", db),
            attr("db.operation", op),
            attr("db.sql.table", table),
            attr("db.user", user),
            attr("db.statement", sql),
            attr("mysql.slowlog.query_time", query_time),
            attr("mysql.slowlog.lock_time", lock_time),
            attr("mysql.slowlog.rows_examined", rows_examined),
            attr("mysql.slowlog.rows_sent", rows_sent),
            attr("client.address", f"app-server-{random.randint(1,4)}.internal"),
            attr("client.port", random.randint(40000, 59999)),
        ],
    }


def _mysql_error_record(dt: datetime) -> dict:
    errors = [
        ("ERROR", 17, "InnoDB: Lock wait timeout exceeded; try restarting transaction"),
        ("ERROR", 17, "Aborted connection (Got timeout reading communication packets)"),
        ("ERROR", 17, "Table './ecommerce/orders' is marked as crashed and should be repaired"),
        ("WARNING", 13, "InnoDB: page_cleaner: 1000ms intended loop took 4327ms"),
        ("WARNING", 13, "Disk is almost full; using /tmp instead"),
        ("WARNING", 13, "Slave SQL: Error 'Duplicate entry' on query"),
        ("WARNING", 13, "Too many connections"),
    ]
    sev_text, sev_num, msg = random.choice(errors)
    return {
        "timeUnixNano": ns(dt),
        "observedTimeUnixNano": ns(dt),
        "severityNumber": sev_num,
        "severityText": sev_text,
        "body": {"stringValue": msg},
        "attributes": [attr("db.system", "mysql")],
    }


def send_mysql(endpoint: str, auth: str, dt: datetime, load: float):
    n_slow = max(1, int(load * 12 + random.gauss(0, 2)))
    slow_records = [_mysql_slow_record(dt + timedelta(seconds=i * 5), load)
                    for i in range(n_slow)]
    payload = {"resourceLogs": [{
        "resource": {"attributes": [
            attr("service.name", MYSQL_SERVICE),
            attr("host.name", MYSQL_HOST),
            attr("db.system", "mysql"),
            attr("deployment.environment", "production"),
            attr("data_stream.type", "logs"),
            attr("data_stream.dataset", "mysql.slowlog.otel"),
            attr("data_stream.namespace", "default"),
        ]},
        "scopeLogs": [{"scope": {"name": "mysql.slowlog.otel"},
                       "logRecords": slow_records}],
    }]}
    post(endpoint, auth, "/v1/logs", payload)

    # Error log — occasional
    if random.random() < (0.05 + 0.15 * load):
        n_err = random.randint(1, 3)
        err_records = [_mysql_error_record(dt + timedelta(seconds=i * 30)) for i in range(n_err)]
        err_payload = {"resourceLogs": [{
            "resource": {"attributes": [
                attr("service.name", MYSQL_SERVICE),
                attr("host.name", MYSQL_HOST),
                attr("data_stream.type", "logs"),
                attr("data_stream.dataset", "mysql.error.otel"),
                attr("data_stream.namespace", "default"),
            ]},
            "scopeLogs": [{"scope": {"name": "mysql.error.otel"}, "logRecords": err_records}],
        }]}
        post(endpoint, auth, "/v1/logs", err_payload)


# ---------------------------------------------------------------------------
# PostgreSQL — metrics
# ---------------------------------------------------------------------------

PG_INSTANCES = [
    {"host": "pg-primary-01", "role": "primary", "service": "postgresql-primary",
     "databases": ["warehouse", "catalog", "auth"]},
    {"host": "pg-replica-01", "role": "replica", "service": "postgresql-replica",
     "databases": ["warehouse", "catalog"]},
]


def _pg_gauge(name: str, value, attrs: list) -> dict:
    return {"name": name, "gauge": {"dataPoints": [{
        "timeUnixNano": "PLACEHOLDER",
        "asDouble": float(value),
        "attributes": attrs,
    }]}}


def _pg_sum(name: str, value, attrs: list, unit: str = "1") -> dict:
    return {"name": name, "unit": unit, "sum": {
        "aggregationTemporality": 2,  # CUMULATIVE
        "isMonotonic": True,
        "dataPoints": [{
            "timeUnixNano": "PLACEHOLDER",
            "asInt": str(int(value)),
            "attributes": attrs,
        }],
    }}


def send_postgres(endpoint: str, auth: str, dt: datetime, load: float,
                  _state: dict):
    ts = ns(dt)
    for inst in PG_INSTANCES:
        is_replica = inst["role"] == "replica"
        metrics = []
        for db in inst["databases"]:
            key = f"{inst['host']}:{db}"
            if key not in _state:
                _state[key] = {
                    "commits": random.randint(10_000, 1_000_000),
                    "rollbacks": random.randint(100, 5_000),
                    "deadlocks": random.randint(0, 50),
                    "blks_hit": random.randint(1_000_000, 100_000_000),
                    "blks_read": random.randint(10_000, 500_000),
                    "tup_inserted": random.randint(50_000, 5_000_000),
                    "tup_updated": random.randint(20_000, 2_000_000),
                    "tup_deleted": random.randint(5_000, 500_000),
                    "tup_fetched": random.randint(500_000, 50_000_000),
                    "tup_returned": random.randint(1_000_000, 100_000_000),
                }
            s = _state[key]
            # Increment counters
            commits_delta = int(load * random.randint(50, 500))
            rollbacks_delta = int(load * random.randint(0, 10))
            deadlocks_delta = 1 if (load > 0.6 and random.random() < 0.05) else 0
            blks_hit_delta = int(load * random.randint(5_000, 50_000))
            blks_read_delta = int(load * random.randint(50, 500))
            s["commits"] += commits_delta
            s["rollbacks"] += rollbacks_delta
            s["deadlocks"] += deadlocks_delta
            s["blks_hit"] += blks_hit_delta
            s["blks_read"] += blks_read_delta
            s["tup_inserted"] += int(load * random.randint(10, 200))
            s["tup_updated"] += int(load * random.randint(20, 400))
            s["tup_deleted"] += int(load * random.randint(2, 50))
            s["tup_fetched"] += int(load * random.randint(500, 5_000))
            s["tup_returned"] += int(load * random.randint(1_000, 10_000))

            backends = int(5 + load * 45 * (0.5 if is_replica else 1) + random.gauss(0, 3))
            backends = max(1, min(backends, 100))
            db_size = 500_000_000 + hash(db) % 50_000_000_000  # stable per DB
            db_attr = [attr("postgresql.database.name", db)]

            metrics += [
                _pg_gauge("postgresql.backends", backends, db_attr),
                _pg_gauge("postgresql.db_size", db_size, db_attr),
                _pg_gauge("postgresql.connection.max", 200, db_attr),
                _pg_sum("postgresql.commits", s["commits"], db_attr),
                _pg_sum("postgresql.rollbacks", s["rollbacks"], db_attr),
                _pg_sum("postgresql.deadlocks", s["deadlocks"], db_attr),
                _pg_sum("postgresql.blks_hit", s["blks_hit"], db_attr),
                _pg_sum("postgresql.blks_read", s["blks_read"], db_attr),
                _pg_sum("postgresql.tup_inserted", s["tup_inserted"], db_attr),
                _pg_sum("postgresql.tup_updated", s["tup_updated"], db_attr),
                _pg_sum("postgresql.tup_deleted", s["tup_deleted"], db_attr),
                _pg_sum("postgresql.tup_fetched", s["tup_fetched"], db_attr),
                _pg_sum("postgresql.tup_returned", s["tup_returned"], db_attr),
            ]

        # Fix timestamps
        for m in metrics:
            dp_list = (m.get("gauge") or m.get("sum", {})).get("dataPoints", [])
            for dp in dp_list:
                dp["timeUnixNano"] = ts

        res_attrs = [
            attr("service.name", inst["service"]),
            attr("host.name", inst["host"]),
            attr("postgresql.role", inst["role"]),
            attr("deployment.environment", "production"),
            attr("data_stream.type", "metrics"),
            attr("data_stream.dataset", "postgresqlreceiver.otel"),
            attr("data_stream.namespace", "default"),
        ]
        payload = {"resourceMetrics": [{
            "resource": {"attributes": res_attrs},
            "scopeMetrics": [{"scope": {"name": "postgresqlreceiver.otel"}, "metrics": metrics}],
        }]}
        post(endpoint, auth, "/v1/metrics", payload)


# ---------------------------------------------------------------------------
# MS SQL Server — metrics (most important per customer brief)
# ---------------------------------------------------------------------------

MSSQL_INSTANCES = [
    {"host": "mssql-prod-01", "instance": "MSSQLSERVER", "service": "sqlserver-production",
     "databases": ["SalesDB", "InventoryDB", "CustomerDB", "ReportingDB"]},
    {"host": "mssql-prod-02", "instance": "MSSQLSERVER", "service": "sqlserver-secondary",
     "databases": ["SalesDB", "CustomerDB"]},
]


def _ms_gauge(name: str, value, attrs: list, unit: str = "1") -> dict:
    return {"name": name, "unit": unit, "gauge": {"dataPoints": [{
        "timeUnixNano": "PLACEHOLDER",
        "asDouble": float(value),
        "attributes": attrs,
    }]}}


def _ms_sum(name: str, value, attrs: list, unit: str = "1") -> dict:
    return {"name": name, "unit": unit, "sum": {
        "aggregationTemporality": 2,
        "isMonotonic": True,
        "dataPoints": [{"timeUnixNano": "PLACEHOLDER", "asInt": str(int(value)),
                        "attributes": attrs}],
    }}


def send_mssql(endpoint: str, auth: str, dt: datetime, load: float, _state: dict):
    ts = ns(dt)
    for inst in MSSQL_INSTANCES:
        key = inst["host"]
        if key not in _state:
            _state[key] = {
                "batch_requests": random.randint(1_000_000, 100_000_000),
                "sql_compilations": random.randint(10_000, 1_000_000),
                "lock_waits": random.randint(0, 10_000),
                "page_reads": random.randint(100_000, 10_000_000),
                "page_writes": random.randint(50_000, 5_000_000),
                "transactions": random.randint(100_000, 10_000_000),
                "deadlocks": random.randint(0, 100),
            }
        s = _state[key]
        s["batch_requests"] += int(load * random.randint(500, 5_000))
        s["sql_compilations"] += int(load * random.randint(10, 100))
        s["lock_waits"] += int(load * random.randint(0, 20))
        s["page_reads"] += int(load * random.randint(100, 2_000))
        s["page_writes"] += int(load * random.randint(50, 1_000))
        s["transactions"] += int(load * random.randint(100, 2_000))
        if load > 0.6 and random.random() < 0.03:
            s["deadlocks"] += 1

        user_connections = int(50 + load * 450 + random.gauss(0, 20))
        user_connections = max(5, min(user_connections, 1_000))
        buf_cache_hit = 96.0 + random.uniform(-2, 2)
        lock_wait_time = random.lognormvariate(1, 1) if load > 0.3 else 0.0
        active_transactions = int(load * 200 + random.gauss(0, 10))
        no_attr: list = []
        inst_attr = [attr("sqlserver.instance.name", inst["instance"])]

        metrics = [
            _ms_gauge("sqlserver.user.connection.count", user_connections, no_attr),
            _ms_gauge("sqlserver.page.buffer_cache.hit_ratio", buf_cache_hit, no_attr, "%"),
            _ms_gauge("sqlserver.lock.wait_time.avg", lock_wait_time, no_attr, "ms"),
            _ms_gauge("sqlserver.transaction.active.count", active_transactions, no_attr),
            _ms_sum("sqlserver.batch_sql_request.count", s["batch_requests"], no_attr),
            _ms_sum("sqlserver.sql_compilation.count", s["sql_compilations"], no_attr),
            _ms_sum("sqlserver.lock.wait.count", s["lock_waits"], no_attr),
            _ms_sum("sqlserver.page.read.count", s["page_reads"], no_attr),
            _ms_sum("sqlserver.page.write.count", s["page_writes"], no_attr),
            _ms_sum("sqlserver.transaction.count", s["transactions"], no_attr),
            _ms_sum("sqlserver.deadlock.count", s["deadlocks"], no_attr),
        ]

        # Per-database metrics
        for db in inst["databases"]:
            db_attr = [attr("sqlserver.database.name", db)]
            read_latency = random.lognormvariate(1.5, 0.8)
            write_latency = random.lognormvariate(1.2, 0.7)
            db_size = 1_000_000_000 + hash(db) % 100_000_000_000
            metrics += [
                _ms_gauge("sqlserver.database.io.read_latency", read_latency, db_attr, "ms"),
                _ms_gauge("sqlserver.database.io.write_latency", write_latency, db_attr, "ms"),
                _ms_gauge("sqlserver.database.size", db_size, db_attr, "By"),
            ]

        for m in metrics:
            dp_list = (m.get("gauge") or m.get("sum", {})).get("dataPoints", [])
            for dp in dp_list:
                dp["timeUnixNano"] = ts

        res_attrs = [
            attr("service.name", inst["service"]),
            attr("host.name", inst["host"]),
            attr("sqlserver.computer.name", inst["host"]),
            attr("deployment.environment", "production"),
            attr("data_stream.type", "metrics"),
            attr("data_stream.dataset", "sqlserverreceiver.otel"),
            attr("data_stream.namespace", "default"),
        ]
        payload = {"resourceMetrics": [{
            "resource": {"attributes": res_attrs},
            "scopeMetrics": [{"scope": {"name": "sqlserverreceiver.otel"}, "metrics": metrics}],
        }]}
        post(endpoint, auth, "/v1/metrics", payload)


# ---------------------------------------------------------------------------
# MongoDB — metrics
# ---------------------------------------------------------------------------

MONGO_INSTANCES = [
    {"host": "mongo-rs0-primary", "role": "primary", "service": "mongodb-primary",
     "rs": "rs0", "databases": ["product_catalog", "user_data", "sessions", "analytics"]},
    {"host": "mongo-rs0-secondary", "role": "secondary", "service": "mongodb-secondary",
     "rs": "rs0", "databases": ["product_catalog", "user_data"]},
]
MONGO_OPS = ["insert", "query", "update", "delete", "getmore", "command"]


def _mdb_gauge(name: str, value, attrs: list, unit: str = "1") -> dict:
    return {"name": name, "unit": unit, "gauge": {"dataPoints": [{
        "timeUnixNano": "PLACEHOLDER",
        "asDouble": float(value),
        "attributes": attrs,
    }]}}


def _mdb_sum(name: str, value, attrs: list) -> dict:
    return {"name": name, "sum": {
        "aggregationTemporality": 2,
        "isMonotonic": True,
        "dataPoints": [{"timeUnixNano": "PLACEHOLDER", "asInt": str(int(value)),
                        "attributes": attrs}],
    }}


def send_mongodb(endpoint: str, auth: str, dt: datetime, load: float, _state: dict):
    ts = ns(dt)
    for inst in MONGO_INSTANCES:
        key = inst["host"]
        is_primary = inst["role"] == "primary"
        if key not in _state:
            _state[key] = {op: random.randint(10_000, 10_000_000) for op in MONGO_OPS}
            _state[key]["docs_inserted"] = random.randint(100_000, 10_000_000)
            _state[key]["docs_updated"] = random.randint(50_000, 5_000_000)
            _state[key]["docs_deleted"] = random.randint(10_000, 1_000_000)
            _state[key]["replication_lag"] = 0.0

        s = _state[key]
        # Update op counters
        for op in MONGO_OPS:
            write_load = load if is_primary else load * 0.1
            s[op] += int(write_load * random.randint(5, 500))
        s["docs_inserted"] += int(load * random.randint(1, 100))
        s["docs_updated"] += int(load * random.randint(5, 200))
        s["docs_deleted"] += int(load * random.randint(0, 20))
        if not is_primary:
            s["replication_lag"] = max(0, min(10, random.lognormvariate(-1, 1)))

        connections = int(10 + load * 190 * (1.0 if is_primary else 0.3) + random.gauss(0, 5))
        connections = max(1, min(connections, 500))
        resident_mb = int(512 + load * 3_000 + random.gauss(0, 100))
        virtual_mb = resident_mb * random.uniform(2, 4)
        network_in = int(load * random.randint(100_000, 5_000_000))
        network_out = int(load * random.randint(200_000, 10_000_000))

        no_attr: list = []
        role_attr = [attr("mongodb.role", inst["role"])]

        metrics = [
            _mdb_gauge("mongodb.connection.count", connections, no_attr),
            _mdb_gauge("mongodb.memory.usage", resident_mb * 1024 * 1024, no_attr, "By"),
            _mdb_gauge("mongodb.memory.virtual", virtual_mb * 1024 * 1024, no_attr, "By"),
        ]
        for op in MONGO_OPS:
            metrics.append(_mdb_sum("mongodb.operation.count", s[op],
                                    [attr("mongodb.operation.type", op)]))

        metrics += [
            _mdb_sum("mongodb.document.operation.count", s["docs_inserted"],
                     [attr("mongodb.operation.type", "insert")]),
            _mdb_sum("mongodb.document.operation.count", s["docs_updated"],
                     [attr("mongodb.operation.type", "update")]),
            _mdb_sum("mongodb.document.operation.count", s["docs_deleted"],
                     [attr("mongodb.operation.type", "delete")]),
            _mdb_sum("mongodb.network.io.receive", network_in, no_attr),
            _mdb_sum("mongodb.network.io.transmit", network_out, no_attr),
        ]
        if not is_primary:
            metrics.append(_mdb_gauge("mongodb.replication.lag", s["replication_lag"],
                                      no_attr, "s"))

        for db in inst["databases"]:
            db_attr = [attr("mongodb.database.name", db)]
            coll_count = random.randint(5, 50)
            db_size = 100_000_000 + hash(db) % 10_000_000_000
            metrics += [
                _mdb_gauge("mongodb.database.collection.count", coll_count, db_attr),
                _mdb_gauge("mongodb.database.size", db_size, db_attr, "By"),
            ]

        for m in metrics:
            dp_list = (m.get("gauge") or m.get("sum", {})).get("dataPoints", [])
            for dp in dp_list:
                dp["timeUnixNano"] = ts

        rs_attr = [attr("mongodb.replicaset.name", inst["rs"])]
        res_attrs = [
            attr("service.name", inst["service"]),
            attr("host.name", inst["host"]),
            attr("mongodb.host", inst["host"]),
            attr("deployment.environment", "production"),
            attr("data_stream.type", "metrics"),
            attr("data_stream.dataset", "mongodbatlas.otel"),
            attr("data_stream.namespace", "default"),
        ]
        payload = {"resourceMetrics": [{
            "resource": {"attributes": res_attrs},
            "scopeMetrics": [{"scope": {"name": "mongodbatlas.otel"}, "metrics": metrics}],
        }]}
        post(endpoint, auth, "/v1/metrics", payload)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_window(endpoint: str, auth: str, dt: datetime,
                    pg_state: dict, ms_state: dict, mdb_state: dict,
                    metrics_now: datetime = None):
    """Send one interval of data for all 4 DB types.

    MySQL slow/error logs use the historical ``dt`` timestamp — LogsDB accepts
    any timestamp.  TSDB metrics streams only accept documents within a ~2 hour
    rolling window, so PostgreSQL/SQL Server/MongoDB always use ``metrics_now``
    (current wall-clock time) to avoid timestamp_error failures.
    """
    load = business_load(dt)
    ts_metrics = metrics_now or datetime.now(timezone.utc)
    send_mysql(endpoint, auth, dt, load)
    send_postgres(endpoint, auth, ts_metrics, load, pg_state)
    send_mssql(endpoint, auth, ts_metrics, load, ms_state)
    send_mongodb(endpoint, auth, ts_metrics, load, mdb_state)


def main():
    parser = argparse.ArgumentParser(description="DB OTel data generator")
    parser.add_argument("--otlp-endpoint", required=True,
                        help="OTLP HTTP base URL (e.g. https://xxx.ingest.us-east-1.aws.elastic.cloud)")
    parser.add_argument("--otlp-auth", required=True,
                        help="Authorization header value (e.g. 'ApiKey xxxx==')")
    parser.add_argument("--historical-days", type=int, default=4,
                        help="Days of historical MySQL log data to seed (default: 4)")
    parser.add_argument("--live", action="store_true",
                        help="Keep running and send live data every 60 s")
    parser.add_argument("--interval-minutes", type=int, default=5,
                        help="Minutes between historical data points (default: 5)")
    args = parser.parse_args()

    pg_state: dict = {}
    ms_state: dict = {}
    mdb_state: dict = {}

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=args.historical_days)
    step = timedelta(minutes=args.interval_minutes)
    total = int((now - start) / step)

    print(f"Generating {args.historical_days}d historical data "
          f"({total} intervals × {args.interval_minutes}-min)…")
    print("  MySQL logs: historical timestamps | PG/MSSQL/MongoDB metrics: current timestamp (TSDB window)")

    dt = start
    i = 0
    while dt <= now:
        now_wall = datetime.now(timezone.utc)
        generate_window(args.otlp_endpoint, args.otlp_auth, dt,
                        pg_state, ms_state, mdb_state, metrics_now=now_wall)
        i += 1
        if i % 50 == 0:
            pct = int(100 * i / total)
            print(f"  {pct}% ({i}/{total} intervals)…")
        dt += step

    print("Historical data sent.")

    if args.live:
        print("Live mode: sending data every 60 s. Ctrl-C to stop.")
        while True:
            time.sleep(60)
            now = datetime.now(timezone.utc)
            generate_window(args.otlp_endpoint, args.otlp_auth, now,
                            pg_state, ms_state, mdb_state, metrics_now=now)
            print(f"  Live tick {now.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
