#!/usr/bin/env python3
"""Adjudicate provisional and derivative-pilot backreaction route splits.

This combines the two current backreaction-route diagnostics into one compact
decision artifact. It does not select a physical null, alter K2, or authorize
measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROVISIONAL = EVIDENCE / "backreaction_k2_component_split_summary.csv"
PILOT = EVIDENCE / "derivative_pilot_k2_component_split_summary.csv"

OUT_MATRIX = EVIDENCE / "backreaction_route_adjudication_matrix.csv"
OUT_SUMMARY = EVIDENCE / "backreaction_route_adjudication_summary.csv"
OUT_DOC = DOCS / "backreaction_route_adjudication.md"

CLAIM_BOUNDARY = "backreaction_route_adjudication_no_measurement_validation"


def as_float(row: pd.Series, col: str) -> float:
    return float(row[col])


def classify(depth_activation_ratio: float, mid_high_fraction: float, route_gap: float) -> str:
    if mid_high_fraction <= 0.0:
        return "NO_BACKREACTION_COMPONENT"
    if depth_activation_ratio < 2.0:
        return "WEAK_DEPTH_SELECTIVITY"
    if route_gap > 0.35:
        return "ROUTE_SENSITIVE_COMPONENT_WARNING"
    return "DEPTH_SELECTIVE_COMPONENT_PRESENT"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    prov = pd.read_csv(PROVISIONAL).iloc[0]
    pilot = pd.read_csv(PILOT).iloc[0]

    rows = [
        {
            "RouteFamily": "PROVISIONAL_BAO_ONLY",
            "RouteClass": "provisional_bao_only_polynomial_reconstruction",
            "MidHighComponentFraction": as_float(prov, "MidHighBackreactionEnergyFractionMean"),
            "HighComponentFraction": as_float(prov, "HighBackreactionEnergyFractionMean"),
            "LowComponentFraction": "",
            "MidHighResidualFraction": 1.0 - as_float(prov, "MidHighBackreactionEnergyFractionMean"),
            "HighResidualFraction": 1.0 - as_float(prov, "HighBackreactionEnergyFractionMean"),
            "MidHighTargetCorrelation": as_float(prov, "MidHighBackreactionComponentTargetCorrelationMean"),
            "ResidualTargetCorrelation": as_float(prov, "MidHighResidualTargetCorrelationMean"),
            "SourceNative": False,
            "CovarianceReady": False,
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "RouteFamily": "PUBLIC_SN_BAO_DERIVATIVE_PILOT",
            "RouteClass": "fixed_polynomial_public_training_input_pilot",
            "MidHighComponentFraction": as_float(pilot, "MidHighPilotEnergyFractionMean"),
            "HighComponentFraction": as_float(pilot, "HighPilotEnergyFractionMean"),
            "LowComponentFraction": as_float(pilot, "LowPilotEnergyFractionMean"),
            "MidHighResidualFraction": as_float(pilot, "MidHighResidualEnergyFractionMean"),
            "HighResidualFraction": as_float(pilot, "HighResidualEnergyFractionMean"),
            "MidHighTargetCorrelation": as_float(pilot, "MidHighPilotTargetCorrelationMean"),
            "ResidualTargetCorrelation": as_float(pilot, "MidHighResidualTargetCorrelationMean"),
            "SourceNative": False,
            "CovarianceReady": False,
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
    ]
    matrix = pd.DataFrame(rows)
    matrix.to_csv(OUT_MATRIX, index=False)

    provisional_mid = float(matrix.loc[matrix["RouteFamily"].eq("PROVISIONAL_BAO_ONLY"), "MidHighComponentFraction"].iloc[0])
    pilot_mid = float(matrix.loc[matrix["RouteFamily"].eq("PUBLIC_SN_BAO_DERIVATIVE_PILOT"), "MidHighComponentFraction"].iloc[0])
    provisional_high = float(matrix.loc[matrix["RouteFamily"].eq("PROVISIONAL_BAO_ONLY"), "HighComponentFraction"].iloc[0])
    pilot_high = float(matrix.loc[matrix["RouteFamily"].eq("PUBLIC_SN_BAO_DERIVATIVE_PILOT"), "HighComponentFraction"].iloc[0])
    pilot_low = float(matrix.loc[matrix["RouteFamily"].eq("PUBLIC_SN_BAO_DERIVATIVE_PILOT"), "LowComponentFraction"].iloc[0])

    min_mid = min(provisional_mid, pilot_mid)
    max_mid = max(provisional_mid, pilot_mid)
    min_high = min(provisional_high, pilot_high)
    max_high = max(provisional_high, pilot_high)
    route_gap_mid = max_mid - min_mid
    route_gap_high = max_high - min_high
    depth_activation_ratio = pilot_mid / pilot_low if pilot_low > 0.0 else float("inf")
    status = classify(depth_activation_ratio, min_mid, route_gap_mid)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "BACKREACTION_ROUTE_ADJUDICATION_V1",
                "RoutesCompared": len(matrix),
                "MinMidHighComponentFraction": min_mid,
                "MaxMidHighComponentFraction": max_mid,
                "MidHighRouteGap": route_gap_mid,
                "MinHighComponentFraction": min_high,
                "MaxHighComponentFraction": max_high,
                "HighRouteGap": route_gap_high,
                "PilotLowComponentFraction": pilot_low,
                "PilotDepthActivationRatioMidHighOverLow": depth_activation_ratio,
                "BothRoutesSupportNonzeroMidHighComponent": min_mid > 0.0,
                "BothRoutesSupportNonzeroHighComponent": min_high > 0.0,
                "DerivativePilotLowDepthSuppressed": pilot_low < 0.15,
                "SourceNativeRouteAvailable": False,
                "CovarianceReady": False,
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": status,
                "StrongestAllowedClaim": (
                    "both current non-source-native backreaction routes show a nonzero K2 component in mid/high depth, "
                    "while the derivative pilot keeps low-depth response suppressed"
                ),
                "PrimaryResidualRisk": (
                    "component size remains route-sensitive and neither route is a source-native symbolic-regression export"
                ),
                "NextAction": "obtain source-native derivative/covariance exports and rerun this adjudication before promoting a physical-null claim",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Backreaction Route Adjudication",
                "",
                "Status: route-sensitive diagnostic support; no measurement-validation claim.",
                "",
                "This compares the provisional BAO-only backreaction split with the public SN/BAO derivative-pilot split. Both routes are non-source-native and are used only to decide what should be tested next.",
                "",
                "## Key Result",
                "",
                f"- Mid/high component fraction range: {min_mid:.3f} to {max_mid:.3f}",
                f"- High-depth component fraction range: {min_high:.3f} to {max_high:.3f}",
                f"- Derivative-pilot low-depth component fraction: {pilot_low:.3f}",
                f"- Status: `{status}`",
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
