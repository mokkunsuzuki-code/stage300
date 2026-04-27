#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    demo_path = Path("demo/ai_vulnerability_output.json")
    manifest_path = Path("examples/stage300_accept_manifest.json")

    manifest = {
        "subject": "Stage300 AI vulnerability verification demo",
        "stage": 300,
        "evidence_type": "ai-vulnerability-url",
        "verification_url": "https://mokkunsuzuki-code.github.io/stage300/",
        "content_file": str(demo_path),
        "content_sha256": sha256_file(demo_path),
        "signature_valid": True,
        "source_note": "Safe simulated AI vulnerability evidence for public demo.",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
