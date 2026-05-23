#!/usr/bin/env python3
"""Validate reference-state candidate spec."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_REFERENCE_STATE_CANDIDATE_SPEC_v1"


def main() -> int:
    paths = [
        EVIDENCE / "p_taucov_reference_state_candidate_spec.csv",
        EVIDENCE / "p_taucov_reference_state_candidate_spec_summary.csv",
        DOCS / "p_taucov_reference_state_candidate_spec.md",
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
    if bool(row["JacobianBuildAuthorized"]) or bool(row["ScoringAuthorized"]):
        raise SystemExit("Spec must not authorize Jacobian build or scoring")
    if int(row["ReferenceStatesFrozen"]) != 0:
        raise SystemExit("Spec must not freeze final reference state")
    if "RS_ORIGIN_ACTIVE_SCAFFOLD" not in set(df["CandidateID"]):
        raise SystemExit("Active scaffold origin candidate is required")
    for col in ["UsesTargetResiduals", "UsesScoreOutcomes", "ScoringAuthorized", "SurvivalClaimAuthorized", "TauCoreValidationClaimAuthorized"]:
        if df[col].astype(bool).any():
            raise SystemExit(f"{col} must be false for all rows")
    pd.DataFrame(
        [
            {
                "FreezeID": FREEZE_ID,
                "ValidationStatus": "P_TAUCOV_REFERENCE_STATE_CANDIDATE_SPEC_VALID",
                "SpecStatus": row["Status"],
                "CandidatesDefined": len(df),
                "ReferenceStatesFrozen": 0,
                "ScoringAuthorized": False,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_reference_state_candidate_spec_validation.csv", index=False)
    print("P_TAUCOV_REFERENCE_STATE_CANDIDATE_SPEC_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
