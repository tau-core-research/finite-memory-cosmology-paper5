#!/usr/bin/env python3
"""Validate the Q-range projector freeze."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_v1"


def main() -> int:
    required = [
        EVIDENCE / "p_taucov_q_range_projector_matrix.csv",
        EVIDENCE / "p_taucov_q_range_projector_summary.csv",
        EVIDENCE / "p_taucov_q_range_projector_gates.csv",
        EVIDENCE / "p_taucov_q_range_projector_spectrum.csv",
        DOCS / "p_taucov_q_range_projector_freeze.md",
    ]
    for path in required:
        if not path.exists():
            raise SystemExit(f"Missing required artifact: {path}")
    summary = pd.read_csv(EVIDENCE / "p_taucov_q_range_projector_summary.csv")
    gates = pd.read_csv(EVIDENCE / "p_taucov_q_range_projector_gates.csv")
    if len(summary) != 1:
        raise SystemExit("Expected one summary row")
    row = summary.iloc[0]
    if row["FreezeID"] != FREEZE_ID:
        raise SystemExit("Unexpected FreezeID")
    for col in ["ObjectConstructed", "ScoringAuthorized", "SurvivalClaimAuthorized", "TauCoreValidationClaimAuthorized"]:
        if bool(row[col]):
            raise SystemExit(f"{col} must be false")
    passed = int(gates["Passed"].astype(bool).sum())
    total = int(len(gates))
    expected = "P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_PASS_NO_SCORING" if passed == total else "P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_FAIL_NO_SCORING"
    if row["Status"] != expected:
        raise SystemExit("Unexpected status")
    if int(row["PassedGates"]) != passed or int(row["TotalGates"]) != total:
        raise SystemExit("Gate counts mismatch")
    pd.DataFrame(
        [
            {
                "FreezeID": FREEZE_ID,
                "ValidationStatus": "P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_VALID",
                "FreezeStatus": row["Status"],
                "ActiveRank": int(row["ActiveRank"]),
                "ScoringAuthorized": False,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_range_projector_validation.csv", index=False)
    print("P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
