#!/usr/bin/env python3
"""Score source-native backreaction exports against locked K2 when available.

If source-native exports are missing, this script still writes a blocked
readiness artifact. It never changes locked K2, fits a new K1, or authorizes
measurement validation.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_native_backreaction import load_csv_if_exists

EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"

OMEGA = DATA / "source_native_backreaction_vector.csv"

ROUTES = [
    {
        "RouteID": "PUBLIC_PROXY_WHITENED_STANDARDIZED",
        "Vector": EVIDENCE / "whitened_standardized_branch_contrast_vector.csv",
        "Whitening": EVIDENCE / "whitened_standardized_branch_contrast_matrix.csv",
        "Covariance": None,
    },
    {
        "RouteID": "REGISTERED_SHRINKAGE_WHITENED",
        "Vector": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_vector.csv",
        "Whitening": None,
        "Covariance": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_covariance.csv",
    },
]

OUT_ROW = EVIDENCE / "source_native_backreaction_bridge_row_audit.csv"
OUT_SCORE = EVIDENCE / "source_native_backreaction_bridge_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "source_native_backreaction_bridge_summary.csv"
OUT_DOC = DOCS / "source_native_backreaction_bridge_scorecard.md"


def load_whitening(route: dict[str, object], grid_indices: list[int]) -> np.ndarray:
    if route["Whitening"] is not None:
        matrix = pd.read_csv(Path(str(route["Whitening"])))
        return matrix[[str(idx) for idx in grid_indices]].to_numpy(float)
    cov_df = pd.read_csv(Path(str(route["Covariance"])))
    cov = cov_df[[str(idx) for idx in grid_indices]].to_numpy(float)
    eigvals, eigvecs = np.linalg.eigh(0.5 * (cov + cov.T))
    if np.any(eigvals <= 0.0):
        raise ValueError(f"non-positive covariance eigenvalue for {route['RouteID']}")
    return eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T


def chi2(y: np.ndarray, pred: np.ndarray) -> float:
    residual = y - pred
    return float(residual @ residual)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) == 0.0 or np.std(b) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def sign_matches(a: np.ndarray, b: np.ndarray, stable: np.ndarray) -> int:
    mask = np.asarray(stable, dtype=bool)
    return int(np.sum(np.sign(a[mask]) == np.sign(b[mask])))


def write_blocked(reason: str) -> None:
    pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_BRIDGE_SCORECARD_V1",
                "SourceNativeVectorAvailable": False,
                "RowsScored": 0,
                "RoutesScored": 0,
                "FamiliesScored": 0,
                "SourceNativeBridgeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_BRIDGE_SCORE_BLOCKED",
                "StrongestAllowedClaim": "source-native bridge scorecard gate is ready, but source-native backreaction vector is missing",
                "PrimaryResidualRisk": reason,
                "NextAction": "provide and validate source_native_reconstruction_vector.csv and source_native_selection_metadata.csv",
                "ClaimBoundary": "source_native_backreaction_bridge_scorecard_no_measurement_validation",
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    pd.DataFrame(columns=["AuditID", "RouteID", "FamilyID", "SampleID"]).to_csv(OUT_ROW, index=False)
    pd.DataFrame(columns=["AuditID", "RouteID", "FamilyID", "SampleID"]).to_csv(OUT_SCORE, index=False)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    omega = load_csv_if_exists(OMEGA)
    if omega is None or omega.empty:
        write_blocked("source_native_backreaction_vector_missing_or_empty")
    else:
        row_rows = []
        score_rows = []
        for route in ROUTES:
            vector = pd.read_csv(Path(str(route["Vector"])))
            grid_indices = vector["GridIndex"].astype(int).to_list()
            whitening = load_whitening(route, grid_indices)
            z = vector["z_grid"].to_numpy(float)
            target = vector["WhitenedTarget"].to_numpy(float)
            k1 = vector["K1Whitened"].to_numpy(float)
            k2 = vector["K2LockedWhitened"].to_numpy(float)
            stable = vector["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

            for (family_id, sample_id), group in omega.groupby(["FamilyID", "SampleID"]):
                group = group.sort_values("z")
                omega_interp = np.interp(
                    z,
                    group["z"].to_numpy(float),
                    group["Omega_R_plus_3Omega_Q"].to_numpy(float),
                )
                pred = whitening @ omega_interp
                score_rows.append(
                    {
                        "AuditID": "SOURCE_NATIVE_BACKREACTION_BRIDGE_SCORECARD_V1",
                        "RouteID": route["RouteID"],
                        "FamilyID": family_id,
                        "SampleID": sample_id,
                        "Rows": len(target),
                        "Chi2AgainstTarget": chi2(target, pred),
                        "K1Chi2AgainstTarget": chi2(target, k1),
                        "K2Chi2AgainstTarget": chi2(target, k2),
                        "DeltaChi2_K2_minus_SourceNativeBackreaction": chi2(target, k2) - chi2(target, pred),
                        "CorrelationWithTarget": corr(target, pred),
                        "CorrelationWithK2": corr(k2, pred),
                        "StableSignMatchesTarget": sign_matches(pred, target, stable),
                        "StableRows": int(np.sum(stable)),
                        "LockedK2Changed": False,
                        "ScaleFitAllowed": False,
                        "MeasurementValidationAllowed": False,
                        "ClaimBoundary": "source_native_backreaction_bridge_scorecard_no_measurement_validation",
                    }
                )
                for i, row in vector.iterrows():
                    row_rows.append(
                        {
                            "AuditID": "SOURCE_NATIVE_BACKREACTION_BRIDGE_ROW_AUDIT_V1",
                            "RouteID": route["RouteID"],
                            "FamilyID": family_id,
                            "SampleID": sample_id,
                            "GridIndex": int(row["GridIndex"]),
                            "z_grid": float(row["z_grid"]),
                            "BackreactionInterpolated": float(omega_interp[i]),
                            "BackreactionWhitened": float(pred[i]),
                            "WhitenedTarget": float(target[i]),
                            "K2LockedWhitened": float(k2[i]),
                            "ResidualToTarget": float(target[i] - pred[i]),
                            "ResidualToK2": float(k2[i] - pred[i]),
                            "SignStable": bool(stable[i]),
                            "SignMatchesTarget": bool(np.sign(pred[i]) == np.sign(target[i])),
                            "SignMatchesK2": bool(np.sign(pred[i]) == np.sign(k2[i])),
                            "MeasurementValidationAllowed": False,
                            "ClaimBoundary": "source_native_backreaction_bridge_scorecard_no_measurement_validation",
                        }
                    )

        score = pd.DataFrame(score_rows)
        row = pd.DataFrame(row_rows)
        score.to_csv(OUT_SCORE, index=False)
        row.to_csv(OUT_ROW, index=False)
        summary = pd.DataFrame(
            [
                {
                    "AuditID": "SOURCE_NATIVE_BACKREACTION_BRIDGE_SCORECARD_V1",
                    "SourceNativeVectorAvailable": True,
                    "RowsScored": len(row),
                    "RoutesScored": score["RouteID"].nunique(),
                    "FamiliesScored": score["FamilyID"].nunique(),
                    "SourceNativeBridgeScoringReady": True,
                    "MeasurementValidationAllowed": False,
                    "CurrentStatus": "SOURCE_NATIVE_BRIDGE_SCORECARD_PREFLIGHT_READY",
                    "StrongestAllowedClaim": "source-native backreaction bridge can be scored as a preflight physical-null comparator",
                    "PrimaryResidualRisk": "source-native covariance/bootstrap must still be attached for measurement-grade scoring",
                    "NextAction": "attach source-native covariance/bootstrap and run covariance-aware physical-null benchmark",
                    "ClaimBoundary": "source_native_backreaction_bridge_scorecard_no_measurement_validation",
                }
            ]
        )
        summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Backreaction Bridge Scorecard",
                "",
                "Status: scoring gate ready; blocked until source-native vector is available.",
                "",
                "This script compares a future source-native `Omega_R + 3 Omega_Q` vector against the locked K2 routes. It does not fit a scale, refit K1, or alter locked K2.",
                "",
                "## Outputs",
                "",
                f"- Row audit: `{OUT_ROW.relative_to(ROOT)}`",
                f"- Scorecard: `{OUT_SCORE.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_SCORE}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
