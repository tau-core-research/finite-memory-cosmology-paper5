#!/usr/bin/env python3
"""Summarize the A2-vs-polynomial tension after the preflight gate opened."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SCORE = ROOT / "evidence" / "k2_a2_public_covariance_proxy_summary.csv"
POLY_CV = ROOT / "evidence" / "k2_a2_polynomial_cv_summary.csv"
FAIRNESS = ROOT / "evidence" / "polynomial_control_fairness_summary.csv"
PREFLIGHT_GATE = ROOT / "evidence" / "k2_a2_preflight_scoring_gate_summary.csv"

OUT = ROOT / "evidence" / "k2_a2_polynomial_tension_diagnosis.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    public = pd.read_csv(PUBLIC_SCORE).iloc[0]
    cv = pd.read_csv(POLY_CV)
    fairness = pd.read_csv(FAIRNESS).iloc[0]
    gate = pd.read_csv(PREFLIGHT_GATE).iloc[0]

    comparisons = cv[cv["ModelID"].eq("A2_CV_COMPARISON")].copy()
    comparisons["A2BeatsBestPolyBool"] = comparisons["A2BeatsBestPoly"].map(truthy)
    public_cv = comparisons[comparisons["SigmaRoute"].eq("public_proxy_diag")]
    branch_cv = comparisons[comparisons["SigmaRoute"].ne("public_proxy_diag")]

    rows = [
        {
            "DiagnosisID": "IN_SAMPLE_PUBLIC_PROXY",
            "Question": "Does locked A2 beat polynomial controls in the current public covariance proxy scorecard?",
            "Finding": (
                "A2 improves over K1 and unit K2, but POLY_DEG2 remains better in-sample."
            ),
            "Evidence": (
                f"A2MinusK1={public['DeltaAIC_A2_minus_K1']}; "
                f"A2MinusUnitK2={public['DeltaAIC_A2_minus_UnitK2']}; "
                f"A2MinusBestPoly={public['DeltaAIC_A2_minus_BestPoly']}"
            ),
            "Interpretation": "supportive_vs_memory_nulls_but_not_distinctive_vs_flexible_smoothing",
            "MeasurementValidationImpact": "blocks_stronger_measurement_claim",
            "ClaimBoundary": "polynomial_tension_no_measurement_validation",
        },
        {
            "DiagnosisID": "PUBLIC_PROXY_CV",
            "Question": "Is the polynomial advantage stable under public-proxy cross-validation?",
            "Finding": (
                "Mixed: polynomial wins public-proxy leave-one-out, but A2 wins public-proxy blocked split."
            ),
            "Evidence": (
                f"A2BeatsBestPolyPublicCV={int(public_cv['A2BeatsBestPolyBool'].sum())}/{len(public_cv)}; "
                f"Modes={';'.join(public_cv['ValidationMode'].astype(str))}"
            ),
            "Interpretation": "polynomial_advantage_is_not_uniform_out_of_sample",
            "MeasurementValidationImpact": "weakens_polynomial_as_final_rejection_but_keeps_blocker",
            "ClaimBoundary": "polynomial_tension_no_measurement_validation",
        },
        {
            "DiagnosisID": "BRANCH_SCATTER_CV",
            "Question": "Does A2 stay competitive when reconstruction-family scatter is included?",
            "Finding": "A2 beats polynomial controls on all non-public-proxy CV routes.",
            "Evidence": (
                f"A2BeatsBestPolyBranchCV={int(branch_cv['A2BeatsBestPolyBool'].sum())}/{len(branch_cv)}"
            ),
            "Interpretation": "a2_support_strengthens_when_reconstruction_family_uncertainty_is_counted",
            "MeasurementValidationImpact": "supportive_preflight_only",
            "ClaimBoundary": "polynomial_tension_no_measurement_validation",
        },
        {
            "DiagnosisID": "POLYNOMIAL_FAIRNESS",
            "Question": "Can the polynomial control be dismissed?",
            "Finding": "No. It is not a physical null, but it remains a mandatory overfit-risk blocker.",
            "Evidence": (
                f"Role={fairness['PolynomialControlRole']}; "
                f"CanBeDismissed={fairness['PolynomialCanBeDismissed']}; "
                f"Status={fairness['CurrentStatus']}"
            ),
            "Interpretation": "do_not_hide_poly_tension_do_not_promote_poly_to_physical_explanation",
            "MeasurementValidationImpact": "blocks_stronger_measurement_claim",
            "ClaimBoundary": "polynomial_tension_no_measurement_validation",
        },
        {
            "DiagnosisID": "CURRENT_DECISION",
            "Question": "What is the current best reading of the A2 result?",
            "Finding": (
                "The preflight scorecard is allowed and A2 is stronger than K1/unit K2, "
                "but polynomial tension keeps the result at preflight-support level."
            ),
            "Evidence": (
                f"PreflightAllowed={gate['PreflightScorecardAllowed']}; "
                f"MeasurementValidationAllowed={gate['MeasurementValidationAllowed']}"
            ),
            "Interpretation": "a2_preflight_support_not_measurement_validation",
            "MeasurementValidationImpact": "full_likelihood_native_public_benchmark_required",
            "ClaimBoundary": "polynomial_tension_no_measurement_validation",
        },
    ]
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
