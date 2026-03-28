#!/usr/bin/env python3
"""
deploy-alert-rules.py
Creates/updates database monitoring alert rules in Kibana.

Usage:
  python3 alert-rules/deploy-alert-rules.py

Env:
  KIBANA_URL, ES_API_KEY  (or ES_USERNAME + ES_PASSWORD)
"""
import json, os, sys, urllib.request, urllib.error, base64

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
API_KEY    = os.environ.get("ES_API_KEY", "") or os.environ.get("KIBANA_API_KEY", "")
ES_USER    = os.environ.get("ES_USERNAME", "admin")
ES_PASS    = os.environ.get("ES_PASSWORD", "")

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

WORKFLOW_ID = os.environ.get("WORKFLOW_ID", "")


def upsert_rule(rule_id, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{KIBANA_URL}/api/alerting/rule/{rule_id}", data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 409:
            # Already exists — update via PUT (rule_type_id + consumer are immutable, omit them)
            put_body = {k: v for k, v in body.items() if k not in ("rule_type_id", "consumer")}
            req2 = urllib.request.Request(
                f"{KIBANA_URL}/api/alerting/rule/{rule_id}",
                data=json.dumps(put_body).encode(), headers=HEADERS, method="PUT")
            try:
                with urllib.request.urlopen(req2) as r2:
                    return json.loads(r2.read())
            except urllib.error.HTTPError as e2:
                return {"error": e2.code, "msg": e2.read().decode()[:300]}
        return {"error": e.code, "msg": e.read().decode()[:300]}


def workflow_action(action_group="query matched"):
    """Only adds workflow action if WORKFLOW_ID env var is set."""
    if not WORKFLOW_ID:
        return []
    return [{
        "id": WORKFLOW_ID,
        "group": action_group,
        "params": {},
        "frequency": {"summary": False, "notify_when": "onActionGroupChange"}
    }]


RULES = [
    # --- MySQL: Slow Query Spike ---
    ("db-alert-mysql-slow-queries", {
        "name": "🐢 MySQL — Slow Query Spike",
        "rule_type_id": ".es-query",
        "consumer": "observability",
        "schedule": {"interval": "5m"},
        "tags": ["database-monitoring", "mysql", "demo"],
        "params": {
            "index": ["logs-mysql.slowlog.otel.otel-default"],
            "timeField": "@timestamp",
            "esQuery": json.dumps({"query": {"match_all": {}}}),
            "threshold": [10],
            "thresholdComparator": ">",
            "timeWindowSize": 5,
            "timeWindowUnit": "m",
            "size": 100,
            "searchType": "esQuery",
            "excludeHitsFromPreviousRun": False,
        },
        "actions": workflow_action("query matched"),
    }),
    # --- MySQL: Error Log Spike ---
    ("db-alert-mysql-errors", {
        "name": "🔴 MySQL — Error Log Spike",
        "rule_type_id": ".es-query",
        "consumer": "observability",
        "schedule": {"interval": "5m"},
        "tags": ["database-monitoring", "mysql", "demo"],
        "params": {
            "index": ["logs-mysql.error.otel.otel-default"],
            "timeField": "@timestamp",
            "esQuery": json.dumps({"query": {"match_all": {}}}),
            "threshold": [3],
            "thresholdComparator": ">",
            "timeWindowSize": 5,
            "timeWindowUnit": "m",
            "size": 100,
            "searchType": "esQuery",
            "excludeHitsFromPreviousRun": False,
        },
        "actions": workflow_action("query matched"),
    }),
    # --- PostgreSQL: High Connection Count ---
    ("db-alert-postgres-connections", {
        "name": "🐘 PostgreSQL — High Connection Count",
        "rule_type_id": "observability.rules.custom_threshold",
        "consumer": "observability",
        "schedule": {"interval": "5m"},
        "tags": ["database-monitoring", "postgresql", "demo"],
        "params": {
            "criteria": [{
                "comparator": ">",
                "metrics": [{"name": "A", "aggType": "avg", "field": "postgresql.backends"}],
                "threshold": [80],
                "timeSize": 5,
                "timeUnit": "m",
            }],
            "alertOnNoData": False,
            "alertOnGroupDisappear": False,
            "groupBy": ["postgresql.database.name"],
            "searchConfiguration": {
                "index": {
                    "id": "metrics-postgresqlreceiver.otel.otel-default",
                    "title": "metrics-postgresqlreceiver.otel.otel-default",
                },
                "query": {"language": "kuery", "query": ""},
            },
        },
        "actions": workflow_action("custom_threshold.fired"),
    }),
    # --- SQL Server: High Active Transactions ---
    ("db-alert-sqlserver-transactions", {
        "name": "💾 SQL Server — High Active Transactions",
        "rule_type_id": "observability.rules.custom_threshold",
        "consumer": "observability",
        "schedule": {"interval": "5m"},
        "tags": ["database-monitoring", "sqlserver", "demo"],
        "params": {
            "criteria": [{
                "comparator": ">",
                "metrics": [{"name": "A", "aggType": "avg",
                             "field": "sqlserver.transaction.active.count"}],
                "threshold": [100],
                "timeSize": 5,
                "timeUnit": "m",
            }],
            "alertOnNoData": False,
            "alertOnGroupDisappear": False,
            "searchConfiguration": {
                "index": {
                    "id": "metrics-sqlserverreceiver.otel.otel-default",
                    "title": "metrics-sqlserverreceiver.otel.otel-default",
                },
                "query": {"language": "kuery", "query": ""},
            },
        },
        "actions": workflow_action("custom_threshold.fired"),
    }),
    # --- MongoDB: High Operations Rate ---
    ("db-alert-mongodb-ops", {
        "name": "🍃 MongoDB — High Operations Rate",
        "rule_type_id": "observability.rules.custom_threshold",
        "consumer": "observability",
        "schedule": {"interval": "5m"},
        "tags": ["database-monitoring", "mongodb", "demo"],
        "params": {
            "criteria": [{
                "comparator": ">",
                "metrics": [{"name": "A", "aggType": "avg", "field": "mongodb.operation.count"}],
                "threshold": [5000],
                "timeSize": 5,
                "timeUnit": "m",
            }],
            "alertOnNoData": False,
            "alertOnGroupDisappear": False,
            "searchConfiguration": {
                "index": {
                    "id": "metrics-mongodbatlas.otel.otel-default",
                    "title": "metrics-mongodbatlas.otel.otel-default",
                },
                "query": {"language": "kuery", "query": ""},
            },
        },
        "actions": workflow_action("custom_threshold.fired"),
    }),
]


def deploy_workflow():
    """Deploy the RCA workflow YAML to Kibana."""
    yaml_path = os.path.join(os.path.dirname(__file__), "../workflows/rca-workflow.yaml")
    if not os.path.exists(yaml_path):
        print("WARN: rca-workflow.yaml not found, skipping workflow deploy")
        return None
    yaml_content = open(yaml_path).read()
    req = urllib.request.Request(
        f"{KIBANA_URL}/api/workflows",
        data=json.dumps({"yaml": yaml_content}).encode(),
        headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
            print(f"  ✓ Workflow deployed: {result['name']} (id={result['id']})")
            return result["id"]
    except urllib.error.HTTPError as e:
        print(f"  WARN: Workflow deploy failed HTTP {e.code}: {e.read().decode()[:200]}")
        return None


if __name__ == "__main__":
    print("\nDeploying RCA Workflow...")
    wf_id = deploy_workflow()
    if wf_id:
        global WORKFLOW_ID
        WORKFLOW_ID = wf_id

    print("\nDeploying Alert Rules...")
    for rule_id, body in RULES:
        # Refresh workflow_action with deployed ID
        if wf_id:
            group = "query matched" if body["rule_type_id"] == ".es-query" else "custom_threshold.fired"
            body["actions"] = [{
                "id": wf_id, "group": group, "params": {},
                "frequency": {"summary": False, "notify_when": "onActionGroupChange"}
            }]
        result = upsert_rule(rule_id, body)
        if "error" in result:
            print(f"  ✗ {body['name']}: {result.get('msg','')[:100]}")
        else:
            print(f"  ✓ {result['name']} [{result.get('enabled') and 'enabled' or 'disabled'}]")

    print(f"\n✓ Done. View rules at: {KIBANA_URL}/app/observability/alerts/rules")
    if wf_id:
        print(f"✓ Workflow at:         {KIBANA_URL}/app/management/insightsAndAlerting/workflows/{wf_id}")
    print("""
NOTE: To wire the workflow to each rule:
  Stack Management → Rules → select a rule → Edit → Actions → Workflows → select the RCA workflow
""")
