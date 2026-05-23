#!/usr/bin/env python3
"""Validate reduced branch-Jacobian source specification."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_v1"


def main() -> int:
    paths = [
        EVIDENCE / "p_taucov_reduced_branch_jacobian_source_spec.csv",
        EVIDENCE / "p_taucov_reduced_branch_jacobian_source_spec_summary.csv",
        DOCS / "p_taucov_reduced_branch_jacobian_source_spec.md",
    ]
    for p in paths:
        if not p.exists():
            raise SystemExit(f"Missing artifact: {p}")
    df = pd.read_csv(paths[0])
    summary = pd.read_csv(paths[1])
    if len(summary) != 1:
        raise SystemExit("Expected one summary row")
    row = summary.iloc[0]
    if row["FreezeID"] != FREEZE_ID:
        raise SystemExit("Unexpected FreezeID")
    for col in ["ObjectConstructed", "ScoringAuthorized", "SurvivalClaimAuthorized", "TauCoreValidationClaimAuthorized"]:
        if bool(row[col]):
            raise SystemExit(f"{col} must be false")
    blockers = int(df["BlocksJacobian"].astype(bool).sum())
    expected = (
        "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_BLOCKED_NO_OBJECT_NO_SCORING"
        if blockers
        else "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_READY_NO_OBJECT_NO_SCORING"
    )
    if row["Status"] != expected:
        raise SystemExit("Unexpected status")
    if "Q_range" not in set(df["ObjectID"]):
        raise SystemExit("Q_range source is required")
    if not (df.loc[df["ObjectID"] == "Q_range", "CurrentStatus"] == "FROZEN_AVAILABLE").any():
        raise SystemExit("Q_range must be frozen available")
    pd.DataFrame(
        [
            {
                "FreezeID": FREEZE_ID,
                "ValidationStatus": "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_VALID",
                "SpecStatus": row["Status"],
                "BlockingObjects": blockers,
                "ScoringAuthorized": False,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_reduced_branch_jacobian_source_spec_validation.csv", index=False)
    print("P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
