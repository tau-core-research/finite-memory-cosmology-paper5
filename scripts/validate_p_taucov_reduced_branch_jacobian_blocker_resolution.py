#!/usr/bin/env python3
"""Validate reduced branch-Jacobian blocker resolution audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_BLOCKER_RESOLUTION_v1"


def main() -> int:
    paths = [
        EVIDENCE / "p_taucov_reduced_branch_jacobian_blocker_resolution.csv",
        EVIDENCE / "p_taucov_reduced_branch_jacobian_blocker_resolution_summary.csv",
        DOCS / "p_taucov_reduced_branch_jacobian_blocker_resolution.md",
    ]
    for path in paths:
        if not path.exists():
            raise SystemExit(f"Missing artifact: {path}")
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
    blockers = int(df["StillBlocks"].astype(bool).sum())
    if int(row["RemainingBlockers"]) != blockers:
        raise SystemExit("Remaining blocker count mismatch")
    if "P_red" not in set(df["ObjectID"]):
        raise SystemExit("P_red row required")
    pred = df[df["ObjectID"] == "P_red"].iloc[0]
    if bool(pred["StillBlocks"]):
        raise SystemExit("P_red should not still block after full-action-domain packet")
    pd.DataFrame(
        [
            {
                "FreezeID": FREEZE_ID,
                "ValidationStatus": "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_BLOCKER_RESOLUTION_VALID",
                "ResolutionStatus": row["Status"],
                "RemainingBlockers": blockers,
                "ScoringAuthorized": False,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_reduced_branch_jacobian_blocker_resolution_validation.csv", index=False)
    print("P_TAUCOV_REDUCED_BRANCH_JACOBIAN_BLOCKER_RESOLUTION_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
