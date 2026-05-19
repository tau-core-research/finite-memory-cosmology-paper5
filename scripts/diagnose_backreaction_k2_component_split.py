#!/usr/bin/env python3
"""Decompose locked K2 into provisional backreaction-like and residual parts.

This diagnostic asks whether the provisional BAO-only backreaction bridge can
explain a component of K2, especially at mid/high depth. The projection scale is
reported as a diagnostic decomposition of K2, not as a fitted physical model and
not as measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROW_AUDIT = EVIDENCE / "provisional_backreaction_bridge_diagnosis_row.csv"

OUT_ROW = EVIDENCE / "backreaction_k2_component_split_row.csv"
OUT_ZONE = EVIDENCE / "backreaction_k2_component_split_zone.csv"
OUT_SUMMARY = EVIDENCE / "backreaction_k2_component_split_summary.csv"
OUT_DOC = DOCS / "backreaction_k2_component_split.md"


def depth_zone(z: float) -> str:
    if z < 0.9:
        return "low_depth"
    if z < 1.6:
        return "mid_depth"
    return "high_depth"


def chi2(residual: np.ndarray) -> float:
    return float(residual @ residual)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) == 0.0 or np.std(b) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def projection_scale(source: np.ndarray, basis: np.ndarray) -> float:
    denom = float(basis @ basis)
    if denom <= 0.0:
        return float("nan")
    return float((basis @ source) / denom)


def summarize_subset(route_id: str, subset_id: str, df: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame]:
    target = df["WhitenedTarget"].to_numpy(float)
    k1 = df["K1Whitened"].to_numpy(float)
    k2 = df["K2LockedWhitened"].to_numpy(float)
    br = df["BackreactionRawWhitened"].to_numpy(float)

    scale_k2_to_br = projection_scale(k2, br)
    br_component = scale_k2_to_br * br
    k2_residual = k2 - br_component

    k2_energy = float(k2 @ k2)
    br_component_energy = float(br_component @ br_component)
    residual_energy = float(k2_residual @ k2_residual)
    explained_fraction = br_component_energy / k2_energy if k2_energy > 0.0 else float("nan")

    combined_pred = k1 + k2_residual + br_component
    if not np.allclose(combined_pred, k1 + k2):
        raise AssertionError("component reconstruction changed locked K2 prediction")

    row_out = df.copy()
    row_out["SubsetID"] = subset_id
    row_out["K2ProjectedBackreactionScale"] = scale_k2_to_br
    row_out["BackreactionLikeK2Component"] = br_component
    row_out["K2ResidualFiniteMemoryComponent"] = k2_residual
    row_out["BackreactionComponentAbsFractionOfK2"] = np.divide(
        np.abs(br_component),
        np.maximum(np.abs(k2), 1e-12),
    )
    row_out["ResidualComponentAbsFractionOfK2"] = np.divide(
        np.abs(k2_residual),
        np.maximum(np.abs(k2), 1e-12),
    )
    row_out["K2ResidualCloserToTargetThanBackreactionComponent"] = (
        np.abs(target - k2_residual) < np.abs(target - br_component)
    )
    row_out["MeasurementValidationAllowed"] = False
    row_out["ClaimBoundary"] = "backreaction_k2_component_split_no_measurement_validation"

    summary = {
        "DiagnosisID": "BACKREACTION_K2_COMPONENT_SPLIT_V1",
        "RouteID": route_id,
        "SubsetID": subset_id,
        "Rows": len(df),
        "K2ProjectedBackreactionScale": scale_k2_to_br,
        "K2Energy": k2_energy,
        "BackreactionLikeComponentEnergy": br_component_energy,
        "K2ResidualEnergy": residual_energy,
        "BackreactionLikeEnergyFractionOfK2": explained_fraction,
        "CorrelationBackreactionComponentWithK2": corr(br_component, k2),
        "CorrelationK2ResidualWithTarget": corr(k2_residual, target),
        "CorrelationBackreactionComponentWithTarget": corr(br_component, target),
        "K2Chi2ToTarget": chi2(target - k2),
        "BackreactionComponentChi2ToTarget": chi2(target - br_component),
        "K2ResidualChi2ToTarget": chi2(target - k2_residual),
        "K1PlusLockedK2Chi2ToTarget": chi2(target - (k1 + k2)),
        "K1PlusResidualOnlyChi2ToTarget": chi2(target - (k1 + k2_residual)),
        "ScaleFitAllowed": False,
        "LockedK2Changed": False,
        "MeasurementValidationAllowed": False,
        "CurrentStatus": "BACKREACTION_LIKE_COMPONENT_DIAGNOSTIC_ONLY",
        "ClaimBoundary": "backreaction_k2_component_split_no_measurement_validation",
    }
    return summary, row_out


def main() -> None:
    row = pd.read_csv(ROW_AUDIT)
    if "DepthZone" not in row.columns:
        row["DepthZone"] = row["z_grid"].map(depth_zone)

    summaries = []
    row_frames = []
    for route_id, group in row.groupby("RouteID", sort=True):
        for subset_id, subset in [
            ("all_depth", group),
            ("mid_high_depth", group[group["DepthZone"].ne("low_depth")]),
            ("high_depth", group[group["DepthZone"].eq("high_depth")]),
            ("mid_depth", group[group["DepthZone"].eq("mid_depth")]),
            ("low_depth", group[group["DepthZone"].eq("low_depth")]),
        ]:
            if subset.empty:
                continue
            summary, rows = summarize_subset(route_id, subset_id, subset)
            summaries.append(summary)
            row_frames.append(rows)

    zone = pd.DataFrame(summaries)
    row_out = pd.concat(row_frames, ignore_index=True)
    zone.to_csv(OUT_ZONE, index=False)
    row_out.to_csv(OUT_ROW, index=False)

    mid_high = zone[zone["SubsetID"].eq("mid_high_depth")]
    high = zone[zone["SubsetID"].eq("high_depth")]
    overall = pd.DataFrame(
        [
            {
                "DiagnosisID": "BACKREACTION_K2_COMPONENT_SPLIT_V1",
                "Routes": zone["RouteID"].nunique(),
                "Subsets": len(zone),
                "MidHighBackreactionEnergyFractionMean": float(mid_high["BackreactionLikeEnergyFractionOfK2"].mean()),
                "HighBackreactionEnergyFractionMean": float(high["BackreactionLikeEnergyFractionOfK2"].mean()),
                "MidHighBackreactionComponentTargetCorrelationMean": float(mid_high["CorrelationBackreactionComponentWithTarget"].mean()),
                "MidHighResidualTargetCorrelationMean": float(mid_high["CorrelationK2ResidualWithTarget"].mean()),
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "BACKREACTION_COMPONENT_PRESENT_BUT_NOT_SUFFICIENT_AS_STANDALONE_EXPLANATION",
                "StrongestAllowedClaim": (
                    "the provisional backreaction bridge explains a diagnostic component of locked K2, "
                    "mainly outside the low-depth regime, but does not replace the finite-memory residual"
                ),
                "PrimaryResidualRisk": "projection scale is diagnostic and the backreaction observable bridge is not source-native",
                "NextAction": "test the same split with source-native symbolic-regression backreaction reconstruction when available",
                "ClaimBoundary": "backreaction_k2_component_split_no_measurement_validation",
            }
        ]
    )
    overall.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Backreaction-K2 Component Split",
        "",
        "Status: diagnostic decomposition only; locked K2 unchanged.",
        "",
        "This split projects locked K2 onto the provisional BAO-only backreaction bridge and reports the residual. The projection is not a fitted physical model; it is a diagnostic for whether backreaction-like structure is present inside K2.",
        "",
        "## Outputs",
        "",
        f"- Row split: `{OUT_ROW.relative_to(ROOT)}`",
        f"- Zone split: `{OUT_ZONE.relative_to(ROOT)}`",
        f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
        "",
        "## Claim Boundary",
        "",
        "No measurement validation, no K2 change, no fitted new model. The result can only guide the next source-native backreaction test.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_ZONE}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
