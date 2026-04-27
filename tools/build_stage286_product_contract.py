#!/usr/bin/env python3
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = ROOT / "spec" / "qsp_product_spec.json"
OUT_DIR = ROOT / "out" / "product"
CONTRACT_PATH = OUT_DIR / "qsp_product_contract.json"
SHA256_PATH = OUT_DIR / "qsp_product_contract.json.sha256"


def canonical_json_bytes(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

    contract = {
        "stage": "stage286",
        "spec_version": spec["version"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_layer": {
            "session_id": "qsp-session-stage286-demo",
            "subject": "QSP internal product connection",
            "policy": {
                "policy_id": "qsp-product-policy-v1",
                "fail_closed_required": True
            },
            "evidence": {
                "integrity": {
                    "sha256_present": True,
                    "manifest_bound": True
                },
                "execution": {
                    "workflow_evidence_present": True,
                    "ci_reproducible": True
                },
                "identity": {
                    "signature_present": True,
                    "issuer_bound": True
                },
                "time": {
                    "ots_present": True,
                    "settlement_status": "pending_or_complete"
                }
            }
        },
        "decision_layer": {
            "decision": "accept",
            "reason": "QSP internal product contract is well-formed and all required trust dimensions are represented.",
            "scores": {
                "integrity_trust": 1.0,
                "execution_trust": 1.0,
                "identity_trust": 1.0,
                "time_trust": 0.5,
                "total_trust": 0.5
            },
            "verified_claims": [
                "QSP decision is normalized before exposure",
                "Fail-closed state is part of the product contract",
                "VEP consumes a stable export contract"
            ]
        },
        "enforcement_layer": {
            "fail_closed": True,
            "execution_state": "released",
            "allowed_outputs": [
                "normalized_contract",
                "public_verification_artifacts",
                "verification_page_inputs"
            ]
        },
        "exposure_layer": {
            "public_status": "accept",
            "exposure_artifacts": [
                "release_manifest.json",
                "release_manifest.json.sha256",
                "github_actions_receipt.json",
                "public_verification_url"
            ],
            "contract_sha256": ""
        }
    }

    partial_bytes = canonical_json_bytes(contract)
    digest = sha256_hex(partial_bytes)
    contract["exposure_layer"]["contract_sha256"] = digest

    final_bytes = canonical_json_bytes(contract)
    final_digest = sha256_hex(final_bytes)

    CONTRACT_PATH.write_bytes(final_bytes)
    SHA256_PATH.write_text(f"{final_digest}  {CONTRACT_PATH.name}\n", encoding="utf-8")

    print(f"[OK] wrote {CONTRACT_PATH}")
    print(f"[OK] wrote {SHA256_PATH}")
    print(f"[OK] contract sha256={final_digest}")


if __name__ == "__main__":
    main()
