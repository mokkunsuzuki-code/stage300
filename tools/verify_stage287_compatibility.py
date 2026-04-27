#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "out" / "compatibility" / "compatibility_report.json"


def main() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert report["stage"] == "stage287", "stage must be stage287"
    assert isinstance(report["is_compatible"], bool), "is_compatible must be bool"
    assert len(report["checks"]) > 0, "checks must not be empty"
    assert all("passed" in check for check in report["checks"]), "each check must contain passed"
    assert report["is_compatible"] is True, "contract must be compatible"

    print("[OK] stage287 compatibility verified")
    print(f"[OK] contract_version: {report['contract_version']}")
    print(f"[OK] is_compatible: {report['is_compatible']}")
    print(f"[OK] checks: {len(report['checks'])}")


if __name__ == "__main__":
    main()
