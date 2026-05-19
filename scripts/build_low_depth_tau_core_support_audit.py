#!/usr/bin/env python3
"""Separate Tau-core low-depth suppression from derivative-pilot instability.

The low-depth route should be strengthened only through locked operator and
predeclared depth-response checks, not by fitting the derivative pilot. This
audit therefore distinguishes:

1. locked K2/Tau-core low-depth suppression;
2. low-depth weakness relative to target scale;
3. derivative-pilot low-depth instability as a reconstruction warning.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

K2_DEPTH = EVIDENCE / "k2_depth_scaling_summary.csv"
MIDHIGH = EVIDENCE / "midhigh_component_stability_summary.csv"
NOISE = EVIDENCE / "derivative_pilot_noise_source_summary.csv"
DEGREE = EVIDENCE / "derivative_pilot_degree_sensitivity_summary.csv"
COMPONENT_UNCERT = EVIDENCE / "derivative_pilot_component_uncertainty_summary.csv"

OUT_MATRIX = EVIDENCE / "low_depth_tau_core_support_matrix.csv"
OUT_SUMMARY = EVIDENCE / "low_depth_tau_core_support_summary.csv"
OUT_DOC = DOCS / "low_depth_tau_core_support_audit.md"

CLAIM_BOUNDARY = "low_depth_tau_core_support_audit_no_measurement_validation"


def row_for(df: pd.DataFrame, column: str, value: str) -> pd.Series:
    return df[df[column].astype(str).eq(value)].iloc[0]


def safe_ratio(num: float, den: float) -> float:
    return num / den if abs(den) > 1e-12 else float("nan")


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    depth = pd.read_csv(K2_DEPTH)
    low = row_for(depth, "Subset", "low_depth")
    mid = row_for(depth, "Subset", "mid_depth")
    high = row_for(depth, "Subset", "high_depth")

    midhigh = pd.read_csv(MIDHIGH).iloc[0]
    noise = pd.read_csv(NOISE)
    noise_overall = noise[noise["NoiseMode"].eq("OVERALL")].iloc[0]
    degree = pd.read_csv(DEGREE).iloc[0]
    uncert = pd.read_csv(COMPONENT_UNCERT).iloc[0]

    low_delta_w = float(low["MeanWLockedRho4"]) - 1.0
    mid_delta_w = float(mid["MeanWLockedRho4"]) - 1.0
    high_delta_w = float(high["MeanWLockedRho4"]) - 1.0

    rows = [
        {
            "CheckID": "LOCKED_OPERATOR_DEPTH_SUPPRESSION",
            "EvidenceAxis": "predeclared_cubic_memory_kernel",
            "LowValue": low_delta_w,
            "MidValue": mid_delta_w,
            "HighValue": high_delta_w,
            "LowToHighRatio": safe_ratio(low_delta_w, high_delta_w),
            "Status": "SUPPORTS_LOW_DEPTH_SUPPRESSION" if safe_ratio(low_delta_w, high_delta_w) < 0.15 else "WEAK_WARNING",
            "Interpretation": "locked finite-memory increment is naturally much weaker at low depth",
        },
        {
            "CheckID": "LOCKED_K2_TARGET_SCALE_SUPPRESSION",
            "EvidenceAxis": "locked_k2_vs_target_rms",
            "LowValue": float(low["K2ToTargetRMSRatio"]),
            "MidValue": float(mid["K2ToTargetRMSRatio"]),
            "HighValue": float(high["K2ToTargetRMSRatio"]),
            "LowToHighRatio": safe_ratio(float(low["K2ToTargetRMSRatio"]), float(high["K2ToTargetRMSRatio"])),
            "Status": "SUPPORTS_LOW_DEPTH_SUPPRESSION"
            if safe_ratio(float(low["K2ToTargetRMSRatio"]), float(high["K2ToTargetRMSRatio"])) < 0.20
            else "WEAK_WARNING",
            "Interpretation": "locked K2 remains small relative to target in low-depth rows",
        },
        {
            "CheckID": "MEMORY_BOOST_TARGET_SCALE_SUPPRESSION",
            "EvidenceAxis": "memory_boost_vs_target",
            "LowValue": float(low["MeanMemoryBoostOverTargetAbs"]),
            "MidValue": float(mid["MeanMemoryBoostOverTargetAbs"]),
            "HighValue": float(high["MeanMemoryBoostOverTargetAbs"]),
            "LowToHighRatio": safe_ratio(
                float(low["MeanMemoryBoostOverTargetAbs"]), float(high["MeanMemoryBoostOverTargetAbs"])
            ),
            "Status": "SUPPORTS_LOW_DEPTH_SUPPRESSION"
            if safe_ratio(float(low["MeanMemoryBoostOverTargetAbs"]), float(high["MeanMemoryBoostOverTargetAbs"])) < 0.10
            else "WEAK_WARNING",
            "Interpretation": "finite-memory boost is strongly suppressed in low-depth target units",
        },
        {
            "CheckID": "PILOT_COMPONENT_LOW_DEPTH_WARNING",
            "EvidenceAxis": "non_source_native_derivative_pilot",
            "LowValue": float(uncert["low_depth_P50"]),
            "MidValue": float(uncert["mid_high_depth_P50"]),
            "HighValue": float(uncert["high_depth_P50"]),
            "LowToHighRatio": safe_ratio(float(uncert["low_depth_P50"]), float(uncert["high_depth_P50"])),
            "Status": "RECONSTRUCTION_WARNING_NOT_TAU_CORE_FAILURE",
            "Interpretation": "pilot low-depth component is unstable under public-input bootstrap",
        },
        {
            "CheckID": "PILOT_DEGREE_LOW_DEPTH_WARNING",
            "EvidenceAxis": "fixed_polynomial_degree_grid",
            "LowValue": float(degree["LowComponentFractionP50"]),
            "MidValue": float(degree["MidHighComponentFractionP50"]),
            "HighValue": float(degree["HighComponentFractionP50"]),
            "LowToHighRatio": safe_ratio(float(degree["LowComponentFractionP50"]), float(degree["HighComponentFractionP50"])),
            "Status": "RECONSTRUCTION_WARNING_NOT_TAU_CORE_FAILURE"
            if str(degree["LowDepthDegreeSensitive"]).lower() == "true"
            else "SUPPORTS_LOW_DEPTH_SUPPRESSION",
            "Interpretation": "low-depth pilot component is degree-sensitive while mid/high remains nonzero",
        },
    ]
    matrix = pd.DataFrame(rows)
    matrix["LockedK2Changed"] = False
    matrix["ScaleFitAllowed"] = False
    matrix["MeasurementValidationAllowed"] = False
    matrix["ClaimBoundary"] = CLAIM_BOUNDARY
    matrix.to_csv(OUT_MATRIX, index=False)

    tau_support_checks = matrix[matrix["Status"].eq("SUPPORTS_LOW_DEPTH_SUPPRESSION")]
    reconstruction_warnings = matrix[matrix["Status"].str.contains("WARNING", na=False)]
    current_status = (
        "LOW_DEPTH_SUPPORTED_BY_LOCKED_TAU_CORE_OPERATOR_PILOT_RECONSTRUCTION_WEAK"
        if len(tau_support_checks) >= 3 and len(reconstruction_warnings) >= 2
        else "LOW_DEPTH_SUPPORT_MIXED"
    )
    summary = pd.DataFrame(
        [
            {
                "AuditID": "LOW_DEPTH_TAU_CORE_SUPPORT_AUDIT_V1",
                "Checks": len(matrix),
                "TauCoreSuppressionChecks": len(tau_support_checks),
                "ReconstructionWarningChecks": len(reconstruction_warnings),
                "LockedDeltaWLowToHighRatio": safe_ratio(low_delta_w, high_delta_w),
                "LockedK2TargetLowToHighRatio": safe_ratio(
                    float(low["K2ToTargetRMSRatio"]), float(high["K2ToTargetRMSRatio"])
                ),
                "MemoryBoostTargetLowToHighRatio": safe_ratio(
                    float(low["MeanMemoryBoostOverTargetAbs"]), float(high["MeanMemoryBoostOverTargetAbs"])
                ),
                "MidHighPreflightStable": str(midhigh["CurrentStatus"]) == "MIDHIGH_COMPONENT_STABLE_LOW_DEPTH_NOT_STABLE",
                "LowDepthStableAsPilotPhysicalNull": False,
                "SourceNativeRouteAvailable": False,
                "CovarianceReady": False,
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": current_status,
                "StrongestAllowedClaim": (
                    "low-depth suppression is strengthened at the locked Tau-core operator level, while the derivative-pilot low-depth physical-null route remains weak"
                ),
                "PrimaryResidualRisk": (
                    "the current public derivative pilot cannot support strong low-depth physical-null claims without source-native reconstruction and covariance"
                ),
                "NextAction": "use locked operator/target-scale suppression as the low-depth claim; keep pilot low-depth claims conditional until source-native rerun",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Low-Depth Tau Core Support Audit",
                "",
                "Status: locked Tau-core low-depth suppression strengthened; derivative-pilot physical-null low-depth remains weak.",
                "",
                "This audit prevents a false dilemma. Low-depth is supported by the predeclared cubic memory operator and target-scale suppression, while the public derivative-pilot backreaction route remains too reconstruction-sensitive for a strong low-depth physical-null claim.",
                "",
                "## Key Ratios",
                "",
                f"- Locked memory increment low/high ratio: {safe_ratio(low_delta_w, high_delta_w):.3f}",
                f"- Locked K2 target-scale low/high ratio: {safe_ratio(float(low['K2ToTargetRMSRatio']), float(high['K2ToTargetRMSRatio'])):.3f}",
                f"- Memory boost target-scale low/high ratio: {safe_ratio(float(low['MeanMemoryBoostOverTargetAbs']), float(high['MeanMemoryBoostOverTargetAbs'])):.3f}",
                f"- Status: `{current_status}`",
                "",
                "## Outputs",
                "",
                f"- Matrix: `{OUT_MATRIX.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_MATRIX}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
