#!/usr/bin/env python3
"""Run covariance-sensitivity checks on standardized source-split residuals.

This is not K2 scoring. It asks whether the SN/BAO branch contrast is robust
under simple within-row SN-BAO correlation assumptions.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
SRC = EVIDENCE / "source_split_standardized_preflight.csv"
OUT = EVIDENCE / "source_split_covariance_sensitivity.csv"
SUMMARY = EVIDENCE / "source_split_covariance_sensitivity_summary.csv"


RHO_VALUES = [-0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75]


def contrast_chi2(sn_z: float, bao_z: float, rho: float) -> float:
    """Return [sn, bao]^T C^-1 [sn, bao] for unit variances and correlation rho."""
    cov = np.array([[1.0, rho], [rho, 1.0]], dtype=float)
    vec = np.array([sn_z, bao_z], dtype=float)
    return float(vec.T @ np.linalg.solve(cov, vec))


def contrast_sigma(rho: float) -> float:
    """Sigma of SN-BAO contrast when both standardized branches have unit variance."""
    return float(np.sqrt(max(2.0 - 2.0 * rho, 0.0)))


def main() -> None:
    df = pd.read_csv(SRC)
    complete = df[df["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    complete = complete[
        complete["SNStandardizedResidual"].notna() & complete["BAOStandardizedResidual"].notna()
    ].copy()

    rows = []
    for rho in RHO_VALUES:
        sigma_delta = contrast_sigma(rho)
        for _, row in complete.iterrows():
            sn = float(row["SNStandardizedResidual"])
            bao = float(row["BAOStandardizedResidual"])
            delta = sn - bao
            delta_score = abs(delta) / sigma_delta if sigma_delta > 0.0 else np.inf
            rows.append(
                {
                    "CovarianceModel": "WITHIN_ROW_SN_BAO_CORR",
                    "RhoSNBAO": rho,
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "SignStable": bool(row["SignStable"]),
                    "SNStandardizedResidual": sn,
                    "BAOStandardizedResidual": bao,
                    "SNMinusBAO": delta,
                    "ContrastSigma": sigma_delta,
                    "AbsContrastOverSigma": delta_score,
                    "JointChi2Proxy": contrast_chi2(sn, bao, rho),
                    "OppositeSign": bool(not row["SNBAOSameSign"]),
                    "ReadyForK2Scoring": False,
                    "ClaimBoundary": "preflight_only_no_measurement_validation",
                }
            )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    summary_rows = []
    for rho, group in output.groupby("RhoSNBAO", sort=True):
        stable = group[group["SignStable"]]
        summary_rows.append(
            {
                "CovarianceModel": "WITHIN_ROW_SN_BAO_CORR",
                "RhoSNBAO": rho,
                "Rows": len(group),
                "OppositeSignRows": int(group["OppositeSign"].sum()),
                "MeanAbsContrastOverSigma": float(group["AbsContrastOverSigma"].mean()),
                "MaxAbsContrastOverSigma": float(group["AbsContrastOverSigma"].max()),
                "MeanJointChi2Proxy": float(group["JointChi2Proxy"].mean()),
                "SignStableRows": len(stable),
                "SignStableOppositeSignRows": int(stable["OppositeSign"].sum()),
                "SignStableMeanAbsContrastOverSigma": float(stable["AbsContrastOverSigma"].mean())
                if not stable.empty
                else np.nan,
                "Status": "PREFLIGHT_COVARIANCE_SENSITIVITY_NOT_MEASUREMENT_GATE",
                "BlockingIssue": "proxy_correlation_only;coordinate_native_k1_missing;joint_covariance_missing",
                "NextAction": "Replace within-row proxy with public joint covariance before K2 scoring.",
            }
        )
    pd.DataFrame(summary_rows).to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
