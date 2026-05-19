#!/usr/bin/env python3
"""Diagnose whether the likelihood-native amplitude gap is recoverable with rho<=4."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked, w_power

EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
REQ_OUT = ROOT / "evidence" / "source_split_likelihood_native_rho_requirement_audit.csv"
SCAN_OUT = ROOT / "evidence" / "source_split_likelihood_native_bounded_rho_scan.csv"
SUMMARY_OUT = ROOT / "evidence" / "source_split_likelihood_native_rho_requirement_summary.csv"


def main() -> None:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    data = external.merge(
        target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    sigma = data["K1Sigma"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    x3 = x**3
    same_sign = np.sign(y) == np.sign(k1)
    with np.errstate(divide="ignore", invalid="ignore"):
        rho_required = ((y / k1) - 1.0) / x3
    finite_required = np.isfinite(rho_required)
    within_bound = finite_required & same_sign & (rho_required >= 0.0) & (rho_required <= 4.0)

    req = pd.DataFrame(
        {
            "GridIndex": data["GridIndex"].astype(int),
            "z_grid": data["z_grid"].astype(float),
            "x_coordinate": x,
            "TargetResponse": y,
            "K1Response": k1,
            "K2Rho4Response": w_k2_locked(x, rho=4.0) * k1,
            "SigmaDiag": sigma,
            "SameSignTargetK1": same_sign,
            "RhoRequiredForExactMatch": rho_required,
            "RhoRequiredFinite": finite_required,
            "RhoWithinPassiveBound": within_bound,
            "RhoExceedsBound": finite_required & same_sign & (rho_required > 4.0),
            "RhoNegativeOrSignConflict": finite_required & (~same_sign | (rho_required < 0.0)),
            "ClaimBoundary": "rho_requirement_diagnosis_only_no_rho_rescue",
        }
    )
    req.to_csv(REQ_OUT, index=False)

    rows = []
    cov = np.diag(sigma * sigma)
    for rho in np.linspace(0.0, 4.0, 81):
        pred = w_power(x, rho=float(rho), p=3) * k1
        c2 = chi2(y, pred, cov)
        sign_viol = int(np.sum(np.sign(pred[stable]) != np.sign(y[stable])))
        rows.append(
            {
                "Rho": float(rho),
                "P": 3,
                "WithinPassiveBound": True,
                "Chi2DiagProxy": c2,
                "AIC": aic(c2, 0),
                "BIC": bic(c2, 0, len(y)),
                "SignStableViolations": sign_viol,
                "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                "ClaimBoundary": "bounded_rho_scan_only_no_posthoc_rescue",
            }
        )
    scan = pd.DataFrame(rows)
    scan.to_csv(SCAN_OUT, index=False)

    best = scan.loc[scan["Chi2DiagProxy"].idxmin()]
    rho4 = scan[np.isclose(scan["Rho"], 4.0)].iloc[0]
    k1_chi2 = chi2(y, k1, cov)
    summary = pd.DataFrame(
        [
            {
                "ArtifactID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_RHO_REQUIREMENT",
                "Rows": len(req),
                "RowsExactMatchWithinRhoBound": int(req["RhoWithinPassiveBound"].sum()),
                "RowsRhoExceedsBound": int(req["RhoExceedsBound"].sum()),
                "RowsRhoNegativeOrSignConflict": int(req["RhoNegativeOrSignConflict"].sum()),
                "BestBoundedRho": float(best["Rho"]),
                "BestBoundedRhoChi2": float(best["Chi2DiagProxy"]),
                "Rho4Chi2": float(rho4["Chi2DiagProxy"]),
                "K1NoMemoryChi2": float(k1_chi2),
                "BestBoundedRhoImprovesOverK1": bool(float(best["Chi2DiagProxy"]) < k1_chi2),
                "BestBoundedRhoEqualsUpperBound": bool(np.isclose(float(best["Rho"]), 4.0)),
                "Interpretation": "bounded_rho_prefers_upper_bound_but_cannot_close_amplitude_gap",
                "NextAction": "Do not use rho>4; investigate target scale, covariance, or independently declared amplitude normalization.",
                "ClaimBoundary": "rho_requirement_diagnosis_only_no_rho_rescue",
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    print(f"Wrote {REQ_OUT}")
    print(f"Wrote {SCAN_OUT}")
    print(f"Wrote {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
