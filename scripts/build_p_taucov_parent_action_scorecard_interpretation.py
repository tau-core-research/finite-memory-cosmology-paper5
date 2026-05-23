#!/usr/bin/env python3
"""Build interpretation note for parent-action P-TauCov scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_IN = ROOT / "evidence/p_taucov_parent_action_scorecard_summary.csv"
OUT = ROOT / "evidence/p_taucov_parent_action_scorecard_interpretation.csv"
DOC = ROOT / "docs/p_taucov_parent_action_scorecard_interpretation.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
INTERPRETATION_ID = "P_TAUCOV_PARENT_ACTION_SCORECARD_INTERPRETATION_v1"
CLAIM_BOUNDARY = "parent_action_primary_scorecard_interpretation_no_survival_claim"


def main() -> int:
    summary = pd.read_csv(SUMMARY_IN).iloc[0]
    primary_delta = float(summary["PrimaryOOSDeltaNLL_BaselineMinusKernel"])
    status = (
        "P_TAUCOV_PARENT_ACTION_PRIMARY_SCORECARD_POSITIVE_NO_SURVIVAL_CLAIM"
        if primary_delta > 0.0
        else "P_TAUCOV_PARENT_ACTION_PRIMARY_SCORECARD_NEGATIVE_NO_SURVIVAL_CLAIM"
    )
    interpretation = (
        "minimal_parent_action_psd_kernel_improves_primary_oos_but_null_survival_not_tested"
        if primary_delta > 0.0
        else "minimal_parent_action_psd_kernel_does_not_improve_primary_oos"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "InterpretationID": INTERPRETATION_ID,
                "Status": status,
                "PrimaryOOSDeltaNLL_BaselineMinusKernel": primary_delta,
                "Interpretation": interpretation,
                "SurvivalClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Action Scorecard Interpretation",
                "",
                f"Status: `{status}`.",
                "",
                f"- primary OOS DeltaNLL baseline-minus-kernel: `{primary_delta}`",
                "",
                "The first authorized parent-action primary covariance scorecard is",
                "negative: the minimal two-coordinate PSD lift does not improve the",
                "primary out-of-sample covariance likelihood over the baseline.",
                "",
                "This is not a Tau Core falsification. It is a failure of this minimal",
                "parent-action PSD scorecard candidate. It leaves open richer branch",
                "support, different admissible projection maps, and independently",
                "frozen response constructions.",
                "",
                "No survival claim or measurement-validation claim is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
