#!/usr/bin/env python3
"""Freeze PB zero-diagonal df/covariance policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_pb_zero_diagonal_df_covariance_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_pb_zero_diagonal_df_covariance_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_pb_zero_diagonal_df_covariance_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_DF_COVARIANCE_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "pb_zero_diagonal_df_covariance_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("PARAM_ALPHA", "degrees_of_freedom", "single scalar alpha for C=C0+alpha*K_pb_zero_diagonal", "1"),
        ("KERNEL_POLICY", "kernel", "primary kernel is frozen PB zero-diagonal covariance-response object", "symmetric_offdiagonal_covariance_deformation"),
        ("ZERO_DIAGONAL_POLICY", "claim_boundary", "zero diagonal is frozen source construction and does not add fitted df", "df_unchanged"),
        ("COVARIANCE_REGULARIZATION", "regularization", "use predeclared ridge/jitter only if numerically required", "scorecard_declared"),
        ("INFORMATION_CRITERION", "model_comparison", "AIC and BIC count df=1 for PB zero-diagonal deformation", "df_1"),
        ("NO_DIAGNOSTIC_RESCUE", "claim_boundary", "cleaned/family-masked diagnostics cannot rescue failed primary score", "forbidden"),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "PolicyID": pid,
                "PolicyClass": cls,
                "Definition": definition,
                "FrozenValue": value,
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for pid, cls, definition, value in rows
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PB_ZERO_DIAGONAL_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING",
                "PolicyRows": len(table),
                "DeclaredDF": 1,
                "PrimaryKernelPolicy": "pb_zero_diagonal_covariance_deformation",
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "# P-TauCov PB Zero-Diagonal DF/Covariance Policy\n\n"
        "Status: `P_TAUCOV_PB_ZERO_DIAGONAL_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING`.\n\n"
        "If authorized later, the primary scorecard is a one-parameter covariance\n"
        "deformation test with `df=1`. Zero diagonal is frozen source construction,\n"
        "not an additional fitted degree of freedom.\n",
        encoding="utf-8",
    )
    print("P_TAUCOV_PB_ZERO_DIAGONAL_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
