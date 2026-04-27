#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict


@dataclass
class GateResult:
    stage: int
    decision: str
    reason: str
    verification_ok: bool
    signature_valid: bool
    fail_closed: bool
    trust_score: float
    manifest_sha256: str


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_manifest(manifest: Dict[str, Any]) -> bool:
    required = ["subject", "evidence_type", "verification_url", "content_sha256"]

    for field in required:
        if not manifest.get(field):
            return False

    digest = str(manifest.get("content_sha256", ""))

    if len(digest) != 64:
        return False

    try:
        int(digest, 16)
    except ValueError:
        return False

    return True


def run_gate(manifest_path: Path) -> GateResult:
    manifest = load_json(manifest_path)

    verification_ok = verify_manifest(manifest)
    signature_valid = bool(manifest.get("signature_valid") is True)
    fail_closed = True

    if verification_ok and signature_valid:
        decision = "accept"
        reason = "Evidence is valid and signature is valid."
        trust_score = 1.0
    elif verification_ok:
        decision = "pending"
        reason = "Evidence is valid, but signature is missing or not yet verified."
        trust_score = 0.6
    else:
        decision = "reject"
        reason = "Evidence is invalid. Fail-closed Gate rejected the input."
        trust_score = 0.0

    return GateResult(
        stage=299,
        decision=decision,
        reason=reason,
        verification_ok=verification_ok,
        signature_valid=signature_valid,
        fail_closed=fail_closed,
        trust_score=trust_score,
        manifest_sha256=sha256_file(manifest_path),
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Stage299 Signature-Aware Gate")
    parser.add_argument("manifest")
    parser.add_argument("--out", default="stage299_gate_result.json")
    args = parser.parse_args()

    result = run_gate(Path(args.manifest))

    Path(args.out).write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    print(json.dumps(asdict(result), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
