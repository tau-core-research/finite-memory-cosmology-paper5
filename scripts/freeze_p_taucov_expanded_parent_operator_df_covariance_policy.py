#!/usr/bin/env python3
"""Freeze expanded parent-operator df/covariance policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_df_covariance_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_df_covariance_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_df_covariance_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DF_COVARIANCE_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "expanded_parent_operator_df_covariance_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("PARAM_ALPHA", "degrees_of_freedom", "single scalar alpha for C=C0+alpha*K_expanded", "1"),
        ("KERNEL_POLICY", "kernel", "primary kernel is the frozen expanded parent-operator PSD candidate", "PSD"),
        ("EXPANDED_AXIS_DF", "claim_boundary", "scale/context axes are frozen source axes and do not add fitted df", "df_unchanged"),
        ("COVARIANCE_REGULARIZATION", "regularization", "use predeclared ridge/jitter only if numerically required", "scorecard_declared"),
        ("INFORMATION_CRITERION", "model_comparison", "AIC and BIC count df=1 for the expanded deformation", "df_1"),
        ("NO_SECONDARY_RESCUE", "claim_boundary", "diagnostic contrasts cannot rescue failed primary covariance score", "forbidden"),
    ]
    policy = pd.DataFrame(
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
    policy.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING",
                "PolicyRows": len(policy),
                "DeclaredDF": 1,
                "PrimaryKernelPolicy": "PSD",
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        """# P-TauCov Expanded Parent-Operator DF/Covariance Policy

Status: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING`.

The future primary scorecard, if authorized, is a one-parameter covariance
deformation test:

```math
C = C_0 + \\alpha K_{\\rm expanded}.
```

The scale/context axes are frozen source axes, not fitted parameters, so
information-criterion accounting remains `df=1`. This policy does not
authorize scoring.
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
