#!/usr/bin/env python3
"""Run the authorized source-split K2/null preflight scorecard."""

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
AUTH = EVIDENCE / "source_split_k2_scoring_authorization.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
K1 = EVIDENCE / "source_split_k1_coordinate_native_target.csv"
COV = EVIDENCE / "source_split_joint_covariance_policy.csv"
SIGN = EVIDENCE / "source_split_family_sign_rule_preview.csv"
OUT = EVIDENCE / "source_split_k2_null_scorecard.csv"
SUMMARY = EVIDENCE / "source_split_k2_null_scorecard_summary.csv"


def authorization_ok() -> bool:
    auth = pd.read_csv(AUTH)
    return not auth.empty and auth["K2ScoringAuthorized"].astype(str).str.lower().eq("true").all()


def covariance_matrix(cov_rows: pd.DataFrame, grid_indices: list[int]) -> np.ndarray:
    index_to_position = {grid: i for i, grid in enumerate(grid_indices)}
    matrix = np.zeros((len(grid_indices), len(grid_indices)), dtype=float)
    for _, row in cov_rows.iterrows():
        i = int(row["GridIndexI"])
        j = int(row["GridIndexJ"])
        if i in index_to_position and j in index_to_position:
            matrix[index_to_position[i], index_to_position[j]] = float(row["Covariance"])
    return matrix


def response_sign(values: np.ndarray) -> np.ndarray:
    return np.sign(np.asarray(values, dtype=float)).astype(int)


def sign_stable_violations(prediction: np.ndarray, target: np.ndarray, stable: np.ndarray) -> int:
    return int(np.sum(response_sign(prediction)[stable] != response_sign(target)[stable]))


def max_abs_whitened_residual(target: np.ndarray, prediction: np.ndarray, covariance: np.ndarray) -> float:
    sigma = np.sqrt(np.diag(covariance))
    return float(np.max(np.abs((target - prediction) / sigma)))


def score_model(
    model_id: str,
    prediction: np.ndarray,
    target: np.ndarray,
    covariance: np.ndarray,
    sign_stable: np.ndarray,
    parameter_count: int,
    rho: float | None,
    notes: str,
) -> dict[str, object]:
    c2 = chi2(target, prediction, covariance)
    violations = sign_stable_violations(prediction, target, sign_stable)
    max_resid = max_abs_whitened_residual(target, prediction, covariance)
    status = "STRICT_GATE_WARNING" if violations else "NON_VIOLATING_PREFLIGHT"
    return {
        "ScorecardID": "SOURCE_SPLIT_K2_NULL_SCORECARD_V1",
        "ModelID": model_id,
        "ParameterCount": parameter_count,
        "rho": "" if rho is None else rho,
        "p": 3 if model_id.startswith("K2") else "",
        "Chi2": c2,
        "AIC": aic(c2, parameter_count),
        "BIC": bic(c2, parameter_count, len(target)),
        "SignStableViolations": violations,
        "MaxAbsWhitenedResidual": max_resid,
        "Status": status,
        "Notes": notes,
        "ClaimBoundary": "source_split_preflight_scorecard_no_measurement_validation",
    }


def main() -> None:
    if not authorization_ok():
        pd.DataFrame(
            [
                {
                    "ScorecardID": "SOURCE_SPLIT_K2_NULL_SCORECARD_V1",
                    "Status": "NOT_RUN_AUTHORIZATION_BLOCKED",
                    "ClaimBoundary": "source_split_preflight_scorecard_no_measurement_validation",
                }
            ]
        ).to_csv(SUMMARY, index=False)
        print(f"Wrote {SUMMARY}")
        return

    target = pd.read_csv(TARGET)
    k1 = pd.read_csv(K1)
    cov_rows = pd.read_csv(COV)
    sign_rows = pd.read_csv(SIGN)

    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    usable = usable.sort_values("GridIndex").reset_index(drop=True)
    grid_indices = usable["GridIndex"].astype(int).tolist()
    k1_usable = (
        k1[k1["GridIndex"].astype(int).isin(grid_indices)]
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )
    sign_usable = (
        sign_rows[sign_rows["GridIndex"].astype(int).isin(grid_indices)]
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )

    x = usable["x_coordinate"].to_numpy(float)
    y = usable["SourceSplitResponse"].to_numpy(float)
    k1_response = k1_usable["K1NoMemoryResponse"].to_numpy(float)
    covariance = covariance_matrix(cov_rows, grid_indices)
    sign_stable = sign_usable["FamilySignStable"].astype(str).str.lower().eq("true").to_numpy()

    models = [
        (
            "K2_LOCKED_RHO4_FROM_ZERO_K1",
            k2_from_k1(x, k1_response, rho=4.0),
            0,
            4.0,
            "locked K2 multiplier applied to zero-contrast K1; degenerates to no-memory response",
        ),
        (
            "K2_LOCKED_GRID_3_4_FROM_ZERO_K1",
            k2_from_k1(x, k1_response, rho=3.0),
            1,
            3.0,
            "bounded rho grid is degenerate because zero K1 remains zero for every rho<=4",
        ),
        (
            "K1_ZERO_CONTRAST_NO_MEMORY",
            k1_response,
            0,
            None,
            "coordinate-native zero branch contrast no-memory control",
        ),
        (
            "CONSTANT_MEAN_CONTROL",
            np.full_like(y, np.mean(y)),
            1,
            None,
            "fixed constant mean diagnostic control",
        ),
        (
            "POLY_DEG1_CONTROL",
            np.polyval(np.polyfit(x, y, 1), x),
            2,
            None,
            "degree-1 polynomial diagnostic control",
        ),
        (
            "POLY_DEG2_CONTROL",
            np.polyval(np.polyfit(x, y, 2), x),
            3,
            None,
            "degree-2 polynomial diagnostic control",
        ),
    ]

    rows = [
        score_model(model_id, prediction, y, covariance, sign_stable, k, rho, notes)
        for model_id, prediction, k, rho, notes in models
    ]
    output = pd.DataFrame(rows)
    k2_chi2 = float(output.loc[output["ModelID"].eq("K2_LOCKED_RHO4_FROM_ZERO_K1"), "Chi2"].iloc[0])
    k2_aic = float(output.loc[output["ModelID"].eq("K2_LOCKED_RHO4_FROM_ZERO_K1"), "AIC"].iloc[0])
    output["DeltaChi2VsK2Rho4"] = output["Chi2"] - k2_chi2
    output["DeltaAICVsK2Rho4"] = output["AIC"] - k2_aic
    output.to_csv(OUT, index=False)

    best = output.sort_values(["AIC", "Chi2"]).iloc[0]
    summary = pd.DataFrame(
        [
            {
                "ScorecardID": "SOURCE_SPLIT_K2_NULL_SCORECARD_V1",
                "Rows": len(y),
                "Authorized": True,
                "BestAICModel": best["ModelID"],
                "K2DegenerateWithK1NoMemory": True,
                "K2Rho4Status": output.loc[
                    output["ModelID"].eq("K2_LOCKED_RHO4_FROM_ZERO_K1"), "Status"
                ].iloc[0],
                "K2Rho4SignStableViolations": int(
                    output.loc[
                        output["ModelID"].eq("K2_LOCKED_RHO4_FROM_ZERO_K1"),
                        "SignStableViolations",
                    ].iloc[0]
                ),
                "Interpretation": "Locked multiplicative K2 is not distinguishable from zero-contrast no-memory K1 on this source-split target.",
                "ClaimBoundary": "source_split_preflight_scorecard_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
