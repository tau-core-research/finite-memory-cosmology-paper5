#!/usr/bin/env python3
"""Audit source-split geometry behind the A_tau=2 prior.

The audit asks whether the A2 prior is supported by source-branch geometry:
opposed SN/BAO channels, K2 sign agreement, depth activation, and A_opt near 2.
It does not change the locked prediction.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

ANTI = EVIDENCE / "source_split_antialignment_summary.csv"
AOPT = EVIDENCE / "tau_core_a2_amplitude_specificity_audit.csv"
DEPTH = EVIDENCE / "tau_core_depth_activation_summary.csv"
MEMORY = EVIDENCE / "k2_a2_memory_active_scorecard_summary.csv"

OUT = EVIDENCE / "tau_core_source_split_geometry_audit.csv"
SUMMARY = EVIDENCE / "tau_core_source_split_geometry_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    anti = pd.read_csv(ANTI).set_index("Subset")
    aopt = pd.read_csv(AOPT)
    depth = pd.read_csv(DEPTH).iloc[0]
    memory = pd.read_csv(MEMORY).set_index("SubsetID")

    high_anti = anti.loc["high_depth"]
    sign_anti = anti.loc["sign_stable_only"]
    all_anti = anti.loc["all_points"]
    mid_high_anti = anti.loc["mid_high_depth"]

    aopt_public = aopt[aopt["RouteID"].eq("PUBLIC_COVARIANCE_PROXY")].copy()
    aopt_public["AOptNumeric"] = pd.to_numeric(aopt_public["AOpt"], errors="coerce")
    aopt_mid_high = aopt_public[aopt_public["SubsetID"].eq("mid_high_memory_active")].iloc[0]
    aopt_high = aopt_public[aopt_public["SubsetID"].eq("high_depth")].iloc[0]
    aopt_anti = aopt_public[aopt_public["SubsetID"].eq("memory_active_anti_aligned")].iloc[0]

    memory_mid_high = memory.loc["mid_high_memory_active"]
    memory_anti = memory.loc["memory_active_anti_aligned"]

    checks = [
        {
            "CheckID": "K2_SIGN_MATCHES_SOURCE_SPLIT",
            "Question": "Does locked K2 choose the same sign as the source-split response?",
            "Passed": float(all_anti["K2MatchesSourceSplitFraction"]) == 1.0,
            "Evidence": f"all-points K2 sign match={all_anti['K2MatchesSourceSplitRows']}/{all_anti['Rows']}",
            "Interpretation": "locked K2 direction follows source-split sign across the packet",
        },
        {
            "CheckID": "ANTI_ALIGNMENT_SIGN_STABLE_SUPPORT",
            "Question": "Are sign-stable rows mostly SN/BAO anti-aligned?",
            "Passed": bool(sign_anti["SupportsATau2Prior"]),
            "Evidence": (
                f"sign-stable opposite-sign fraction={sign_anti['OppositeSignFraction']}; "
                f"mean channel product={sign_anti['MeanSignedChannelProduct']}"
            ),
            "Interpretation": "anti-aligned branch geometry supports source-split gain prior in stable rows",
        },
        {
            "CheckID": "HIGH_DEPTH_ANTI_ALIGNMENT_SUPPORT",
            "Question": "Does high-depth regime retain anti-alignment support?",
            "Passed": bool(high_anti["SupportsATau2Prior"]),
            "Evidence": (
                f"high-depth opposite-sign fraction={high_anti['OppositeSignFraction']}; "
                f"anti-aligned+K2 match={high_anti['AntiAlignedAndK2MatchedRows']}/{high_anti['Rows']}"
            ),
            "Interpretation": "high-depth branch geometry is compatible with A_tau=2",
        },
        {
            "CheckID": "MID_HIGH_NOT_UNIFORMLY_ANTI_ALIGNED",
            "Question": "Is the full mid/high set uniformly anti-aligned?",
            "Passed": not bool(mid_high_anti["SupportsATau2Prior"]),
            "Evidence": (
                f"mid-high opposite-sign fraction={mid_high_anti['OppositeSignFraction']}; "
                f"mean channel product={mid_high_anti['MeanSignedChannelProduct']}"
            ),
            "Interpretation": "A2 support is not reducible to simple anti-alignment in every row; depth activation is also required",
        },
        {
            "CheckID": "AOPT_MID_HIGH_NEAR_2",
            "Question": "Does mid/high public-proxy amplitude point back to A_tau≈2?",
            "Passed": abs(float(aopt_mid_high["AOptNumeric"]) - 2.0) <= 0.25,
            "Evidence": f"mid-high AOpt={float(aopt_mid_high['AOptNumeric']):.6g}",
            "Interpretation": "source-split projection amplitude is close to the locked A2 prior",
        },
        {
            "CheckID": "AOPT_HIGH_DEPTH_NEAR_2",
            "Question": "Does high-depth public-proxy amplitude point back to A_tau≈2?",
            "Passed": abs(float(aopt_high["AOptNumeric"]) - 2.0) <= 0.25,
            "Evidence": f"high-depth AOpt={float(aopt_high['AOptNumeric']):.6g}",
            "Interpretation": "activated high-depth response supports A_tau=2 specifically",
        },
        {
            "CheckID": "AOPT_ANTI_ALIGNED_NEAR_2",
            "Question": "Does anti-aligned memory-active amplitude remain near A_tau=2?",
            "Passed": abs(float(aopt_anti["AOptNumeric"]) - 2.0) <= 0.5,
            "Evidence": f"memory-active anti-aligned AOpt={float(aopt_anti['AOptNumeric']):.6g}",
            "Interpretation": "anti-aligned rows are compatible with a two-channel source-split gain",
        },
        {
            "CheckID": "MEMORY_ACTIVE_SCORE_SUPPORT",
            "Question": "Does memory-active scoring support A2 against K1/unit/polynomial controls?",
            "Passed": truthy(memory_mid_high["A2ImprovesOverK1"])
            and truthy(memory_mid_high["A2ImprovesOverUnitK2"])
            and truthy(memory_mid_high["A2BeatsBestPoly"]),
            "Evidence": (
                f"mid-high DeltaAIC A2-K1={memory_mid_high['DeltaAIC_A2_minus_K1']}; "
                f"A2-unit={memory_mid_high['DeltaAIC_A2_minus_UnitK2']}; "
                f"A2-poly={memory_mid_high['DeltaAIC_A2_minus_BestPoly']}"
            ),
            "Interpretation": "projection gain prior improves the memory-active scorecard",
        },
        {
            "CheckID": "DEPTH_ACTIVATION_CONTEXT",
            "Question": "Does this geometry sit inside a passed depth-activation pattern?",
            "Passed": truthy(depth["DepthActivationPatternSupported"]),
            "Evidence": f"depth activation passed checks={depth['PassedChecks']}/{depth['Checks']}",
            "Interpretation": "source-split geometry and depth activation are mutually consistent",
        },
    ]

    output = pd.DataFrame(checks)
    output["ClaimBoundary"] = "source_split_geometry_no_measurement_validation"
    output.to_csv(OUT, index=False)

    passed = int(output["Passed"].map(truthy).sum())
    total = len(output)
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "TAU_CORE_SOURCE_SPLIT_GEOMETRY_AUDIT",
                "Checks": total,
                "PassedChecks": passed,
                "GeometrySupportsATau2Preflight": passed >= total - 1,
                "UniformAntiAlignmentRequired": False,
                "MeasurementValidationAllowed": False,
                "CurrentInterpretation": (
                    "A_tau_2_supported_by_source_split_geometry_plus_depth_activation"
                    if passed >= total - 1
                    else "source_split_geometry_support_mixed"
                ),
                "StrongestAllowedClaim": "A_tau=2 is geometrically supported in memory-active preflight",
                "DisallowedClaim": "measurement validation is not authorized",
                "NextAction": "repeat with likelihood-native SN/BAO transforms and public covariance-native source split",
                "ClaimBoundary": "source_split_geometry_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
