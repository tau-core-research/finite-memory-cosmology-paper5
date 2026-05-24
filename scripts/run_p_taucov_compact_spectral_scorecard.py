#!/usr/bin/env python3
"""Blocked compact spectral P-TauCov scorecard entrypoint."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_final_manifest_summary.csv"
AUTHORIZED_STATUS = "P_TAUCOV_COMPACT_SPECTRAL_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM"


def main() -> int:
    if not MANIFEST_SUMMARY.exists():
        print("P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_BLOCKED_NO_FINAL_MANIFEST")
        return 1
    summary = pd.read_csv(MANIFEST_SUMMARY).iloc[0]
    if str(summary["Status"]) != AUTHORIZED_STATUS or not bool(summary["PTauCovScoringAuthorized"]):
        print("P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_BLOCKED_NOT_AUTHORIZED")
        return 1
    print("P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_AUTHORIZED_BUT_NOT_IMPLEMENTED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
