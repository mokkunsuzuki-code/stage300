#!/usr/bin/env python3
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent.parent
SITE_JSON = ROOT / "out" / "site" / "site_data.json"
WEB_JSON = ROOT / "web" / "site_data.json"


def main() -> None:
    if not SITE_JSON.exists():
        raise SystemExit("site_data.json does not exist. Run build_stage288_site.py first.")

    shutil.copy2(SITE_JSON, WEB_JSON)
    print(f"[OK] copied {SITE_JSON} -> {WEB_JSON}")


if __name__ == "__main__":
    main()
