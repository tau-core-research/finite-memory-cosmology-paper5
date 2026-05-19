#!/usr/bin/env python3
"""Audit PySR criteria-set-3 penalty normalization.

The upstream text says to select by Loss + Penalty * Complexity with penalty
1.0. The structured smoke run shows that raw penalty-one selects a constant
even when a much lower-loss nonconstant candidate is available. This script
does not alter the registered K2/A2 model or pick a new source-native result.
It records the scale issue and the governance choices needed before bootstrap
source-native scoring.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

HOF = EVIDENCE / "pysr_criteria3_structured_hall_of_fame.csv"
STRUCTURED_SUMMARY = EVIDENCE / "pysr_criteria3_structured_smoke_summary.csv"

OUT_AUDIT = EVIDENCE / "pysr_penalty_normalization_audit.csv"
OUT_POLICY = EVIDENCE / "pysr_penalty_normalization_policy.csv"
OUT_SUMMARY = EVIDENCE / "pysr_penalty_normalization_summary.csv"
OUT_DOC = DOCS / "pysr_penalty_normalization_audit.md"

CLAIM_BOUNDARY = "pysr_penalty_normalization_audit_no_measurement_validation"


def selected_for_penalty(hof: pd.DataFrame, penalty: float) -> pd.Series:
    tmp = hof.copy()
    tmp["SelectionScore"] = tmp["loss"].astype(float) + penalty * tmp["complexity"].astype(float)
    return tmp.sort_values(["SelectionScore", "loss", "complexity"]).iloc[0]


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    hof = pd.read_csv(HOF)
    summary = pd.read_csv(STRUCTURED_SUMMARY).iloc[0]
    finite = hof[hof["FinitePrediction"].astype(bool)].copy()
    finite["IsConstant"] = finite["IsConstant"].astype(bool)

    constant = finite[finite["IsConstant"]].sort_values(["loss", "complexity"]).iloc[0]
    nonconstants = finite[~finite["IsConstant"]].copy()
    best_nonconstant = nonconstants.sort_values(["loss", "complexity"]).iloc[0]

    const_loss = float(constant["loss"])
    const_complexity = float(constant["complexity"])
    best_loss = float(best_nonconstant["loss"])
    best_complexity = float(best_nonconstant["complexity"])
    complexity_gap = best_complexity - const_complexity
    break_even_penalty = (const_loss - best_loss) / complexity_gap if complexity_gap > 0 else np.nan

    penalty_grid = [0.0, 0.001, 0.003, 0.005, 0.01, 0.03, 0.05, break_even_penalty, 0.1, 0.25, 0.5, 1.0]
    audit_rows = []
    for penalty in sorted({float(p) for p in penalty_grid if np.isfinite(p) and p >= 0}):
        selected = selected_for_penalty(finite, penalty)
        audit_rows.append(
            {
                "AuditID": "PYSR_PENALTY_NORMALIZATION_AUDIT_V1",
                "Penalty": penalty,
                "SelectedEquation": selected["equation"],
                "SelectedComplexity": int(selected["complexity"]),
                "SelectedLoss": float(selected["loss"]),
                "SelectedIsConstant": bool(selected["IsConstant"]),
                "SelectedWeightedMSEOriginal": float(selected["WeightedMSEOriginal"]),
                "SelectedPredictionStd": float(selected["PredictionStd"]),
                "BreakEvenPenaltyBestNonconstantVsConstant": break_even_penalty,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    pd.DataFrame(audit_rows).to_csv(OUT_AUDIT, index=False)

    policy_rows = [
        {
            "PolicyID": "RAW_UPSTREAM_PENALTY_ONE",
            "Description": "Use Loss + 1.0 * Complexity exactly on the PySR smoke loss scale",
            "AllowedForSmoke": True,
            "AllowedForSourceNativeScoring": False,
            "ObservedEffect": "selects constant despite available low-loss nonconstant candidate",
            "Risk": "over-penalizes shape on the current standardized smoke scale",
            "RequiredNextCheck": "verify upstream loss scaling or normalize penalty before bootstrap scoring",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "PolicyID": "BREAK_EVEN_PENALTY_DIAGNOSTIC",
            "Description": "Record the penalty threshold where the best nonconstant candidate stops beating the constant",
            "AllowedForSmoke": True,
            "AllowedForSourceNativeScoring": False,
            "ObservedEffect": f"break-even penalty approximately {break_even_penalty:.6g}",
            "Risk": "diagnostic threshold is derived from the current hall of fame and is not a registered selector",
            "RequiredNextCheck": "use only as governance evidence, not as a post-hoc selector",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "PolicyID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3",
            "Description": "Define a source-native normalized Loss + penalty * Complexity convention before bootstrap",
            "AllowedForSmoke": True,
            "AllowedForSourceNativeScoring": False,
            "ObservedEffect": "candidate governance route, not yet active",
            "Risk": "requires explicit pre-registration before any source-native scoring",
            "RequiredNextCheck": "write and freeze the normalized selector, then rerun PySR bootstrap",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "PolicyID": "AIC_BIC_MODEL_DIAGNOSTIC",
            "Description": "Use original-scale weighted residuals with complexity as model-size diagnostic",
            "AllowedForSmoke": True,
            "AllowedForSourceNativeScoring": False,
            "ObservedEffect": "useful diagnostic comparator only",
            "Risk": "not the upstream criteria-set-3 selector",
            "RequiredNextCheck": "keep separate from strict PySR selection metadata",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
    ]
    pd.DataFrame(policy_rows).to_csv(OUT_POLICY, index=False)

    penalty_one = selected_for_penalty(finite, 1.0)
    penalty_zero = selected_for_penalty(finite, 0.0)
    penalty_below_break = selected_for_penalty(finite, max(break_even_penalty * 0.5, 0.0))
    penalty_above_break = selected_for_penalty(finite, break_even_penalty * 1.5)

    summary_df = pd.DataFrame(
        [
            {
                "AuditID": "PYSR_PENALTY_NORMALIZATION_AUDIT_V1",
                "HallOfFameRows": int(len(hof)),
                "FiniteRows": int(len(finite)),
                "ConstantRows": int(finite["IsConstant"].sum()),
                "NonconstantRows": int((~finite["IsConstant"]).sum()),
                "StrictPenaltyOneSelectedIsConstant": bool(penalty_one["IsConstant"]),
                "PenaltyZeroSelectedIsConstant": bool(penalty_zero["IsConstant"]),
                "BestNonconstantEquation": best_nonconstant["equation"],
                "BestNonconstantLoss": best_loss,
                "BestNonconstantComplexity": int(best_complexity),
                "ConstantEquation": constant["equation"],
                "ConstantLoss": const_loss,
                "ConstantComplexity": int(const_complexity),
                "BreakEvenPenaltyBestNonconstantVsConstant": break_even_penalty,
                "BelowBreakEvenSelectedIsConstant": bool(penalty_below_break["IsConstant"]),
                "AboveBreakEvenSelectedIsConstant": bool(penalty_above_break["IsConstant"]),
                "StrictWeightedMSEOriginal": float(summary["StrictWeightedMSEOriginal"]),
                "BestNonconstantWeightedMSEOriginal": float(summary["BestNonconstantWeightedMSEOriginal"]),
                "WeightedMSEImprovementNonconstantVsStrict": float(summary["WeightedMSEImprovementNonconstantVsStrict"]),
                "PenaltyNormalizationRequiredBeforeSourceNativeScoring": True,
                "SourceNativeCovarianceReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "PYSR_PENALTY_NORMALIZATION_REQUIRED_BEFORE_SOURCE_NATIVE_SCORING",
                "StrongestAllowedClaim": (
                    "the PySR smoke run exposes a penalty-scale governance issue before source-native backreaction scoring"
                ),
                "PrimaryResidualRisk": (
                    "using raw penalty-one on the smoke loss scale selects a constant while lower-loss nonconstant shapes exist"
                ),
                "NextAction": (
                    "pre-register a source-native normalized criteria-set-3 selector or obtain the upstream authors' exact loss-scale convention"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary_df.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# PySR Penalty Normalization Audit",
                "",
                "Status: PYSR_PENALTY_NORMALIZATION_REQUIRED_BEFORE_SOURCE_NATIVE_SCORING.",
                "",
                "The structured smoke run shows that raw penalty-one criteria selects a constant on the current standardized loss scale, while much lower-loss nonconstant candidates are present.",
                "",
                "## Key Numbers",
                "",
                f"- Strict penalty-one selects constant: {bool(penalty_one['IsConstant'])}",
                f"- Best nonconstant equation: `{best_nonconstant['equation']}`",
                f"- Constant loss: {const_loss}",
                f"- Best nonconstant loss: {best_loss}",
                f"- Break-even penalty: {break_even_penalty}",
                f"- Strict original weighted MSE: {float(summary['StrictWeightedMSEOriginal'])}",
                f"- Best nonconstant original weighted MSE: {float(summary['BestNonconstantWeightedMSEOriginal'])}",
                "",
                "## Boundary",
                "",
                "This does not select a replacement source-native null. It only records that the penalty convention must be governed before bootstrap-scale scoring.",
                "",
                "## Next Action",
                "",
                "Pre-register a source-native normalized criteria-set-3 selector or obtain the upstream authors' exact loss-scale convention.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_AUDIT.relative_to(ROOT)}")
    print(f"Wrote {OUT_POLICY.relative_to(ROOT)}")
    print(f"Wrote {OUT_DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
