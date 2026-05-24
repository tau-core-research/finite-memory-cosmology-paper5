#!/usr/bin/env python3
"""Freeze compact spectral df/covariance policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_compact_spectral_df_covariance_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_df_covariance_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_compact_spectral_df_covariance_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_COMPACT_SPECTRAL_DF_COVARIANCE_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "compact_spectral_df_covariance_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("PARAM_ALPHA", "degrees_of_freedom", "single scalar alpha for C=C0+alpha*K_compact_spectral", "1"),
        ("KERNEL_POLICY", "kernel", "primary kernel is the frozen compact spectral residue source", "PSD_or_symmetric_covariance_deformation"),
        ("SPECTRAL_SELECTION_DF", "claim_boundary", "selected modes are frozen source construction and do not add fitted df", "df_unchanged"),
        ("COVARIANCE_REGULARIZATION", "regularization", "use predeclared ridge/jitter only if numerically required", "scorecard_declared"),
        ("INFORMATION_CRITERION", "model_comparison", "AIC and BIC count df=1 for the compact spectral deformation", "df_1"),
        ("NO_SECONDARY_RESCUE", "claim_boundary", "diagnostic contrasts cannot rescue failed primary covariance score", "forbidden"),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "PolicyID": policy_id,
                "PolicyClass": policy_class,
                "Definition": definition,
                "FrozenValue": value,
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for policy_id, policy_class, definition, value in rows
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_COMPACT_SPECTRAL_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING",
                "PolicyRows": len(table),
                "DeclaredDF": 1,
                "PrimaryKernelPolicy": "compact_spectral_residue_covariance_deformation",
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        """# P-TauCov Compact Spectral DF/Covariance Policy

Status: `P_TAUCOV_COMPACT_SPECTRAL_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING`.

If authorized later, the primary scorecard is a one-parameter covariance
deformation test. The compact spectral mode selection is frozen source
construction, not fitted degrees of freedom, so information-criterion
accounting remains `df=1`.
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_COMPACT_SPECTRAL_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
