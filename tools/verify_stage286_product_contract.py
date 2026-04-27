#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Stage286 product contract")
    parser.add_argument(
        "--contract",
        default="out/product/qsp_product_contract.json",
        help="Path to the generated contract JSON"
    )
    parser.add_argument(
        "--sha256",
        default="out/product/qsp_product_contract.json.sha256",
        help="Path to the sha256 file"
    )
    args = parser.parse_args()

    contract_path = Path(args.contract)
    sha256_path = Path(args.sha256)

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    actual_digest = sha256_file(contract_path)

    expected_line = sha256_path.read_text(encoding="utf-8").strip()
    expected_digest = expected_line.split()[0]

    assert contract["stage"] == "stage286", "stage must be stage286"
    assert contract["input_layer"]["policy"]["fail_closed_required"] is True, "fail_closed_required must be true"
    assert contract["decision_layer"]["decision"] in {"accept", "pending", "reject"}, "invalid decision"
    assert contract["enforcement_layer"]["fail_closed"] is True, "fail_closed must be true"
    assert contract["exposure_layer"]["public_status"] == contract["decision_layer"]["decision"], \
        "public_status must match decision"
    assert expected_digest == actual_digest, "sha256 mismatch"

    print("[OK] stage286 product contract verified")
    print(f"[OK] stage: {contract['stage']}")
    print(f"[OK] decision: {contract['decision_layer']['decision']}")
    print(f"[OK] fail_closed: {contract['enforcement_layer']['fail_closed']}")
    print(f"[OK] sha256: {actual_digest}")


if __name__ == "__main__":
    main()
