#!/usr/bin/env python3
"""Build covariance-preview artifacts for alpha-derived physical-null controls.

This script does not create a measurement covariance. It exposes two
predeclared preview families from the source alpha uncertainty:

- diagonal amplitude propagation;
- exponential correlation in source-split x with fixed length.

Both remain non-scoring until a source-native covariance route or explicitly
registered measurement covariance policy is available.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

PREVIEW = EVIDENCE / "physical_null_alpha_response_preview.csv"

POLICY_OUT = EVIDENCE / "physical_null_alpha_covariance_preview_policy.csv"
MATRIX_OUT = EVIDENCE / "physical_null_alpha_covariance_preview_matrix.csv"
SUMMARY_OUT = EVIDENCE / "physical_null_alpha_covariance_preview_summary.csv"

CORRELATION_LENGTH_X = 0.35


def exp_corr(x_i: float, x_j: float, length: float = CORRELATION_LENGTH_X) -> float:
    return math.exp(-abs(x_i - x_j) / length)


def main() -> None:
    preview = pd.read_csv(PREVIEW)
    policy = pd.DataFrame(
        [
            {
                "PolicyID": "ALPHA_COV_DIAGONAL_PREVIEW_V1",
                "PolicyRole": "preflight_sensitivity_only",
                "CovarianceFormula": "C_ij = sigma_i^2 if i=j else 0",
                "SourceUncertainty": "alpha asymmetric errors compressed to mean half-width",
                "CrossRowCorrelationRule": "none",
                "CanSupportMeasurementScoring": False,
                "RequiredBeforeScoring": "source-native covariance or registered covariance propagation",
                "ClaimBoundary": "alpha_covariance_preview_no_measurement_validation",
            },
            {
                "PolicyID": "ALPHA_COV_EXP_X_PREVIEW_V1",
                "PolicyRole": "preflight_sensitivity_only",
                "CovarianceFormula": "C_ij = sigma_i*sigma_j*exp(-abs(x_i-x_j)/0.35)",
                "SourceUncertainty": "alpha asymmetric errors compressed to mean half-width",
                "CrossRowCorrelationRule": "fixed exponential in source-split x; not tuned by score",
                "CanSupportMeasurementScoring": False,
                "RequiredBeforeScoring": "source-native covariance or registered covariance propagation",
                "ClaimBoundary": "alpha_covariance_preview_no_measurement_validation",
            },
        ]
    )
    policy.to_csv(POLICY_OUT, index=False)

    rows: list[dict[str, object]] = []
    for extraction_id, group in preview.groupby("ExtractionID"):
        group = group.sort_values("GridIndex").reset_index(drop=True)
        for _, left in group.iterrows():
            for _, right in group.iterrows():
                sigma_i = float(left["ResponseSigmaDiagPreview"])
                sigma_j = float(right["ResponseSigmaDiagPreview"])
                x_i = float(left["x_coordinate"])
                x_j = float(right["x_coordinate"])
                for policy_id in ["ALPHA_COV_DIAGONAL_PREVIEW_V1", "ALPHA_COV_EXP_X_PREVIEW_V1"]:
                    if policy_id == "ALPHA_COV_DIAGONAL_PREVIEW_V1":
                        corr = 1.0 if int(left["GridIndex"]) == int(right["GridIndex"]) else 0.0
                    else:
                        corr = exp_corr(x_i, x_j)
                    rows.append(
                        {
                            "CovariancePreviewID": policy_id,
                            "ExtractionID": extraction_id,
                            "GridIndexI": int(left["GridIndex"]),
                            "GridIndexJ": int(right["GridIndex"]),
                            "z_i": float(left["z_grid"]),
                            "z_j": float(right["z_grid"]),
                            "x_i": x_i,
                            "x_j": x_j,
                            "SigmaI": sigma_i,
                            "SigmaJ": sigma_j,
                            "Correlation": corr,
                            "CovarianceValue": sigma_i * sigma_j * corr,
                            "ScoringAllowed": False,
                            "CovarianceStatus": "preview_only",
                            "BlockingIssue": "source_native_covariance_missing;measurement_scorecard_not_authorized",
                            "ClaimBoundary": "alpha_covariance_preview_no_measurement_validation",
                        }
                    )

    matrix = pd.DataFrame(rows)
    matrix.to_csv(MATRIX_OUT, index=False)

    summary_rows: list[dict[str, object]] = []
    for (policy_id, extraction_id), group in matrix.groupby(["CovariancePreviewID", "ExtractionID"]):
        diag = group[group["GridIndexI"].eq(group["GridIndexJ"])]
        off = group[~group["GridIndexI"].eq(group["GridIndexJ"])]
        summary_rows.append(
            {
                "SummaryID": "PHYSICAL_NULL_ALPHA_COVARIANCE_PREVIEW_SUMMARY",
                "CovariancePreviewID": policy_id,
                "ExtractionID": extraction_id,
                "MatrixEntries": len(group),
                "DiagonalEntries": len(diag),
                "OffDiagonalEntries": len(off),
                "MaxDiagonalVariance": float(diag["CovarianceValue"].max()) if len(diag) else 0.0,
                "MaxAbsOffDiagonalCovariance": float(off["CovarianceValue"].abs().max()) if len(off) else 0.0,
                "ScoringAllowed": False,
                "PrimaryBlockingIssue": "source_native_covariance_missing;measurement_scorecard_not_authorized",
                "Interpretation": "alpha covariance preview exists, but is not measurement covariance",
                "ClaimBoundary": "alpha_covariance_preview_no_measurement_validation",
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY_OUT, index=False)
    print(f"Wrote {POLICY_OUT}")
    print(f"Wrote {MATRIX_OUT}")
    print(f"Wrote {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
