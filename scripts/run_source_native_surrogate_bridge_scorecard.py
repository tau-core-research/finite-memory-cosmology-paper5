#!/usr/bin/env python3
"""Score surrogate backreaction-family exports against locked K2.

This uses the same route structure as the future source-native scorecard, but
reads the explicitly marked surrogate family vectors. It is a pipeline rehearsal
only and does not authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"

OMEGA = DATA / "source_native_surrogate_backreaction_vector.csv"

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

OUT_ROW = EVIDENCE / "source_native_surrogate_bridge_row_audit.csv"
OUT_SCORE = EVIDENCE / "source_native_surrogate_bridge_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "source_native_surrogate_bridge_summary.csv"
OUT_DOC = DOCS / "source_native_surrogate_bridge_scorecard.md"

CLAIM_BOUNDARY = "source_native_surrogate_bridge_scorecard_no_measurement_validation"


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


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    omega = pd.read_csv(OMEGA)
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
            source_chi2 = chi2(target, pred)
            k1_chi2 = chi2(target, k1)
            k2_chi2 = chi2(target, k2)
            score_rows.append(
                {
                    "AuditID": "SOURCE_NATIVE_SURROGATE_BRIDGE_SCORECARD_V1",
                    "RouteID": route["RouteID"],
                    "FamilyID": family_id,
                    "SampleID": sample_id,
                    "Rows": len(target),
                    "SurrogateBackreactionChi2": source_chi2,
                    "K1Chi2AgainstTarget": k1_chi2,
                    "K2Chi2AgainstTarget": k2_chi2,
                    "DeltaChi2_K2_minus_SurrogateBackreaction": k2_chi2 - source_chi2,
                    "DeltaChi2_K2_minus_K1": k2_chi2 - k1_chi2,
                    "CorrelationWithTarget": corr(target, pred),
                    "CorrelationWithK2": corr(k2, pred),
                    "StableSignMatchesTarget": sign_matches(pred, target, stable),
                    "StableSignMatchesK2": sign_matches(pred, k2, stable),
                    "StableRows": int(np.sum(stable)),
                    "LockedK2Changed": False,
                    "ScaleFitAllowed": False,
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
            for i, row in vector.iterrows():
                row_rows.append(
                    {
                        "AuditID": "SOURCE_NATIVE_SURROGATE_BRIDGE_ROW_AUDIT_V1",
                        "RouteID": route["RouteID"],
                        "FamilyID": family_id,
                        "SampleID": sample_id,
                        "GridIndex": int(row["GridIndex"]),
                        "z_grid": float(row["z_grid"]),
                        "SurrogateBackreactionInterpolated": float(omega_interp[i]),
                        "SurrogateBackreactionWhitened": float(pred[i]),
                        "WhitenedTarget": float(target[i]),
                        "K2LockedWhitened": float(k2[i]),
                        "ResidualToTarget": float(target[i] - pred[i]),
                        "ResidualToK2": float(k2[i] - pred[i]),
                        "SignStable": bool(stable[i]),
                        "SignMatchesTarget": bool(np.sign(pred[i]) == np.sign(target[i])),
                        "SignMatchesK2": bool(np.sign(pred[i]) == np.sign(k2[i])),
                        "MeasurementValidationAllowed": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )

    score = pd.DataFrame(score_rows)
    row = pd.DataFrame(row_rows)
    score.to_csv(OUT_SCORE, index=False)
    row.to_csv(OUT_ROW, index=False)

    k2_beats_surrogate = int((score["DeltaChi2_K2_minus_SurrogateBackreaction"] < 0.0).sum())
    k2_beats_k1 = int((score["DeltaChi2_K2_minus_K1"] < 0.0).sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_SURROGATE_BRIDGE_SCORECARD_V1",
                "SurrogateVectorAvailable": True,
                "RowsScored": len(row),
                "RoutesScored": score["RouteID"].nunique(),
                "FamiliesScored": score["FamilyID"].nunique(),
                "RouteFamilyCases": len(score),
                "K2BeatsSurrogateBackreactionCases": k2_beats_surrogate,
                "K2BeatsK1Cases": k2_beats_k1,
                "MedianCorrelationSurrogateWithK2": float(score["CorrelationWithK2"].median()),
                "MinCorrelationSurrogateWithK2": float(score["CorrelationWithK2"].min()),
                "MaxCorrelationSurrogateWithK2": float(score["CorrelationWithK2"].max()),
                "SurrogateBridgeScoringReady": True,
                "SourceNativeBridgeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SURROGATE_BRIDGE_SCORED_SOURCE_NATIVE_STILL_MISSING",
                "StrongestAllowedClaim": (
                    "the future source-native bridge scorecard can execute on a surrogate multi-family export"
                ),
                "PrimaryResidualRisk": (
                    "surrogate polynomial families are not source-native symbolic-regression families and cannot settle the physical-null question"
                ),
                "NextAction": "replace surrogate vectors with source-native family exports and covariance without changing locked K2",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Surrogate Bridge Scorecard",
                "",
                "Status: surrogate bridge scored; source-native bridge still missing.",
                "",
                "This scorecard exercises the final bridge mechanics on explicitly marked surrogate family vectors. It is not a measurement-grade physical-null comparison.",
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
