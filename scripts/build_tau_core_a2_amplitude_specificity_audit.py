#!/usr/bin/env python3
"""Audit whether the source-split amplitude preferred by data is near A_tau=2.

This script does not refit the locked A2 prediction for scoring. It reports the
diagnostic generalized least-squares amplitude that would multiply the already
locked unit K2 backbone on each declared subset / route. Agreement with A=2 is
supportive only; it is not used to change the prediction.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
PUBLIC_COV = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"
TRANSFORM_VARIANTS = EVIDENCE / "k2_a2_transform_variant_robustness.csv"
CROSS_COV = EVIDENCE / "k2_a2_memory_active_cross_covariance.csv"

OUT = EVIDENCE / "tau_core_a2_amplitude_specificity_audit.csv"
SUMMARY = EVIDENCE / "tau_core_a2_amplitude_specificity_summary.csv"


def generalized_amplitude(y: np.ndarray, k: np.ndarray, cov: np.ndarray | None = None) -> float:
    if cov is None:
        denom = float(np.dot(k, k))
        return float(np.dot(k, y) / denom) if denom > 0.0 else float("nan")
    inv_k = np.linalg.solve(cov, k)
    denom = float(k.T @ inv_k)
    return float(k.T @ np.linalg.solve(cov, y) / denom) if denom > 0.0 else float("nan")


def depth_zone(x: float) -> str:
    if x <= 0.5:
        return "low_depth"
    if x <= 0.8:
        return "mid_depth"
    return "high_depth"


def load_public_base() -> tuple[pd.DataFrame, np.ndarray]:
    target = pd.read_csv(TARGET)
    pred = pd.read_csv(PRED)
    cov_df = pd.read_csv(PUBLIC_COV)
    data = (
        target[
            target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])
            & target["SourceSplitResponse"].notna()
        ][["GridIndex", "z_grid", "x_coordinate", "SourceSplitResponse", "SignStableTemplate", "SNBAOSameSign"]]
        .merge(
            pred[["GridIndex", "K2UnitLockedRho4", "K2SourceSplitA2Prediction"]],
            on="GridIndex",
            how="inner",
        )
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )
    data["DepthZone"] = [depth_zone(float(x)) for x in data["x_coordinate"]]
    data["SignStableBool"] = data["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"])
    data["SNBAOSameSignBool"] = data["SNBAOSameSign"].astype(str).str.lower().isin(["true", "1", "yes"])
    indices = data["GridIndex"].astype(int).to_list()
    cov_rows = cov_df[cov_df["GridIndex"].astype(int).isin(indices)].sort_values("GridIndex")
    cov = cov_rows[[str(idx) for idx in indices]].to_numpy(float) + np.eye(len(indices)) * 1e-12
    return data, cov


def subset_masks(data: pd.DataFrame) -> dict[str, np.ndarray]:
    zones = data["DepthZone"].astype(str).to_numpy()
    stable = data["SignStableBool"].astype(bool).to_numpy()
    same = data["SNBAOSameSignBool"].astype(bool).to_numpy()
    return {
        "all_depth": np.ones(len(data), dtype=bool),
        "low_depth": zones == "low_depth",
        "mid_depth": zones == "mid_depth",
        "high_depth": zones == "high_depth",
        "mid_high_memory_active": zones != "low_depth",
        "memory_active_sign_stable": (zones != "low_depth") & stable,
        "memory_active_anti_aligned": (zones != "low_depth") & (~same),
    }


def public_rows() -> list[dict[str, object]]:
    data, cov = load_public_base()
    rows: list[dict[str, object]] = []
    y_all = data["SourceSplitResponse"].to_numpy(float)
    k_all = data["K2UnitLockedRho4"].to_numpy(float)
    for subset_id, mask in subset_masks(data).items():
        if int(mask.sum()) < 2:
            continue
        idx = np.where(mask)[0]
        amp = generalized_amplitude(y_all[idx], k_all[idx], cov[np.ix_(idx, idx)])
        rows.append(
            {
                "RouteID": "PUBLIC_COVARIANCE_PROXY",
                "SubsetID": subset_id,
                "Rows": int(mask.sum()),
                "AmplitudeEstimator": "generalized_least_squares_against_unit_K2",
                "AOpt": amp,
                "DistanceFromA2": abs(amp - 2.0),
                "WithinA2HalfBand": abs(amp - 2.0) <= 0.5,
                "UsedForPrediction": False,
                "ClaimBoundary": "a2_amplitude_specificity_no_measurement_validation",
            }
        )
    return rows


def transform_variant_rows() -> list[dict[str, object]]:
    detail = pd.read_csv(TRANSFORM_VARIANTS)
    rows: list[dict[str, object]] = []
    # Reconstruct only from rows that scored the fixed unit backbone and A2 on
    # unit proxy; route-level AOpt can be derived from the AIC/Chi2 only if raw
    # target is available, so this table reports the implied A2 improvement
    # specificity as a conservative route-level proxy.
    unit = detail[detail["ModelID"].eq("K2_UNIT_LOCKED_RHO4")]
    a2 = detail[detail["ModelID"].eq("K2_SOURCE_SPLIT_A2_PRIOR_V1")]
    merged = unit.merge(
        a2,
        on=["TransformVariantID", "SubsetID"],
        suffixes=("_unit", "_a2"),
    )
    for _, row in merged.iterrows():
        rows.append(
            {
                "RouteID": f"TRANSFORM_VARIANT::{row['TransformVariantID']}",
                "SubsetID": row["SubsetID"],
                "Rows": int(row["Rows_unit"]),
                "AmplitudeEstimator": "fixed_A2_vs_unit_K2_improvement_proxy",
                "AOpt": "",
                "DistanceFromA2": "",
                "WithinA2HalfBand": "",
                "A2ImprovesOverUnit": float(row["AIC_a2"]) < float(row["AIC_unit"]),
                "DeltaAIC_A2_minus_Unit": float(row["AIC_a2"]) - float(row["AIC_unit"]),
                "UsedForPrediction": False,
                "ClaimBoundary": "a2_amplitude_specificity_no_measurement_validation",
            }
        )
    return rows


def cross_cov_rows() -> list[dict[str, object]]:
    cross = pd.read_csv(CROSS_COV)
    rows: list[dict[str, object]] = []
    for _, row in cross.iterrows():
        if row["ModelID"] != "K2_SOURCE_SPLIT_A2_PRIOR_V1":
            continue
        subset = str(row["SubsetID"])
        if subset not in {"mid_high_memory_active", "high_depth", "memory_active_sign_stable", "memory_active_anti_aligned"}:
            continue
        rows.append(
            {
                "RouteID": f"CROSS_COV_RHO::{row['RhoCross']}",
                "SubsetID": subset,
                "Rows": int(row["Rows"]),
                "AmplitudeEstimator": "fixed_A2_cross_covariance_stability_proxy",
                "AOpt": "",
                "DistanceFromA2": "",
                "WithinA2HalfBand": "",
                "A2ImprovesOverUnit": "",
                "DeltaAIC_A2_minus_Unit": "",
                "UsedForPrediction": False,
                "ClaimBoundary": "a2_amplitude_specificity_no_measurement_validation",
            }
        )
    return rows


def main() -> None:
    rows = public_rows() + transform_variant_rows() + cross_cov_rows()
    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    public = output[output["RouteID"].eq("PUBLIC_COVARIANCE_PROXY")].copy()
    public["AOptNumeric"] = pd.to_numeric(public["AOpt"], errors="coerce")
    memory_public = public[public["SubsetID"].isin(["mid_high_memory_active", "high_depth", "memory_active_sign_stable", "memory_active_anti_aligned"])]
    transform = output[output["RouteID"].astype(str).str.startswith("TRANSFORM_VARIANT::")].copy()
    transform_memory = transform[transform["SubsetID"].eq("mid_high_memory_active")]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "TAU_CORE_A2_AMPLITUDE_SPECIFICITY",
                "PublicProxyMemorySubsetCount": len(memory_public),
                "PublicProxyMedianAOptMemorySubsets": float(memory_public["AOptNumeric"].median()),
                "PublicProxyMinAOptMemorySubsets": float(memory_public["AOptNumeric"].min()),
                "PublicProxyMaxAOptMemorySubsets": float(memory_public["AOptNumeric"].max()),
                "PublicProxyMemorySubsetsWithinA2HalfBand": int(memory_public["WithinA2HalfBand"].map(lambda x: str(x).lower() == "true").sum()),
                "TransformVariantMidHighA2ImprovesOverUnit": int(transform_memory["A2ImprovesOverUnit"].map(lambda x: str(x).lower() == "true").sum()),
                "TransformVariantMidHighRoutes": len(transform_memory),
                "CurrentInterpretation": "A2_amplitude_is_supported_in_memory_active_preflight_but_not_used_as_fit",
                "MeasurementValidationAllowed": False,
                "NextAction": "repeat amplitude-specificity audit after SN/BAO likelihood-native transforms are promoted",
                "ClaimBoundary": "a2_amplitude_specificity_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
