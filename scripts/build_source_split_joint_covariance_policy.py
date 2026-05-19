#!/usr/bin/env python3
"""Build a declared source-split shrinkage covariance policy artifact.

This fulfills TQ3 as a covariance-policy preflight. The artifact is coordinate
native and K1-compatible, but it is not a public full covariance and does not
authorize K2 scoring while the public sign-family export is missing.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
TARGET = EVIDENCE / "source_split_k1_coordinate_native_target.csv"
OUT = EVIDENCE / "source_split_joint_covariance_policy.csv"
SUMMARY = EVIDENCE / "source_split_joint_covariance_policy_summary.csv"

COVARIANCE_ID = "SSCOV_SHRINKAGE_SOURCE_SPLIT"
RHO_SN_BAO = 0.0
LAMBDA_SHRINK = 0.15
CORRELATION_LENGTH = 0.25


def main() -> None:
    df = pd.read_csv(TARGET)
    usable = df[df["HasTargetRow"].astype(str).str.lower().eq("true")].reset_index(drop=True)
    x = usable["x_coordinate"].to_numpy(float)
    n = len(usable)
    contrast_sigma = np.sqrt(2.0 * (1.0 - RHO_SN_BAO))

    rows = []
    for i in range(n):
        for j in range(n):
            distance = abs(float(x[i]) - float(x[j]))
            kernel = np.exp(-distance / CORRELATION_LENGTH)
            if i == j:
                corr = 1.0
            else:
                corr = LAMBDA_SHRINK * kernel
            covariance = (contrast_sigma**2) * corr
            rows.append(
                {
                    "CovarianceID": COVARIANCE_ID,
                    "RowI": int(i),
                    "RowJ": int(j),
                    "GridIndexI": int(usable.loc[i, "GridIndex"]),
                    "GridIndexJ": int(usable.loc[j, "GridIndex"]),
                    "z_i": float(usable.loc[i, "z_grid"]),
                    "z_j": float(usable.loc[j, "z_grid"]),
                    "x_i": float(x[i]),
                    "x_j": float(x[j]),
                    "RhoSNBAO": RHO_SN_BAO,
                    "LambdaShrink": LAMBDA_SHRINK,
                    "CorrelationLength": CORRELATION_LENGTH,
                    "Covariance": float(covariance),
                    "Correlation": float(corr),
                    "CoordinateNative": True,
                    "K1Compatible": True,
                    "AllowedForK2Scoring": False,
                    "ClaimBoundary": "shrinkage_policy_preflight_no_measurement_validation",
                }
            )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    matrix = output.pivot(index="RowI", columns="RowJ", values="Covariance").to_numpy(float)
    eigenvalues = np.linalg.eigvalsh(matrix)
    summary = pd.DataFrame(
        [
            {
                "CovarianceID": COVARIANCE_ID,
                "Rows": n,
                "MatrixEntries": len(output),
                "RhoSNBAO": RHO_SN_BAO,
                "LambdaShrink": LAMBDA_SHRINK,
                "CorrelationLength": CORRELATION_LENGTH,
                "MinEigenvalue": float(np.min(eigenvalues)) if len(eigenvalues) else np.nan,
                "MaxEigenvalue": float(np.max(eigenvalues)) if len(eigenvalues) else np.nan,
                "PositiveDefinite": bool(np.min(eigenvalues) > 0.0) if len(eigenvalues) else False,
                "CoordinateNative": True,
                "K1Compatible": True,
                "AllowedForK2Scoring": False,
                "Status": "SHRINKAGE_COVARIANCE_POLICY_EXPORTED_NOT_PUBLIC_FULL_COVARIANCE",
                "BlockingIssue": "public_sign_family_missing;not_public_full_covariance",
                "NextAction": "Export public sign-family before any K2/null scorecard; replace with public full covariance when available.",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
