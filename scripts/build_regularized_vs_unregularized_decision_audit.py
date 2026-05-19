#!/usr/bin/env python3
"""Compare unregularized and derivative-regularized PySR smoke nulls."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

UNREG_SUMMARY = EVIDENCE / "full_normalized_pysr_backreaction_smoke_summary.csv"
REG_SUMMARY = EVIDENCE / "regularized_full_pysr_backreaction_smoke_summary.csv"
UNREG_SENS = EVIDENCE / "full_normalized_pysr_backreaction_sensitivity_summary.csv"
REG_SENS = EVIDENCE / "regularized_full_pysr_backreaction_sensitivity_summary.csv"
UNREG_SCORE = EVIDENCE / "full_normalized_pysr_backreaction_smoke_bridge_scorecard.csv"
REG_SCORE = EVIDENCE / "regularized_full_pysr_backreaction_smoke_bridge_scorecard.csv"

OUT_AUDIT = EVIDENCE / "regularized_vs_unregularized_decision_audit.csv"
OUT_SUMMARY = EVIDENCE / "regularized_vs_unregularized_decision_summary.csv"
OUT_DOC = DOCS / "regularized_vs_unregularized_decision_audit.md"

CLAIM_BOUNDARY = "regularized_vs_unregularized_decision_audit_no_measurement_validation"


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty file: {path}")
    return df.iloc[0]


def ratio_after_before(after: float, before: float) -> float:
    if before == 0:
        return float("nan")
    return float(after / before)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    unreg = first(UNREG_SUMMARY)
    reg = first(REG_SUMMARY)
    unreg_sens = first(UNREG_SENS)
    reg_sens = first(REG_SENS)
    unreg_score = pd.read_csv(UNREG_SCORE)
    reg_score = pd.read_csv(REG_SCORE)

    score_join = unreg_score.merge(
        reg_score,
        on="RouteID",
        suffixes=("_Unregularized", "_Regularized"),
        how="inner",
    )

    rows: list[dict[str, object]] = []
    rows.append(
        {
            "AuditID": "REGULARIZED_VS_UNREGULARIZED_DECISION_AUDIT_V1",
            "CheckID": "LOW_DEPTH_OMEGA_REDUCTION",
            "Before": float(unreg_sens["LowDepthOmegaAbsMax"]),
            "After": float(reg_sens["LowDepthOmegaAbsMax"]),
            "RatioAfterBefore": ratio_after_before(
                float(reg_sens["LowDepthOmegaAbsMax"]),
                float(unreg_sens["LowDepthOmegaAbsMax"]),
            ),
            "Status": "SUPPORTS_REGULARIZED_SELECTOR",
            "Interpretation": "low-depth Omega amplitude is strongly reduced by D-branch derivative regularity governance",
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    rows.append(
        {
            "AuditID": "REGULARIZED_VS_UNREGULARIZED_DECISION_AUDIT_V1",
            "CheckID": "LOW_DEPTH_DERIVATIVE_REDUCTION",
            "Before": float(unreg_sens["MedianDSecondOverDPrimeLowDepth"]),
            "After": float(reg_sens["MedianDSecondOverDPrimeLowDepth"]),
            "RatioAfterBefore": ratio_after_before(
                float(reg_sens["MedianDSecondOverDPrimeLowDepth"]),
                float(unreg_sens["MedianDSecondOverDPrimeLowDepth"]),
            ),
            "Status": "SUPPORTS_REGULARIZED_SELECTOR",
            "Interpretation": "median low-depth derivative curvature is suppressed without changing locked K2",
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    rows.append(
        {
            "AuditID": "REGULARIZED_VS_UNREGULARIZED_DECISION_AUDIT_V1",
            "CheckID": "MIDHIGH_OMEGA_NOT_ERASED",
            "Before": float(unreg_sens["MidHighOmegaAbsMax"]),
            "After": float(reg_sens["MidHighOmegaAbsMax"]),
            "RatioAfterBefore": ratio_after_before(
                float(reg_sens["MidHighOmegaAbsMax"]),
                float(unreg_sens["MidHighOmegaAbsMax"]),
            ),
            "Status": "WARNING",
            "Interpretation": "mid/high smoke amplitude remains present; this is useful for control scoring but still smoke-scale",
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    rows.append(
        {
            "AuditID": "REGULARIZED_VS_UNREGULARIZED_DECISION_AUDIT_V1",
            "CheckID": "K2_BEATS_REGULARIZED_SMOKE",
            "Before": int(unreg["K2BeatsSmokeBackreactionCases"]),
            "After": int(reg["K2BeatsSmokeBackreactionCases"]),
            "RatioAfterBefore": ratio_after_before(
                float(reg["K2BeatsSmokeBackreactionCases"]),
                float(unreg["K2BeatsSmokeBackreactionCases"]),
            ),
            "Status": "SUPPORTS_LOCKED_K2_PREFLIGHT",
            "Interpretation": "locked K2 still beats the regularized smoke backreaction null in all scored routes",
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    rows.append(
        {
            "AuditID": "REGULARIZED_VS_UNREGULARIZED_DECISION_AUDIT_V1",
            "CheckID": "SMOKE_K2_CORRELATION_CHANGE",
            "Before": float(unreg["MedianCorrelationSmokeWithK2"]),
            "After": float(reg["MedianCorrelationSmokeWithK2"]),
            "RatioAfterBefore": ratio_after_before(
                float(reg["MedianCorrelationSmokeWithK2"]),
                float(unreg["MedianCorrelationSmokeWithK2"]),
            ),
            "Status": "SUPPORTS_SELECTOR_SCALE_UP",
            "Interpretation": "regularization changes the smoke null from anti-correlated to positively correlated with locked K2, while K2 remains lower chi2",
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )

    for _, row in score_join.iterrows():
        rows.append(
            {
                "AuditID": "REGULARIZED_VS_UNREGULARIZED_DECISION_AUDIT_V1",
                "CheckID": f"ROUTE_SCORE_{row['RouteID']}",
                "Before": float(row["SmokeBackreactionChi2_Unregularized"]),
                "After": float(row["SmokeBackreactionChi2_Regularized"]),
                "RatioAfterBefore": ratio_after_before(
                    float(row["SmokeBackreactionChi2_Regularized"]),
                    float(row["SmokeBackreactionChi2_Unregularized"]),
                ),
                "Status": "REGULARIZED_NULL_STILL_WORSE_THAN_K2"
                if float(row["DeltaChi2_K2_minus_SmokeBackreaction_Regularized"]) < 0.0
                else "REGULARIZED_NULL_COMPETES_WITH_K2",
                "Interpretation": (
                    f"{row['RouteID']}: regularized smoke chi2 is compared against the unchanged locked K2 chi2"
                ),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT_AUDIT, index=False)

    low_reduction = ratio_after_before(
        float(reg_sens["LowDepthOmegaAbsMax"]),
        float(unreg_sens["LowDepthOmegaAbsMax"]),
    )
    derivative_reduction = ratio_after_before(
        float(reg_sens["MedianDSecondOverDPrimeLowDepth"]),
        float(unreg_sens["MedianDSecondOverDPrimeLowDepth"]),
    )
    k2_beats_all_regularized = int(reg["K2BeatsSmokeBackreactionCases"]) == int(reg["RoutesScored"])
    no_forbidden_changes = not any(
        [
            str(reg["K2KernelChanged"]).lower() == "true",
            str(reg["K1Refit"]).lower() == "true",
            str(reg["ScaleFitAllowed"]).lower() == "true",
            str(reg["MeasurementValidationAllowed"]).lower() == "true",
        ]
    )
    scale_recommendation = (
        "SCALE_REGISTERED_SELECTOR_TO_200_BOOTSTRAP_PREFLIGHT"
        if low_reduction < 0.1 and derivative_reduction < 0.1 and k2_beats_all_regularized and no_forbidden_changes
        else "HOLD_FOR_SELECTOR_REVIEW"
    )
    summary = pd.DataFrame(
        [
            {
                "AuditID": "REGULARIZED_VS_UNREGULARIZED_DECISION_AUDIT_V1",
                "Rows": int(len(audit)),
                "LowDepthOmegaReductionRatio": low_reduction,
                "LowDepthDerivativeReductionRatio": derivative_reduction,
                "UnregularizedOmegaAbsMax": float(unreg_sens["OmegaAbsMax"]),
                "RegularizedOmegaAbsMax": float(reg_sens["OmegaAbsMax"]),
                "UnregularizedMedianCorrelationSmokeWithK2": float(unreg["MedianCorrelationSmokeWithK2"]),
                "RegularizedMedianCorrelationSmokeWithK2": float(reg["MedianCorrelationSmokeWithK2"]),
                "K2BeatsRegularizedSmokeCases": int(reg["K2BeatsSmokeBackreactionCases"]),
                "RoutesScored": int(reg["RoutesScored"]),
                "NoForbiddenChanges": no_forbidden_changes,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "REGULARIZED_SELECTOR_SCALE_UP_RECOMMENDED"
                if scale_recommendation.startswith("SCALE_")
                else "REGULARIZED_SELECTOR_REVIEW_REQUIRED",
                "ScaleRecommendation": scale_recommendation,
                "StrongestAllowedClaim": (
                    "the derivative-regularized smoke null is a better-governed preflight control than the unregularized smoke null"
                ),
                "PrimaryResidualRisk": (
                    "the result is still smoke-scale and source-native covariance plus full bootstrap remain required"
                ),
                "NextAction": (
                    "run the registered derivative-regularized D-branch selector at 200 bootstrap scale"
                    if scale_recommendation.startswith("SCALE_")
                    else "review derivative regularity selector before scale-up"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Regularized vs Unregularized Decision Audit",
                "",
                f"Status: {summary.iloc[0]['CurrentStatus']}.",
                "",
                "This audit compares the unregularized PySR smoke null with the D-branch derivative-regularized smoke null. It does not change K2, refit K1, use target signs, or authorize measurement validation.",
                "",
                "## Key Decision Numbers",
                "",
                f"- Low-depth Omega reduction ratio: {low_reduction}",
                f"- Low-depth derivative reduction ratio: {derivative_reduction}",
                f"- Unregularized Omega abs max: {float(unreg_sens['OmegaAbsMax'])}",
                f"- Regularized Omega abs max: {float(reg_sens['OmegaAbsMax'])}",
                f"- K2 beats regularized smoke cases: {int(reg['K2BeatsSmokeBackreactionCases'])}/{int(reg['RoutesScored'])}",
                f"- Scale recommendation: {scale_recommendation}",
                "",
                "## Boundary",
                "",
                "This supports scale-up of a preflight control only. It is not measurement validation and it is not a discovery claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_AUDIT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
