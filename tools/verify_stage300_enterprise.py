#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_sha256(value: str) -> bool:
    if len(value) != 64:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def verify_gpg(manifest_path: Path, sig_path: Path | None) -> tuple[bool, str]:
    if sig_path is None:
        return False, "No signature file provided."

    if not sig_path.exists():
        return False, "Signature file does not exist."

    result = subprocess.run(
        ["gpg", "--verify", str(sig_path), str(manifest_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode == 0:
        return True, "GPG signature verified successfully."

    return False, result.stderr.strip() or "GPG signature verification failed."


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage300 enterprise verifier")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--sig", required=False)
    parser.add_argument("--out", default="results/stage300_enterprise_result.json")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    content_path = Path(args.content)
    sig_path = Path(args.sig) if args.sig else None

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    actual_sha256 = sha256_file(content_path)
    expected_sha256 = manifest.get("content_sha256", "")

    hash_format_ok = is_sha256(expected_sha256)
    hash_match = actual_sha256 == expected_sha256

    gpg_valid, gpg_reason = verify_gpg(manifest_path, sig_path)

    verification_ok = bool(
        manifest.get("subject")
        and manifest.get("evidence_type")
        and manifest.get("verification_url")
        and hash_format_ok
        and hash_match
    )

    if verification_ok and gpg_valid:
        decision = "accept"
        trust_score = 1.0
        reason = "Content hash matches and GPG signature is valid."
    elif verification_ok:
        decision = "pending"
        trust_score = 0.75
        reason = "Content hash matches, but GPG signature is missing or invalid."
    else:
        decision = "reject"
        trust_score = 0.0
        reason = "Content hash verification failed or manifest is incomplete."

    result = {
        "stage": 300,
        "decision": decision,
        "trust_score": trust_score,
        "verification_ok": verification_ok,
        "content_sha256_expected": expected_sha256,
        "content_sha256_actual": actual_sha256,
        "hash_match": hash_match,
        "gpg_signature_valid": gpg_valid,
        "gpg_reason": gpg_reason,
        "fail_closed": True,
        "reason": reason,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
