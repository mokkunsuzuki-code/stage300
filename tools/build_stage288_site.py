#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "out" / "product" / "qsp_product_contract.json"
COMPAT_PATH = ROOT / "out" / "compatibility" / "compatibility_report.json"
OUT_DIR = ROOT / "out" / "site"
OUT_PATH = OUT_DIR / "site_data.json"


def improved_reason(contract: dict) -> str:
    decision = contract.get("decision_layer", {}).get("decision")
    fail_closed = contract.get("enforcement_layer", {}).get("fail_closed")

    if decision == "accept" and fail_closed is True:
        return (
            "The product contract satisfies all required trust conditions "
            "and is enforced under a fail-closed execution model."
        )
    return contract.get("decision_layer", {}).get(
        "reason",
        "Verification status is available in the product contract."
    )


def verification_result(contract: dict, compatibility: dict) -> dict:
    decision = contract.get("decision_layer", {}).get("decision")
    compatible = compatibility.get("is_compatible", False)
    fail_closed = contract.get("enforcement_layer", {}).get("fail_closed", False)

    if decision == "accept" and compatible and fail_closed:
        return {
            "headline": "ACCEPTED",
            "subheadline": "SAFE TO EXECUTE",
            "status": "accept"
        }
    if decision == "pending":
        return {
            "headline": "PENDING",
            "subheadline": "REVIEW REQUIRED",
            "status": "pending"
        }
    return {
        "headline": "REJECTED",
        "subheadline": "DO NOT EXECUTE",
        "status": "reject"
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    compatibility = json.loads(COMPAT_PATH.read_text(encoding="utf-8"))

    result = verification_result(contract, compatibility)

    site_data = {
        "stage": "stage288",
        "page_stage": "stage288",
        "page_title": "Stage288 Compatibility-Aware Verification URL",
        "hero_title": "VERIFICATION RESULT",
        "hero_status": result["headline"],
        "hero_substatus": result["subheadline"],
        "hero_status_code": result["status"],
        "summary": (
            "This page publicly verifies a QSP product contract.\n\n"
            "It shows:\n"
            "- the contract (Stage286)\n"
            "- its compatibility guarantee (Stage287)\n"
            "- and its enforced decision (fail-closed)\n\n"
            "All in one stable verification interface (Stage288)."
        ),
        "contract": {
            "stage": contract.get("stage"),
            "spec_version": contract.get("spec_version"),
            "generated_at": contract.get("generated_at"),
            "decision": contract.get("decision_layer", {}).get("decision"),
            "reason": improved_reason(contract),
            "public_status": contract.get("exposure_layer", {}).get("public_status"),
            "fail_closed": contract.get("enforcement_layer", {}).get("fail_closed"),
            "execution_state": contract.get("enforcement_layer", {}).get("execution_state"),
            "contract_sha256": contract.get("exposure_layer", {}).get("contract_sha256"),
            "exposure_artifacts": contract.get("exposure_layer", {}).get("exposure_artifacts", [])
        },
        "compatibility": {
            "stage": "stage287",
            "policy_id": compatibility.get("policy_id"),
            "contract_version": compatibility.get("contract_version"),
            "is_compatible": compatibility.get("is_compatible"),
            "checks": compatibility.get("checks", [])
        }
    }

    OUT_PATH.write_text(
        json.dumps(site_data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    print(f"[OK] wrote {OUT_PATH}")
    print(f"[OK] hero_status={site_data['hero_status']}")
    print(f"[OK] hero_substatus={site_data['hero_substatus']}")
    print(f"[OK] page_stage={site_data['page_stage']}")
    print(f"[OK] contract_stage={site_data['contract']['stage']}")
    print(f"[OK] compatibility_stage={site_data['compatibility']['stage']}")


if __name__ == "__main__":
    main()
