#!/usr/bin/env python3
"""
deploy-alert-rules.py
Creates/updates database monitoring alert rules in Kibana.

Usage:
  python3 alert-rules/deploy-alert-rules.py
  python3 alert-rules/deploy-alert-rules.py cleanup-workflows   # fix/remove broken "Untitled workflow" rows
  python3 alert-rules/deploy-alert-rules.py deploy-workflow db-recommendations-workflow.yaml
      # upsert one workflow (updates running instance when name matches Kibana)

Env:
  KIBANA_URL, ES_API_KEY or KIBANA_API_KEY  (or ES_USERNAME + ES_PASSWORD)
"""
import json, os, sys, urllib.parse, urllib.request, urllib.error, base64

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


def _http_json(method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"{KIBANA_URL}{path}", data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            if not raw:
                return None, r.status
            return json.loads(raw), r.status
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else ""
        return {"_http_error": e.code, "_body": err_body}, e.code


def _workflow_items(payload):
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in ("data", "workflows", "items", "results", "saved_objects"):
        block = payload.get(key)
        if isinstance(block, list):
            return block
    return []


def list_workflows():
    """Return workflow summary objects from Kibana (shape varies by version)."""
    # Serverless returns { page, size, total, results: [...] } — no perPage query param.
    for path in ("/api/workflows",):
        payload, status = _http_json("GET", path)
        if status == 404:
            continue
        if isinstance(payload, dict) and payload.get("_http_error"):
            continue
        items = _workflow_items(payload)
        if items or status == 200:
            return items
    return []


def delete_workflow(workflow_id):
    """DELETE /api/workflows/:id — removes a workflow definition (often 404 on Serverless)."""
    qid = urllib.parse.quote(workflow_id, safe="")
    req = urllib.request.Request(
        f"{KIBANA_URL}/api/workflows/{qid}", headers=HEADERS, method="DELETE")
    try:
        with urllib.request.urlopen(req) as r:
            return 200 <= r.status < 300
    except urllib.error.HTTPError:
        return False


def _minimal_valid_workflow_yaml(title: str) -> str:
    """Valid minimal workflow (Serverless rejects log-only steps; needs kibana.request)."""
    safe = title.replace('"', "'")
    return (
        'version: "1"\n'
        f"name: {safe}\n"
        "description: >\n"
        "  Repaired after an invalid import (was Untitled / valid=false). "
        "Safe to delete from the Workflows UI if you do not need it.\n"
        "enabled: false\n"
        "triggers:\n"
        "  - type: manual\n"
        "steps:\n"
        "  - name: noop\n"
        "    type: kibana.request\n"
        "    with:\n"
        "      method: GET\n"
        "      path: /api/status\n"
    )


def repair_workflow(workflow_id, title: str) -> bool:
    """In-place fix: POST /api/workflows with { id, yaml }. Required when DELETE is not available."""
    payload, status = _http_json(
        "POST",
        "/api/workflows",
        {"workflows": [{"id": workflow_id, "yaml": _minimal_valid_workflow_yaml(title)}]},
    )
    if not isinstance(payload, dict) or payload.get("_http_error"):
        return False
    created = payload.get("created") or []
    if not created:
        return False
    return created[0].get("valid") is True


def cleanup_untitled_workflows():
    """
    Fix or remove workflows stuck as 'Untitled workflow' (no triggers / invalid YAML).

    On Elastic Serverless, per-id DELETE often returns 404 for API keys; the same API
    supports updating by POSTing { id, yaml } with a valid definition.
    """
    items = list_workflows()
    if not items:
        print("  (No workflows listed from GET /api/workflows — skip cleanup, or list API unavailable)")
        return 0
    deleted = 0
    repaired = 0
    for w in items:
        if not isinstance(w, dict):
            continue
        name = (w.get("name") or "").strip().lower()
        if name != "untitled workflow":
            continue
        wid = w.get("id")
        if not wid:
            continue
        suffix = wid.split("-")[-1][:8] if "-" in wid else wid[-8:]
        repair_title = f"Repaired orphan workflow ({suffix})"
        if delete_workflow(wid):
            print(f"  ✓ Removed broken workflow {wid}")
            deleted += 1
        elif repair_workflow(wid, repair_title):
            print(f"  ✓ Repaired broken workflow {wid} → {repair_title!r}")
            repaired += 1
        else:
            print(f"  ✗ Could not delete or repair {wid}")
    if deleted or repaired:
        print(f"  Cleanup: removed {deleted}, repaired {repaired} untitled workflow(s).")
    else:
        print("  Cleanup: no 'Untitled workflow' entries found.")
    return deleted + repaired


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
                    "timeFieldName": "@timestamp",
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
                    "timeFieldName": "@timestamp",
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
                    "timeFieldName": "@timestamp",
                },
                "query": {"language": "kuery", "query": ""},
            },
        },
        "actions": workflow_action("custom_threshold.fired"),
    }),
    # --- IBM Db2: High Connection Count ---
    ("db-alert-db2-connections", {
        "name": "🗄️ IBM Db2 — High Connection Count",
        "rule_type_id": "observability.rules.custom_threshold",
        "consumer": "observability",
        "schedule": {"interval": "5m"},
        "tags": ["database-monitoring", "db2", "demo"],
        "params": {
            "criteria": [{
                "comparator": ">",
                "metrics": [{"name": "A", "aggType": "avg", "field": "db2.connection.active"}],
                "threshold": [350],
                "timeSize": 5,
                "timeUnit": "m",
            }],
            "alertOnNoData": False,
            "alertOnGroupDisappear": False,
            "groupBy": ["service.name"],
            "searchConfiguration": {
                "index": {
                    "id": "metrics-db2receiver.otel.otel-default",
                    "title": "metrics-db2receiver.otel.otel-default",
                    "timeFieldName": "@timestamp",
                },
                "query": {"language": "kuery", "query": ""},
            },
        },
        "actions": workflow_action("custom_threshold.fired"),
    }),
    # --- Oracle: High Active Sessions ---
    ("db-alert-oracle-sessions", {
        "name": "🔴 Oracle — High Active Sessions",
        "rule_type_id": "observability.rules.custom_threshold",
        "consumer": "observability",
        "schedule": {"interval": "5m"},
        "tags": ["database-monitoring", "oracle", "demo"],
        "params": {
            "criteria": [{
                "comparator": ">",
                "metrics": [{"name": "A", "aggType": "avg", "field": "oracledb.sessions.current"}],
                "threshold": [250],
                "timeSize": 5,
                "timeUnit": "m",
            }],
            "alertOnNoData": False,
            "alertOnGroupDisappear": False,
            "searchConfiguration": {
                "index": {
                    "id": "metrics-oracledbreceiver.otel.otel-default",
                    "title": "metrics-oracledbreceiver.otel.otel-default",
                    "timeFieldName": "@timestamp",
                },
                "query": {"language": "kuery", "query": "session.type: active"},
            },
        },
        "actions": workflow_action("custom_threshold.fired"),
    }),
]


def _parse_workflow_name_from_yaml(yaml_content: str):
    """First top-level `name:` value in workflow YAML (quoted or not)."""
    for raw in yaml_content.splitlines():
        line = raw.strip()
        if not line.startswith("name:"):
            continue
        val = line[5:].strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            return val[1:-1]
        return val
    return None


def _find_workflow_id_by_name(workflow_name: str):
    """Return Kibana workflow id whose name equals workflow_name, or None."""
    if not workflow_name:
        return None
    for w in list_workflows():
        if not isinstance(w, dict):
            continue
        n = (w.get("name") or "").strip()
        if n == workflow_name.strip():
            return w.get("id")
    return None


def deploy_workflow(filename, label):
    """
    Deploy a workflow YAML to Kibana: update in place when a workflow with the same
    YAML `name` already exists (POST /api/workflows with { id, yaml }), otherwise create.
    """
    yaml_path = os.path.join(os.path.dirname(__file__), f"../workflows/{filename}")
    if not os.path.exists(yaml_path):
        print(f"  WARN: {filename} not found, skipping")
        return None
    yaml_content = open(yaml_path).read()
    wname = _parse_workflow_name_from_yaml(yaml_content)
    existing_id = _find_workflow_id_by_name(wname) if wname else None

    if existing_id:
        entry = {"id": existing_id, "yaml": yaml_content}
        action = "update"
    else:
        entry = {"yaml": yaml_content}
        action = "create"

    req = urllib.request.Request(
        f"{KIBANA_URL}/api/workflows",
        data=json.dumps({"workflows": [entry]}).encode(),
        headers=HEADERS,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
            failed = result.get("failed") or []
            if failed:
                print(f"  WARN: {label}: API reported failure: {failed[0]!s}"[:300])
                return None
            created = result.get("created") or []
            updated = result.get("updated") or []
            row = (created[0] if created else None) or (updated[0] if updated else None)
            if row and row.get("id"):
                wid = row["id"]
                print(f"  ✓ {label}: {action} {row.get('name', '?')} (id={wid})")
                return wid
            if existing_id and not failed:
                print(f"  ✓ {label}: {action} (id={existing_id})")
                return existing_id
            print(f"  WARN: {label}: unexpected response keys={list(result.keys())}")
            return None
    except urllib.error.HTTPError as e:
        print(f"  WARN: {label} deploy failed HTTP {e.code}: {e.read().decode()[:400]}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("cleanup-workflows", "cleanup"):
        print("\nCleaning up broken workflows (Untitled only)...")
        cleanup_untitled_workflows()
        sys.exit(0)

    if len(sys.argv) > 2 and sys.argv[1] == "deploy-workflow":
        wf_file = sys.argv[2]
        print(f"\nUpserting single workflow: {wf_file} ...")
        wid = deploy_workflow(wf_file, wf_file)
        if wid:
            print(f"\n✓ {KIBANA_URL}/app/management/insightsAndAlerting/workflows/{wid}")
        sys.exit(0 if wid else 1)

    print("\nCleaning up broken workflows (Untitled only)...")
    cleanup_untitled_workflows()

    print("\nDeploying Workflows...")
    wf_id = deploy_workflow("rca-workflow.yaml", "RCA Workflow")
    if wf_id:
        WORKFLOW_ID = wf_id

    slo_wf_id = deploy_workflow("db-slo-workflow.yaml", "SLO Workflow")
    rec_wf_id = deploy_workflow("db-recommendations-workflow.yaml", "AI recommendations → Elasticsearch")

    print("\nDeploying Alert Rules...")
    for rule_id, body in RULES:
        # The Workflows preview feature is not exposed as a connector type in the
        # REST API, so rules are created without workflow actions. Wiring is done
        # via the Kibana UI after deployment.
        body["actions"] = []
        result = upsert_rule(rule_id, body)
        if "error" in result:
            print(f"  ✗ {body['name']}: {result.get('msg','')[:100]}")
        else:
            print(f"  ✓ {result['name']} [{result.get('enabled') and 'enabled' or 'disabled'}]")

    print(f"\n✓ Alert rules:   {KIBANA_URL}/app/observability/alerts/rules")
    if wf_id:
        print(f"✓ RCA Workflow:  {KIBANA_URL}/app/management/insightsAndAlerting/workflows/{wf_id}")
    if slo_wf_id:
        print(f"✓ SLO Workflow:  {KIBANA_URL}/app/management/insightsAndAlerting/workflows/{slo_wf_id}")
        print(f"  → Trigger once to seed the 7 DB SLOs, then runs every 24 h automatically.")
    if rec_wf_id:
        print(f"✓ AI recommendations: {KIBANA_URL}/app/management/insightsAndAlerting/workflows/{rec_wf_id}")
        print(f"  → Runs every 10 min + manual: indexes six docs (mysql..oracle) into db-monitoring-recommendations.")
    if wf_id:
        print("""
┌─ Wire RCA workflow to each rule in the UI ──────────────────────────────┐
│  Alerts → Rules → select a rule → Edit → Actions tab                   │
│  → Add action → Workflows → select "Database Monitoring — RCA"          │
│  Repeat for all 7 rules.                                                │
└─────────────────────────────────────────────────────────────────────────┘""")
