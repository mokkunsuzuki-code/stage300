#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "spec" / "compatibility_policy.json"
CONTRACT_PATH = ROOT / "out" / "product" / "qsp_product_contract.json"
OUT_DIR = ROOT / "out" / "compatibility"
REPORT_PATH = OUT_DIR / "compatibility_report.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    version = contract.get("spec_version", "unknown")

    checks = []

    checks.append({
        "id": "COMPAT-001",
        "title": "Known version required",
        "passed": version in policy["supported_contract_versions"],
        "detail": f"contract spec_version={version}"
    })

    checks.append({
        "id": "COMPAT-002",
        "title": "Core layers must remain present",
        "passed": all(
            key in contract
            for key in ["input_layer", "decision_layer", "enforcement_layer", "exposure_layer"]
        ),
        "detail": "checked required core layers"
    })

    checks.append({
        "id": "COMPAT-003",
        "title": "Decision semantics must be stable",
        "passed": contract.get("decision_layer", {}).get("decision") in {"accept", "pending", "reject"},
        "detail": f"decision={contract.get('decision_layer', {}).get('decision')}"
    })

    checks.append({
        "id": "COMPAT-004",
        "title": "Fail-closed semantics must be preserved",
        "passed": isinstance(contract.get("enforcement_layer", {}).get("fail_closed"), bool),
        "detail": f"fail_closed={contract.get('enforcement_layer', {}).get('fail_closed')}"
    })

    checks.append({
        "id": "COMPAT-005",
        "title": "Public status must remain derivable",
        "passed": contract.get("exposure_layer", {}).get("public_status") in {"accept", "pending", "reject"},
        "detail": f"public_status={contract.get('exposure_layer', {}).get('public_status')}"
    })

    is_compatible = all(check["passed"] for check in checks)

    report = {
        "stage": "stage287",
        "policy_id": policy["policy_id"],
        "checked_contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract_version": version,
        "is_compatible": is_compatible,
        "checks": checks
    }

    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    print(f"[OK] wrote {REPORT_PATH}")
    print(f"[OK] contract_version={version}")
    print(f"[OK] is_compatible={is_compatible}")


if __name__ == "__main__":
    main()
