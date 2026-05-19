#!/usr/bin/env python3
"""Score source-split K1 response candidates and their locked K2 responses."""

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
CANDIDATES = EVIDENCE / "source_split_k1_response_candidate_audit.csv"
COV = EVIDENCE / "source_split_joint_covariance_policy.csv"
SIGN = EVIDENCE / "source_split_family_sign_rule_preview.csv"
OUT = EVIDENCE / "source_split_k1_candidate_sensitivity.csv"
SUMMARY = EVIDENCE / "source_split_k1_candidate_sensitivity_summary.csv"


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
    candidate_id: str,
    prediction: np.ndarray,
    target: np.ndarray,
    covariance: np.ndarray,
    stable: np.ndarray,
    parameter_count: int,
    rho: float | None,
    candidate_class: str,
    allowed_primary: bool,
) -> dict[str, object]:
    c2 = chi2(target, prediction, covariance)
    violations = sign_stable_violations(prediction, target, stable)
    return {
        "SensitivityID": "SOURCE_SPLIT_K1_CANDIDATE_SENSITIVITY_V1",
        "ModelID": model_id,
        "K1CandidateID": candidate_id,
        "CandidateClass": candidate_class,
        "AllowedAsPrimaryK1": allowed_primary,
        "ParameterCount": parameter_count,
        "rho": "" if rho is None else rho,
        "p": 3 if rho is not None else "",
        "Chi2": c2,
        "AIC": aic(c2, parameter_count),
        "BIC": bic(c2, parameter_count, len(target)),
        "SignStableViolations": violations,
        "MaxAbsWhitenedResidual": max_abs_whitened_residual(target, prediction, covariance),
        "Status": "STRICT_GATE_WARNING" if violations else "NON_VIOLATING_SENSITIVITY",
        "ClaimBoundary": "k1_candidate_sensitivity_only_no_measurement_validation",
    }


def main() -> None:
    target = pd.read_csv(TARGET)
    candidates = pd.read_csv(CANDIDATES)
    cov_rows = pd.read_csv(COV)
    sign_rows = pd.read_csv(SIGN)

    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].sort_values("GridIndex")
    grid_indices = usable["GridIndex"].astype(int).tolist()
    y = usable["SourceSplitResponse"].to_numpy(float)
    x = usable["x_coordinate"].to_numpy(float)
    covariance = covariance_matrix(cov_rows, grid_indices)
    stable = (
        sign_rows[sign_rows["GridIndex"].astype(int).isin(grid_indices)]
        .sort_values("GridIndex")["FamilySignStable"]
        .astype(str)
        .str.lower()
        .eq("true")
        .to_numpy()
    )

    rows = []
    for candidate_id, group in candidates.groupby("K1CandidateID", sort=False):
        ordered = group.sort_values("GridIndex")
        k1 = ordered["K1Response"].to_numpy(float)
        candidate_class = str(ordered["CandidateClass"].iloc[0])
        allowed_primary = bool(ordered["AllowedAsPrimaryK1"].iloc[0])
        rows.append(
            score(
                f"{candidate_id}_AS_K1",
                candidate_id,
                k1,
                y,
                covariance,
                stable,
                0,
                None,
                candidate_class,
                allowed_primary,
            )
        )
        rows.append(
            score(
                f"{candidate_id}_K2_RHO4",
                candidate_id,
                k2_from_k1(x, k1, rho=4.0),
                y,
                covariance,
                stable,
                0,
                4.0,
                candidate_class,
                allowed_primary,
            )
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    best = output.sort_values(["AIC", "Chi2"]).iloc[0]
    summary = pd.DataFrame(
        [
            {
                "SensitivityID": "SOURCE_SPLIT_K1_CANDIDATE_SENSITIVITY_V1",
                "Rows": len(y),
                "Candidates": int(candidates["K1CandidateID"].nunique()),
                "BestAICModel": best["ModelID"],
                "BestAICCandidateAllowedAsPrimaryK1": bool(best["AllowedAsPrimaryK1"]),
                "NonzeroCandidateCount": int(
                    candidates.groupby("K1CandidateID")["K1Nonzero"].any().sum()
                ),
                "Interpretation": "Nonzero K1 candidates are sensitivity controls until provenance is predeclared; do not use as measurement validation.",
                "ClaimBoundary": "k1_candidate_sensitivity_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
