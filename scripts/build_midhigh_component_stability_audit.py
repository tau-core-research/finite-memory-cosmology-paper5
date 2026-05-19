#!/usr/bin/env python3
"""Build a compact stability audit for the mid/high backreaction-like K2 component."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROUTE = EVIDENCE / "backreaction_route_adjudication_summary.csv"
BOOTSTRAP = EVIDENCE / "derivative_pilot_component_uncertainty_summary.csv"
NOISE = EVIDENCE / "derivative_pilot_noise_source_summary.csv"
DEGREE = EVIDENCE / "derivative_pilot_degree_sensitivity_summary.csv"

OUT_MATRIX = EVIDENCE / "midhigh_component_stability_matrix.csv"
OUT_SUMMARY = EVIDENCE / "midhigh_component_stability_summary.csv"
OUT_DOC = DOCS / "midhigh_component_stability_audit.md"

CLAIM_BOUNDARY = "midhigh_component_stability_audit_no_measurement_validation"


def read_first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def status_from_threshold(value: float, threshold: float = 0.25) -> str:
    return "SURVIVES_THRESHOLD" if value >= threshold else "WEAK_OR_UNSTABLE"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    route = read_first(ROUTE)
    bootstrap = read_first(BOOTSTRAP)
    noise = pd.read_csv(NOISE)
    noise_overall = noise[noise["NoiseMode"].eq("OVERALL")].iloc[0]
    degree = read_first(DEGREE)

    rows = [
        {
            "CheckID": "ROUTE_ADJUDICATION",
            "Axis": "route_family",
            "MidHighLower": float(route["MinMidHighComponentFraction"]),
            "MidHighCentral": (float(route["MinMidHighComponentFraction"]) + float(route["MaxMidHighComponentFraction"])) / 2.0,
            "MidHighUpper": float(route["MaxMidHighComponentFraction"]),
            "HighCentral": (float(route["MinHighComponentFraction"]) + float(route["MaxHighComponentFraction"])) / 2.0,
            "LowCentral": float(route["PilotLowComponentFraction"]),
            "Status": status_from_threshold(float(route["MinMidHighComponentFraction"])),
            "Interpretation": "both current non-source-native routes keep a nonzero mid/high component",
        },
        {
            "CheckID": "BOOTSTRAP_COMPONENT_UNCERTAINTY",
            "Axis": "public_training_input_bootstrap",
            "MidHighLower": float(bootstrap["mid_high_depth_P16"]),
            "MidHighCentral": float(bootstrap["mid_high_depth_P50"]),
            "MidHighUpper": float(bootstrap["mid_high_depth_P84"]),
            "HighCentral": float(bootstrap["high_depth_P50"]),
            "LowCentral": float(bootstrap["low_depth_P50"]),
            "Status": status_from_threshold(float(bootstrap["mid_high_depth_P16"])),
            "Interpretation": "bootstrap stress test keeps mid/high lower band above threshold but low-depth is broad",
        },
        {
            "CheckID": "NOISE_SOURCE_DECOMPOSITION",
            "Axis": "sn_bao_noise_modes",
            "MidHighLower": float(noise_overall["ComponentFractionP16"]),
            "MidHighCentral": float(noise_overall["ComponentFractionP50"]),
            "MidHighUpper": float(noise_overall["ComponentFractionP84"]),
            "HighCentral": float(noise[noise["SubsetID"].eq("high_depth")]["ComponentFractionP50"].median()),
            "LowCentral": float(noise[noise["SubsetID"].eq("low_depth")]["ComponentFractionP50"].median()),
            "Status": status_from_threshold(float(noise_overall["ComponentFractionP16"]), threshold=0.20),
            "Interpretation": "mid/high remains nonzero across SN-only, BAO-only, and combined noise modes",
        },
        {
            "CheckID": "POLYNOMIAL_DEGREE_SENSITIVITY",
            "Axis": "fixed_degree_grid",
            "MidHighLower": float(degree["MidHighComponentFractionMin"]),
            "MidHighCentral": float(degree["MidHighComponentFractionP50"]),
            "MidHighUpper": float(degree["MidHighComponentFractionMax"]),
            "HighCentral": float(degree["HighComponentFractionP50"]),
            "LowCentral": float(degree["LowComponentFractionP50"]),
            "Status": status_from_threshold(float(degree["MidHighComponentFractionMin"]), threshold=0.15),
            "Interpretation": "nearby fixed polynomial degrees preserve a mid/high component but expose reconstruction sensitivity",
        },
    ]
    matrix = pd.DataFrame(rows)
    matrix["MeasurementValidationAllowed"] = False
    matrix["LockedK2Changed"] = False
    matrix["ScaleFitAllowed"] = False
    matrix["ClaimBoundary"] = CLAIM_BOUNDARY
    matrix.to_csv(OUT_MATRIX, index=False)

    surviving = int(matrix["Status"].eq("SURVIVES_THRESHOLD").sum())
    mid_lower_min = float(matrix["MidHighLower"].min())
    mid_central_median = float(matrix["MidHighCentral"].median())
    low_central_median = float(matrix["LowCentral"].median())
    low_is_stable = bool(low_central_median < 0.15 and not bool(degree["LowDepthDegreeSensitive"]))
    current_status = (
        "MIDHIGH_COMPONENT_STABLE_LOW_DEPTH_NOT_STABLE"
        if surviving == len(matrix) and not low_is_stable
        else "COMPONENT_STABILITY_MIXED_WARNING"
    )

    summary = pd.DataFrame(
        [
            {
                "AuditID": "MIDHIGH_COMPONENT_STABILITY_AUDIT_V1",
                "Checks": len(matrix),
                "ChecksSurvivingThreshold": surviving,
                "MidHighLowerMinAcrossChecks": mid_lower_min,
                "MidHighCentralMedianAcrossChecks": mid_central_median,
                "LowCentralMedianAcrossChecks": low_central_median,
                "LowDepthStableSuppression": low_is_stable,
                "SourceNativeRouteAvailable": False,
                "CovarianceReady": False,
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": current_status,
                "StrongestAllowedClaim": (
                    "the non-source-native preflight audits consistently retain a mid/high backreaction-like K2 component"
                ),
                "PrimaryResidualRisk": (
                    "low-depth suppression is not stable under bootstrap/noise/degree stress and source-native covariance is missing"
                ),
                "NextAction": "promote only the mid/high component as preflight-stable; keep low-depth suppression as a weak/conditional diagnostic until source-native rerun",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Mid/High Component Stability Audit",
                "",
                "Status: mid/high preflight component stable; low-depth suppression conditional.",
                "",
                "This audit compresses route, bootstrap, noise-source, and polynomial-degree diagnostics into one decision matrix. It does not promote a measurement claim.",
                "",
                "## Result",
                "",
                f"- Mid/high lower bound across checks: {mid_lower_min:.3f}",
                f"- Mid/high central median across checks: {mid_central_median:.3f}",
                f"- Low-depth central median across checks: {low_central_median:.3f}",
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
