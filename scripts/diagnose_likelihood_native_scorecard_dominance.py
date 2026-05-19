#!/usr/bin/env python3
"""Row-level diagnosis for the likelihood-native preflight scorecard."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.operators import w_k2_locked

EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
AUDIT_OUT = ROOT / "evidence" / "source_split_likelihood_native_scorecard_dominance_audit.csv"
SUMMARY_OUT = ROOT / "evidence" / "source_split_likelihood_native_scorecard_dominance_summary.csv"


def predictions(x: np.ndarray, y: np.ndarray, k1: np.ndarray) -> list[tuple[str, str, np.ndarray]]:
    rows: list[tuple[str, str, np.ndarray]] = [
        ("K1_NO_MEMORY", "fair_null", k1),
        ("K2_LOCKED_RHO4", "locked_prediction", w_k2_locked(x, rho=4.0) * k1),
        ("ZERO_RESPONSE_CONTROL", "diagnostic_control", np.zeros_like(y)),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        rows.append((f"POLY_DEG{degree}", "overfit_risk_control", np.polyval(coeff, x)))
    return rows


def main() -> None:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    data = external.merge(
        target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    x = data["x_coordinate"].to_numpy(float)
    z = data["z_grid"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    sigma = data["K1Sigma"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    rows = []
    for model_id, model_class, pred in predictions(x, y, k1):
        residual = y - pred
        ros = residual / sigma
        contribution = ros * ros
        order = np.argsort(-contribution)
        rank = np.empty_like(order)
        rank[order] = np.arange(1, len(order) + 1)
        sign_violation = stable & (np.sign(pred) != np.sign(y))
        for i in range(len(data)):
            if model_id == "K2_LOCKED_RHO4":
                local_note = "k2_multiplier_applied_to_likelihood_native_k1"
            elif model_id.startswith("POLY"):
                local_note = "flexible_shape_control_not_locked_prediction"
            else:
                local_note = "baseline_or_control"
            rows.append(
                {
                    "Dataset": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_PREFLIGHT",
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "GridIndex": int(data["GridIndex"].iloc[i]),
                    "z_grid": z[i],
                    "x_coordinate": x[i],
                    "target_response": y[i],
                    "k1_response": k1[i],
                    "sigma_diag": sigma[i],
                    "prediction": pred[i],
                    "residual": residual[i],
                    "residual_over_sigma": ros[i],
                    "chi2_contribution": contribution[i],
                    "ContributionRank": int(rank[i]),
                    "sign_stable": bool(stable[i]),
                    "sign_violation": bool(sign_violation[i]),
                    "Notes": local_note,
                    "ClaimBoundary": "dominance_diagnosis_only_no_measurement_validation",
                }
            )
    audit = pd.DataFrame(rows)
    audit.to_csv(AUDIT_OUT, index=False)

    summary = (
        audit.groupby(["ModelID", "ModelClass"], sort=False)
        .agg(
            Chi2DiagProxy=("chi2_contribution", "sum"),
            MaxContribution=("chi2_contribution", "max"),
            TopContributionGridIndex=(
                "GridIndex",
                lambda s: int(
                    audit.loc[
                        audit.loc[s.index, "chi2_contribution"].astype(float).idxmax(),
                        "GridIndex",
                    ]
                ),
            ),
            SignStableViolations=("sign_violation", lambda s: int(s.astype(bool).sum())),
            MeanAbsResidual=("residual", lambda s: float(np.mean(np.abs(s.astype(float))))),
        )
        .reset_index()
    )
    best_aic_proxy = summary.loc[summary["Chi2DiagProxy"].idxmin(), "ModelID"]
    summary["BestChi2Model"] = best_aic_proxy
    summary["Interpretation"] = np.where(
        summary["ModelID"].eq("K2_LOCKED_RHO4"),
        "k2_improves_over_k1_but_not_over_flexible_controls",
        np.where(summary["ModelID"].str.startswith("POLY"), "flexible_control_dominates", "comparison_baseline"),
    )
    summary["ClaimBoundary"] = "dominance_diagnosis_only_no_measurement_validation"
    summary.to_csv(SUMMARY_OUT, index=False)
    print(f"Wrote {AUDIT_OUT}")
    print(f"Wrote {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
