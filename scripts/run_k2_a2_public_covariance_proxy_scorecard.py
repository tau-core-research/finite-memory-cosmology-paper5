#!/usr/bin/env python3
"""Score locked K2_A2 under the existing public covariance proxy."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
COV = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT = EVIDENCE / "k2_a2_public_covariance_proxy_scorecard.csv"
SUMMARY = EVIDENCE / "k2_a2_public_covariance_proxy_summary.csv"


def chi2(y: np.ndarray, pred: np.ndarray, cov: np.ndarray) -> float:
    residual = y - pred
    return float(residual.T @ np.linalg.solve(cov, residual))


def aic(chi2_value: float, k: int) -> float:
    return float(chi2_value + 2 * k)


def bic(chi2_value: float, k: int, n: int) -> float:
    return float(chi2_value + k * np.log(n))


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def model_rows(x: np.ndarray, y: np.ndarray, k1: np.ndarray, k2_unit: np.ndarray, k2_a2: np.ndarray):
    rows: list[tuple[str, np.ndarray, int, str]] = [
        ("K1_NO_MEMORY", k1, 0, "fair_null"),
        ("K2_UNIT_LOCKED_RHO4", k2_unit, 0, "locked_memory_backbone"),
        ("K2_SOURCE_SPLIT_A2_PRIOR_V1", k2_a2, 0, "locked_projection_prior"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        rows.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))
    return rows


def main() -> None:
    target = pd.read_csv(TARGET)
    pred = pd.read_csv(PRED)
    cov_df = pd.read_csv(COV)
    usable = target[
        target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])
        & target["SourceSplitResponse"].notna()
    ][["GridIndex", "SourceSplitResponse", "SignStableTemplate"]]
    data = usable.merge(
        pred[["GridIndex", "x_coordinate", "K1Response", "K2UnitLockedRho4", "K2SourceSplitA2Prediction"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")

    indices = data["GridIndex"].astype(int).to_list()
    cov_rows = cov_df[cov_df["GridIndex"].astype(int).isin(indices)].sort_values("GridIndex")
    cov = cov_rows[[str(idx) for idx in indices]].to_numpy(float)
    cov = cov + np.eye(len(cov)) * 1e-12

    y = data["SourceSplitResponse"].to_numpy(float)
    x = data["x_coordinate"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    k2_unit = data["K2UnitLockedRho4"].to_numpy(float)
    k2_a2 = data["K2SourceSplitA2Prediction"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"]).to_numpy()

    rows = []
    for model_id, values, k, model_class in model_rows(x, y, k1, k2_unit, k2_a2):
        c2 = chi2(y, values, cov)
        rows.append(
            {
                "CovarianceID": "PUBLIC_SN_BAO_PROPAGATED_PROXY_V1",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": k,
                "PredictionToTargetRMSRatio": rms(values) / rms(y) if rms(y) > 0.0 else float("nan"),
                "CosineTargetVsPrediction": cosine(y, values),
                "Chi2": c2,
                "AIC": aic(c2, k),
                "BIC": bic(c2, k, len(y)),
                "MeanAbsResidual": float(np.mean(np.abs(y - values))),
                "SignStableViolations": int(np.sum(np.sign(values[stable]) != np.sign(y[stable]))),
                "SignMatchFraction": float(np.mean(np.sign(values) == np.sign(y))),
                "ClaimBoundary": "a2_public_covariance_proxy_no_measurement_validation",
            }
        )

    scorecard = pd.DataFrame(rows)
    a2_aic = float(scorecard.loc[scorecard["ModelID"].eq("K2_SOURCE_SPLIT_A2_PRIOR_V1"), "AIC"].iloc[0])
    unit_aic = float(scorecard.loc[scorecard["ModelID"].eq("K2_UNIT_LOCKED_RHO4"), "AIC"].iloc[0])
    scorecard["DeltaAICVsA2"] = scorecard["AIC"] - a2_aic
    scorecard["DeltaAICVsUnitK2"] = scorecard["AIC"] - unit_aic
    scorecard.to_csv(OUT, index=False)

    best = scorecard.loc[scorecard["AIC"].idxmin()]
    best_poly_aic = float(scorecard[scorecard["ModelID"].str.startswith("POLY")]["AIC"].min())
    k1_aic = float(scorecard.loc[scorecard["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
    summary = pd.DataFrame(
        [
            {
                "CovarianceID": "PUBLIC_SN_BAO_PROPAGATED_PROXY_V1",
                "Rows": len(y),
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2UnitAIC": unit_aic,
                "K2A2AIC": a2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_A2_minus_K1": a2_aic - k1_aic,
                "DeltaAIC_A2_minus_UnitK2": a2_aic - unit_aic,
                "DeltaAIC_A2_minus_BestPoly": a2_aic - best_poly_aic,
                "A2ImprovesOverK1": a2_aic < k1_aic,
                "A2ImprovesOverUnitK2": a2_aic < unit_aic,
                "A2BeatsBestPoly": a2_aic < best_poly_aic,
                "RawPublicCovariancesUsed": True,
                "SNBAOCrossCovarianceIncluded": False,
                "CovarianceStatus": "public_covariance_proxy_not_full_likelihood",
                "Interpretation": "a2_improves_locked_k2_but_polynomial_control_still_competitive"
                if a2_aic >= best_poly_aic
                else "a2_competitive_under_public_covariance_proxy",
                "ClaimBoundary": "a2_public_covariance_proxy_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
