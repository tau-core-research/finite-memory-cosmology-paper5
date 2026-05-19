#!/usr/bin/env python3
"""Row-level diagnosis for the physical-null preflight scorecard."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.operators import w_k2_locked

EVIDENCE = ROOT / "evidence"
DATA_K1 = ROOT / "data" / "k1"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
EXTERNAL_K1 = DATA_K1 / "source_split_external_k1_response.csv"
TEMPLATES = EVIDENCE / "physical_null_proxy_templates.csv"
BRANCH_SCATTER = EVIDENCE / "source_split_likelihood_native_branch_scatter_covariance.csv"

OUT_AUDIT = EVIDENCE / "physical_null_preflight_row_audit.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_preflight_row_summary.csv"


def load_base_frame() -> pd.DataFrame:
    target = pd.read_csv(TARGET)
    target = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    k1 = pd.read_csv(EXTERNAL_K1)
    scatter = pd.read_csv(BRANCH_SCATTER)
    return (
        target.merge(k1[["GridIndex", "K1Response"]], on="GridIndex", how="inner")
        .merge(scatter[["GridIndex", "SigmaMaxNativeScatter"]], on="GridIndex", how="inner")
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )


def physical_predictions(base: pd.DataFrame) -> list[tuple[str, str, float, np.ndarray]]:
    templates = pd.read_csv(TEMPLATES)
    rows: list[tuple[str, str, float, np.ndarray]] = []
    for template_id, group in templates.groupby("TemplateID"):
        aligned = base[["GridIndex"]].merge(group[["GridIndex", "NullID", "ProxyValue"]], on="GridIndex", how="left")
        if aligned["ProxyValue"].isna().any():
            raise ValueError(f"Template {template_id} is not aligned to target rows.")
        null_id = str(aligned["NullID"].iloc[0])
        shape = aligned["ProxyValue"].to_numpy(float)
        rows.append((f"{null_id}_{template_id}_A+1.0_UNIT_ONLY", null_id, 1.0, shape))
        for amp in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            rows.append((f"{null_id}_{template_id}_A{amp:+.1f}_BOUNDED_GRID", null_id, amp, amp * shape))
    return rows


def classify_row(k2_contrib: float, best_physical_contrib: float, k1_contrib: float) -> str:
    if k2_contrib < best_physical_contrib and k2_contrib < k1_contrib:
        return "K2_ROW_STRONGER_THAN_K1_AND_PHYSICAL_NULLS"
    if k2_contrib < best_physical_contrib:
        return "K2_ROW_STRONGER_THAN_PHYSICAL_NULLS"
    if best_physical_contrib < k2_contrib:
        return "PHYSICAL_NULL_ROW_STRONGER_THAN_K2"
    return "ROW_TIE_OR_NUMERICALLY_NEAR"


def main() -> None:
    base = load_base_frame()
    y = base["SourceSplitResponse"].to_numpy(float)
    x = base["x_coordinate"].to_numpy(float)
    k1 = base["K1Response"].to_numpy(float)
    sigma = base["SigmaMaxNativeScatter"].to_numpy(float)
    stable = base["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    k2 = w_k2_locked(x, rho=4.0) * k1
    k1_contrib = ((y - k1) / sigma) ** 2
    k2_contrib = ((y - k2) / sigma) ** 2

    physical_rows = []
    for model_id, null_id, amp, pred in physical_predictions(base):
        contrib = ((y - pred) / sigma) ** 2
        for idx, row in base.iterrows():
            physical_rows.append(
                {
                    "GridIndex": int(row["GridIndex"]),
                    "PhysicalModelID": model_id,
                    "NullID": null_id,
                    "Amplitude": amp,
                    "PhysicalPrediction": float(pred[idx]),
                    "PhysicalResidual": float(y[idx] - pred[idx]),
                    "PhysicalChi2Contribution": float(contrib[idx]),
                }
            )
    physical = pd.DataFrame(physical_rows)
    best_idx = physical.groupby("GridIndex")["PhysicalChi2Contribution"].idxmin()
    best = physical.loc[best_idx].sort_values("GridIndex").reset_index(drop=True)

    audit_rows = []
    for idx, row in base.iterrows():
        best_row = best[best["GridIndex"].eq(int(row["GridIndex"]))].iloc[0]
        k2_residual = float(y[idx] - k2[idx])
        k1_residual = float(y[idx] - k1[idx])
        sign_violation_k2 = bool(stable[idx] and np.sign(k2[idx]) != np.sign(y[idx]))
        sign_violation_best_physical = bool(
            stable[idx] and np.sign(float(best_row["PhysicalPrediction"])) != np.sign(y[idx])
        )
        audit_rows.append(
            {
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_coordinate": float(row["x_coordinate"]),
                "Target": float(y[idx]),
                "SigmaMaxNativeScatter": float(sigma[idx]),
                "SignStable": bool(stable[idx]),
                "K1Prediction": float(k1[idx]),
                "K2Prediction": float(k2[idx]),
                "K1Residual": k1_residual,
                "K2Residual": k2_residual,
                "K1Chi2Contribution": float(k1_contrib[idx]),
                "K2Chi2Contribution": float(k2_contrib[idx]),
                "BestPhysicalModelID": best_row["PhysicalModelID"],
                "BestPhysicalNullID": best_row["NullID"],
                "BestPhysicalAmplitude": float(best_row["Amplitude"]),
                "BestPhysicalPrediction": float(best_row["PhysicalPrediction"]),
                "BestPhysicalResidual": float(best_row["PhysicalResidual"]),
                "BestPhysicalChi2Contribution": float(best_row["PhysicalChi2Contribution"]),
                "DeltaChi2_K2_minus_K1": float(k2_contrib[idx] - k1_contrib[idx]),
                "DeltaChi2_K2_minus_BestPhysical": float(
                    k2_contrib[idx] - float(best_row["PhysicalChi2Contribution"])
                ),
                "K2SignViolation": sign_violation_k2,
                "BestPhysicalSignViolation": sign_violation_best_physical,
                "RowClass": classify_row(
                    float(k2_contrib[idx]),
                    float(best_row["PhysicalChi2Contribution"]),
                    float(k1_contrib[idx]),
                ),
                "ClaimBoundary": "physical_null_row_audit_no_measurement_validation",
            }
        )

    audit = pd.DataFrame(audit_rows)
    audit["K2ContributionRank"] = audit["K2Chi2Contribution"].rank(ascending=False, method="first").astype(int)
    audit["BestPhysicalContributionRank"] = audit["BestPhysicalChi2Contribution"].rank(
        ascending=False, method="first"
    ).astype(int)
    audit.to_csv(OUT_AUDIT, index=False)

    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_PREFLIGHT_ROW_SUMMARY",
                "Rows": len(audit),
                "RowsWhereK2BeatsK1": int(np.sum(audit["K2Chi2Contribution"] < audit["K1Chi2Contribution"])),
                "RowsWhereK2BeatsBestPhysicalNull": int(
                    np.sum(audit["K2Chi2Contribution"] < audit["BestPhysicalChi2Contribution"])
                ),
                "RowsWhereBestPhysicalNullBeatsK2": int(
                    np.sum(audit["BestPhysicalChi2Contribution"] < audit["K2Chi2Contribution"])
                ),
                "RowsWhereK2HasSignViolation": int(audit["K2SignViolation"].sum()),
                "RowsWhereBestPhysicalHasSignViolation": int(audit["BestPhysicalSignViolation"].sum()),
                "TopK2ContributionGridIndex": int(audit.loc[audit["K2Chi2Contribution"].idxmax(), "GridIndex"]),
                "TopPhysicalContributionGridIndex": int(
                    audit.loc[audit["BestPhysicalChi2Contribution"].idxmax(), "GridIndex"]
                ),
                "NetDeltaChi2_K2_minus_K1": float(audit["DeltaChi2_K2_minus_K1"].sum()),
                "NetDeltaChi2_K2_minus_BestPhysical": float(audit["DeltaChi2_K2_minus_BestPhysical"].sum()),
                "Interpretation": (
                    "row audit supports the aggregate preflight reading if K2 beats K1 and best physical null "
                    "on most rows without sign-stable contradictions"
                ),
                "ClaimBoundary": "physical_null_row_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
