#!/usr/bin/env python3
"""Audit the role of polynomial controls in the measurement gate.

The goal is to decide how polynomial controls should be interpreted: fair
physical null, overfit-risk control, or disqualifying comparator. This script
does not change K2, K1, or any scorecard.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

NULL_REGISTRY = ROOT / "evidence" / "null_model_registry.csv"
REGISTERED_SHRINKAGE = ROOT / "evidence" / "registered_shrinkage_future_preflight_summary.csv"
POLY_CV = ROOT / "evidence" / "source_split_likelihood_native_polynomial_cv_summary.csv"
SUPPORT = ROOT / "evidence" / "source_split_likelihood_native_support_ladder.csv"

OUT_AUDIT = ROOT / "evidence" / "polynomial_control_fairness_audit.csv"
OUT_SUMMARY = ROOT / "evidence" / "polynomial_control_fairness_summary.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    registry = pd.read_csv(NULL_REGISTRY)
    poly_registry = registry[registry["NullID"].eq("GENERIC_POLYNOMIAL_SMOOTHING")].iloc[0]
    shrink = pd.read_csv(REGISTERED_SHRINKAGE).iloc[0]
    cv = pd.read_csv(POLY_CV)
    support = pd.read_csv(SUPPORT)
    support_l2 = support[support["LevelID"].eq("L2_K2_VS_POLYNOMIAL_CONTROLS")].iloc[0]

    comparisons = cv[cv["ModelID"].eq("CV_COMPARISON")].copy()
    total_cv = len(comparisons)
    k2_beats_poly_cv = int(comparisons["K2BeatsBestPoly"].map(bool_text).sum())
    public_cv = comparisons[comparisons["SigmaRoute"].eq("public_proxy_diag")]
    public_k2_beats_poly_cv = int(public_cv["K2BeatsBestPoly"].map(bool_text).sum())

    audit_rows = [
        {
            "CriterionID": "POLY_ROLE_REGISTRY",
            "Question": "How is the polynomial control registered?",
            "Evidence": f"NullCategory={poly_registry['NullCategory']}; Role={poly_registry['Role']}; FreeParameters={poly_registry['FreeParameters']}",
            "Finding": "overfit_risk_control_not_physical_null",
            "PolicyDecision": "mandatory_control_but_not_standalone_physical_explanation",
            "BlocksMeasurementValidation": True,
            "ClaimBoundary": "polynomial_control_fairness_no_measurement_validation",
        },
        {
            "CriterionID": "POLY_IN_SAMPLE_REGISTERED_SHRINKAGE",
            "Question": "Does polynomial control beat K2 under registered shrinkage in-sample?",
            "Evidence": (
                f"K2BeatsBestPoly={shrink['K2BeatsBestPoly']}; "
                f"DeltaAIC_K2_minus_BestPoly={shrink['DeltaAIC_K2_minus_BestPoly']}"
            ),
            "Finding": "polynomial_control_dominates_registered_shrinkage_in_sample",
            "PolicyDecision": "measurement_claim_blocked_under_registered_shrinkage_route",
            "BlocksMeasurementValidation": True,
            "ClaimBoundary": "polynomial_control_fairness_no_measurement_validation",
        },
        {
            "CriterionID": "POLY_CV_STABILITY",
            "Question": "Is polynomial dominance stable across validation routes?",
            "Evidence": f"K2BeatsBestPolyCV={k2_beats_poly_cv}/{total_cv}; PublicProxyCV={public_k2_beats_poly_cv}/{len(public_cv)}",
            "Finding": "polynomial_advantage_not_uniformly_stable",
            "PolicyDecision": "weakens_polynomial_as_final_rejection_but_does_not_remove_blocker",
            "BlocksMeasurementValidation": True,
            "ClaimBoundary": "polynomial_control_fairness_no_measurement_validation",
        },
        {
            "CriterionID": "POLY_SUPPORT_LADDER",
            "Question": "What does the support ladder say about K2-vs-polynomial controls?",
            "Evidence": f"Status={support_l2['Status']}; Evidence={support_l2['Evidence']}",
            "Finding": "mixed_conditional_support",
            "PolicyDecision": "report_as_mixed_not_supportive_measurement",
            "BlocksMeasurementValidation": True,
            "ClaimBoundary": "polynomial_control_fairness_no_measurement_validation",
        },
        {
            "CriterionID": "POLY_FAIRNESS_DECISION",
            "Question": "Can polynomial controls be dismissed as unfair?",
            "Evidence": "They are generic smoothing controls without physical provenance, but they remain preregistered null comparators and win some public-proxy tests.",
            "Finding": "cannot_dismiss_cannot_promote_to_physical_null",
            "PolicyDecision": "keep_as_mandatory_overfit_risk_control; require K2 competitiveness against them for stronger public claim",
            "BlocksMeasurementValidation": True,
            "ClaimBoundary": "polynomial_control_fairness_no_measurement_validation",
        },
    ]
    audit = pd.DataFrame(audit_rows)
    audit.to_csv(OUT_AUDIT, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "POLYNOMIAL_CONTROL_FAIRNESS_AUDIT",
                "Criteria": len(audit),
                "MeasurementBlockingCriteria": int(audit["BlocksMeasurementValidation"].map(bool_text).sum()),
                "PolynomialControlRole": "mandatory_overfit_risk_control",
                "PolynomialIsFairPhysicalNull": False,
                "PolynomialCanBeDismissed": False,
                "K2BeatsBestPolyCVCount": k2_beats_poly_cv,
                "K2BeatsBestPolyCVTotal": total_cv,
                "RegisteredShrinkageK2BeatsBestPoly": bool_text(shrink["K2BeatsBestPoly"]),
                "CurrentStatus": "POLYNOMIAL_CONTROL_REMAINS_MEASUREMENT_BLOCKER",
                "NextAction": "either obtain a public benchmark where locked K2 is competitive with polynomial controls or justify a more specific physical null comparator hierarchy before stronger claims",
                "Interpretation": "polynomial controls are not physical explanation but remain mandatory overfit-risk blockers",
                "ClaimBoundary": "polynomial_control_fairness_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
