#!/usr/bin/env python3
"""Audit the Tau Core depth-activation pattern for locked A2.

The finite-memory projection interpretation predicts a weak low-depth response
and a stronger mid/high-depth response. This script checks that pattern without
changing K1, K2, A2, rho, p, or the transform outputs.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DEPTH = EVIDENCE / "source_split_a2_depth_transition.csv"
MEMORY_SCORE = EVIDENCE / "k2_a2_memory_active_scorecard_summary.csv"
CROSS = EVIDENCE / "k2_a2_memory_active_cross_covariance_summary.csv"
TRANSFORM = EVIDENCE / "k2_a2_transform_variant_robustness_summary.csv"
RANDOM = EVIDENCE / "k2_a2_memory_active_randomization_summary.csv"

OUT = EVIDENCE / "tau_core_depth_activation_audit.csv"
SUMMARY = EVIDENCE / "tau_core_depth_activation_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    depth = pd.read_csv(DEPTH).set_index("DepthBin")
    memory = pd.read_csv(MEMORY_SCORE)
    cross = pd.read_csv(CROSS)
    transform = pd.read_csv(TRANSFORM)
    random = pd.read_csv(RANDOM)

    ratio_low = float(depth.loc["low_depth", "A2PredictionToTargetRMSRatio"])
    ratio_mid = float(depth.loc["mid_depth", "A2PredictionToTargetRMSRatio"])
    ratio_high = float(depth.loc["high_depth", "A2PredictionToTargetRMSRatio"])
    residual_low = float(depth.loc["low_depth", "A2ResidualRMS"])
    residual_mid = float(depth.loc["mid_depth", "A2ResidualRMS"])
    residual_high = float(depth.loc["high_depth", "A2ResidualRMS"])
    delta_k1_low = float(depth.loc["low_depth", "A2DeltaAICVsK1"])
    delta_k1_mid = float(depth.loc["mid_depth", "A2DeltaAICVsK1"])
    delta_k1_high = float(depth.loc["high_depth", "A2DeltaAICVsK1"])

    mid_high = memory[memory["SubsetID"].eq("mid_high_memory_active")].iloc[0]
    high = memory[memory["SubsetID"].eq("high_depth")].iloc[0]

    cross_mid_high = cross[cross["SubsetID"].eq("mid_high_memory_active")]
    cross_high = cross[cross["SubsetID"].eq("high_depth")]
    transform_mid_high = transform[transform["SubsetID"].eq("mid_high_memory_active")]

    random_mid_high = random[random["SubsetID"].eq("mid_high_memory_active")]

    checks = [
        {
            "CheckID": "DEPTH_RESPONSE_MONOTONE",
            "Question": "Does locked A2 response amplitude rise from low to mid to high depth?",
            "Passed": ratio_low < ratio_mid < ratio_high,
            "Evidence": f"ratios low/mid/high={ratio_low:.6g}/{ratio_mid:.6g}/{ratio_high:.6g}",
            "Interpretation": "matches finite-memory activation ordering",
        },
        {
            "CheckID": "DEPTH_RESIDUAL_IMPROVES",
            "Question": "Does residual size shrink from low to mid to high depth?",
            "Passed": residual_low > residual_mid > residual_high,
            "Evidence": f"residual RMS low/mid/high={residual_low:.6g}/{residual_mid:.6g}/{residual_high:.6g}",
            "Interpretation": "A2 becomes more accurate in memory-active regime",
        },
        {
            "CheckID": "K1_IMPROVEMENT_STRENGTHENS_WITH_DEPTH",
            "Question": "Does A2's improvement over K1 strengthen with depth?",
            "Passed": delta_k1_low > delta_k1_mid > delta_k1_high,
            "Evidence": f"DeltaAIC A2-K1 low/mid/high={delta_k1_low:.6g}/{delta_k1_mid:.6g}/{delta_k1_high:.6g}",
            "Interpretation": "no-memory baseline is increasingly disfavored as memory depth grows",
        },
        {
            "CheckID": "MEMORY_ACTIVE_SCORECARD_DOMINANCE",
            "Question": "Does A2 win on the declared mid/high memory-active subset?",
            "Passed": truthy(mid_high["A2ImprovesOverK1"])
            and truthy(mid_high["A2ImprovesOverUnitK2"])
            and truthy(mid_high["A2BeatsBestPoly"]),
            "Evidence": (
                f"mid_high DeltaAIC A2-K1={mid_high['DeltaAIC_A2_minus_K1']}; "
                f"A2-unit={mid_high['DeltaAIC_A2_minus_UnitK2']}; "
                f"A2-poly={mid_high['DeltaAIC_A2_minus_BestPoly']}"
            ),
            "Interpretation": "memory-active subset supports locked A2 against main controls",
        },
        {
            "CheckID": "HIGH_DEPTH_SCORECARD_DOMINANCE",
            "Question": "Is the high-depth subset the strongest fixed-model regime?",
            "Passed": truthy(high["A2ImprovesOverK1"]) and truthy(high["A2ImprovesOverUnitK2"]),
            "Evidence": (
                f"high-depth A2AIC={high['A2AIC']}; K1AIC={high['K1AIC']}; "
                f"unitK2AIC={high['UnitK2AIC']}"
            ),
            "Interpretation": "high-depth behavior is consistent with activated finite-memory response",
        },
        {
            "CheckID": "CROSS_COVARIANCE_ROBUST_MID_HIGH",
            "Question": "Does mid/high A2 dominance survive the declared cross-covariance grid?",
            "Passed": int(cross_mid_high["A2BeatsBestPoly"].map(truthy).sum()) == len(cross_mid_high),
            "Evidence": (
                f"mid_high A2 beats best poly {int(cross_mid_high['A2BeatsBestPoly'].map(truthy).sum())}/"
                f"{len(cross_mid_high)} rho_cross values"
            ),
            "Interpretation": "not explained by a single cross-covariance setting",
        },
        {
            "CheckID": "TRANSFORM_VARIANT_ROBUST_MID_HIGH",
            "Question": "Does mid/high A2 dominance survive simple SN/BAO transform variants?",
            "Passed": int(transform_mid_high["A2BeatsBestPoly"].map(truthy).sum()) == len(transform_mid_high),
            "Evidence": (
                f"mid_high A2 beats best poly {int(transform_mid_high['A2BeatsBestPoly'].map(truthy).sum())}/"
                f"{len(transform_mid_high)} transform variants"
            ),
            "Interpretation": "not tied to a single binned/anchored transform variant",
        },
        {
            "CheckID": "RANDOMIZATION_CONTROL_MID_HIGH",
            "Question": "Does mid/high A2 beat sign/depth randomized controls?",
            "Passed": int(random_mid_high["ObservedBeatsControlMedianCount"].sum())
            == int(random_mid_high["TransformVariants"].sum()),
            "Evidence": (
                "mid_high observed beats randomized medians="
                f"{int(random_mid_high['ObservedBeatsControlMedianCount'].sum())}/"
                f"{int(random_mid_high['TransformVariants'].sum())}; "
                f"median p range={random_mid_high['MedianEmpiricalP_ControlLEObserved'].min():.6g}.."
                f"{random_mid_high['MedianEmpiricalP_ControlLEObserved'].max():.6g}"
            ),
            "Interpretation": "direction/order agreement is unlikely to be a trivial randomized artifact",
        },
    ]

    output = pd.DataFrame(checks)
    output["ClaimBoundary"] = "tau_core_depth_activation_no_measurement_validation"
    output.to_csv(OUT, index=False)

    passed = int(output["Passed"].map(truthy).sum())
    total = len(output)
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "TAU_CORE_DEPTH_ACTIVATION_AUDIT",
                "Checks": total,
                "PassedChecks": passed,
                "DepthActivationPatternSupported": passed == total,
                "MeasurementValidationAllowed": False,
                "CurrentInterpretation": (
                    "locked_A2_matches_depth_activation_preflight_pattern"
                    if passed == total
                    else "depth_activation_pattern_mixed_or_incomplete"
                ),
                "StrongestAllowedClaim": "Tau Core A2 has memory-active preflight support",
                "DisallowedClaim": "measurement validation is not authorized",
                "NextAction": "promote SN/BAO likelihood-native transforms and rerun the same locked A2 tests",
                "ClaimBoundary": "tau_core_depth_activation_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
