#!/usr/bin/env python3
"""Parent-action P-TauCov scorecard entrypoint.

This script is intentionally inert until a final authorization manifest exists.
It is created now so its source can be hashed before any empirical scorecard
execution is allowed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "evidence/p_taucov_parent_action_final_manifest.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the parent-action P-TauCov scorecard only after final authorization.")
    parser.add_argument("--authorization-manifest", default=str(DEFAULT_MANIFEST), help="Final authorization manifest path.")
    parser.add_argument("--dry-run", action="store_true", help="Report authorization state without scoring.")
    args = parser.parse_args()

    manifest = Path(args.authorization_manifest)
    if args.dry_run:
        print("P_TAUCOV_PARENT_ACTION_SCORECARD_DRY_RUN_NO_SCORING")
        print(f"authorization_manifest_exists={manifest.exists()}")
        return 0
    if not manifest.exists():
        print("P_TAUCOV_PARENT_ACTION_SCORECARD_BLOCKED_MISSING_FINAL_MANIFEST")
        return 2
    print("P_TAUCOV_PARENT_ACTION_SCORECARD_BLOCKED_IMPLEMENTATION_PENDING")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
