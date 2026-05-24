#!/usr/bin/env python3
"""Blocked entrypoint for the PB zero-diagonal P-TauCov scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FINAL_MANIFEST = ROOT / "evidence/p_taucov_pb_zero_diagonal_final_manifest_summary.csv"
EXPECTED_STATUS = "P_TAUCOV_PB_ZERO_DIAGONAL_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM"


def main() -> int:
    if not FINAL_MANIFEST.exists():
        print("P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_BLOCKED_NO_FINAL_MANIFEST")
        return 1
    summary = pd.read_csv(FINAL_MANIFEST).iloc[0]
    if str(summary["Status"]) != EXPECTED_STATUS or not bool(summary["PTauCovScoringAuthorized"]):
        print("P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_BLOCKED_NOT_AUTHORIZED")
        return 1
    print("P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_AUTHORIZED_ENTRYPOINT_READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
