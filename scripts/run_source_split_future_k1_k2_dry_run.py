#!/usr/bin/env python3
"""Run a future-only dry run using the external family-mean K1 candidate."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.operators import k2_from_k1

EVIDENCE = ROOT / "evidence"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
COV = EVIDENCE / "source_split_joint_covariance_policy.csv"
SIGN = EVIDENCE / "source_split_family_sign_rule_preview.csv"
RERUN = EVIDENCE / "source_split_future_rerun_protocol_summary.csv"
OUT = EVIDENCE / "source_split_future_k1_k2_dry_run.csv"
SUMMARY = EVIDENCE / "source_split_future_k1_k2_dry_run_summary.csv"


def covariance_matrix(cov_rows: pd.DataFrame, grid_indices: list[int]) -> np.ndarray:
    index_to_position = {grid: i for i, grid in enumerate(grid_indices)}
    matrix = np.zeros((len(grid_indices), len(grid_indices)), dtype=float)
    for _, row in cov_rows.iterrows():
        i = int(row["GridIndexI"])
        j = int(row["GridIndexJ"])
        if i in index_to_position and j in index_to_position:
            matrix[index_to_position[i], index_to_position[j]] = float(row["Covariance"])
    return matrix


def sign_stable_violations(prediction: np.ndarray, target: np.ndarray, stable: np.ndarray) -> int:
    return int(np.sum(np.sign(prediction[stable]) != np.sign(target[stable])))


def max_abs_whitened_residual(target: np.ndarray, prediction: np.ndarray, covariance: np.ndarray) -> float:
    sigma = np.sqrt(np.diag(covariance))
    return float(np.max(np.abs((target - prediction) / sigma)))


def score(
    model_id: str,
    prediction: np.ndarray,
    target: np.ndarray,
    covariance: np.ndarray,
    stable: np.ndarray,
    parameter_count: int,
    rho: float | None,
    notes: str,
) -> dict[str, object]:
    c2 = chi2(target, prediction, covariance)
    violations = sign_stable_violations(prediction, target, stable)
    return {
        "DryRunID": "SOURCE_SPLIT_FUTURE_K1_K2_DRY_RUN_V1",
        "ModelID": model_id,
        "ParameterCount": parameter_count,
        "rho": "" if rho is None else rho,
        "p": 3 if rho is not None else "",
        "Chi2": c2,
        "AIC": aic(c2, parameter_count),
        "BIC": bic(c2, parameter_count, len(target)),
        "SignStableViolations": violations,
        "MaxAbsWhitenedResidual": max_abs_whitened_residual(target, prediction, covariance),
        "Status": "STRICT_GATE_WARNING" if violations else "NON_VIOLATING_FUTURE_DRY_RUN",
        "Notes": notes,
        "ClaimBoundary": "future_only_dry_run_no_current_measurement_validation",
    }


def main() -> None:
    rerun = pd.read_csv(RERUN)
    current_allowed = bool(rerun["AllowedCurrentRerunCount"].iloc[0])

    target = pd.read_csv(TARGET)
    k1 = pd.read_csv(K1)
    cov_rows = pd.read_csv(COV)
    sign_rows = pd.read_csv(SIGN)

    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].sort_values("GridIndex")
    grid_indices = usable["GridIndex"].astype(int).tolist()
    k1_usable = k1[k1["GridIndex"].astype(int).isin(grid_indices)].sort_values("GridIndex")
    sign_usable = sign_rows[sign_rows["GridIndex"].astype(int).isin(grid_indices)].sort_values("GridIndex")

    x = usable["x_coordinate"].to_numpy(float)
    y = usable["SourceSplitResponse"].to_numpy(float)
    k1_response = k1_usable["K1Response"].to_numpy(float)
    covariance = covariance_matrix(cov_rows, grid_indices)
    stable = sign_usable["FamilySignStable"].astype(str).str.lower().eq("true").to_numpy()

    models = [
        (
            "K1_FAMILY_MEAN_NO_MEMORY_FUTURE_ONLY",
            k1_response,
            0,
            None,
            "future-only family-mean K1; not current primary K1",
        ),
        (
            "K2_FAMILY_MEAN_RHO3_FUTURE_ONLY",
            k2_from_k1(x, k1_response, rho=3.0),
            0,
            3.0,
            "locked K2 applied to future-only family-mean K1 with rho=3",
        ),
        (
            "K2_FAMILY_MEAN_RHO4_FUTURE_ONLY",
            k2_from_k1(x, k1_response, rho=4.0),
            0,
            4.0,
            "locked K2 applied to future-only family-mean K1 with rho=4",
        ),
        (
            "ZERO_RESPONSE_NULL",
            np.zeros_like(y),
            0,
            None,
            "zero response no-memory null",
        ),
        (
            "POLY_DEG2_CONTROL",
            np.polyval(np.polyfit(x, y, 2), x),
            3,
            None,
            "degree-2 diagnostic control; not a physical K1",
        ),
    ]

    rows = [
        score(model_id, prediction, y, covariance, stable, k, rho, notes)
        for model_id, prediction, k, rho, notes in models
    ]
    output = pd.DataFrame(rows)
    k2 = output[output["ModelID"].eq("K2_FAMILY_MEAN_RHO4_FUTURE_ONLY")].iloc[0]
    k1_row = output[output["ModelID"].eq("K1_FAMILY_MEAN_NO_MEMORY_FUTURE_ONLY")].iloc[0]
    output["DeltaAICVsK2Rho4"] = output["AIC"].astype(float) - float(k2["AIC"])
    output["DeltaAICVsK1FamilyMean"] = output["AIC"].astype(float) - float(k1_row["AIC"])
    output.to_csv(OUT, index=False)

    best = output.sort_values(["AIC", "Chi2"]).iloc[0]
    summary = pd.DataFrame(
        [
            {
                "DryRunID": "SOURCE_SPLIT_FUTURE_K1_K2_DRY_RUN_V1",
                "Rows": len(y),
                "CurrentRerunAuthorized": current_allowed,
                "FutureOnlyK1Available": True,
                "BestAICModel": best["ModelID"],
                "K1FamilyMeanAIC": float(k1_row["AIC"]),
                "K2Rho4AIC": float(k2["AIC"]),
                "DeltaAICK2Rho4MinusK1": float(k2["AIC"]) - float(k1_row["AIC"]),
                "K2Rho4SignStableViolations": int(k2["SignStableViolations"]),
                "Interpretation": "Future-only diagnostic dry run; current measurement gate remains closed.",
                "ClaimBoundary": "future_only_dry_run_no_current_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
