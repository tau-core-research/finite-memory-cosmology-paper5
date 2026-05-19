#!/usr/bin/env python3
"""Score registered-protocol-guided local reproduction families against locked K2."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OMEGA = DATA / "registered_protocol_guided_reproduction_backreaction_vector.csv"
OUT_ROW = EVIDENCE / "registered_protocol_guided_bridge_row_audit.csv"
OUT_SCORE = EVIDENCE / "registered_protocol_guided_bridge_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "registered_protocol_guided_bridge_summary.csv"
OUT_DOC = DOCS / "registered_protocol_guided_bridge_scorecard.md"

CLAIM_BOUNDARY = "registered_protocol_guided_bridge_no_measurement_validation"

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
    residual = np.asarray(y, dtype=float) - np.asarray(pred, dtype=float)
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

        for (family_id, sample_id), group in omega.groupby(["FamilyID", "SampleID"], sort=False):
            group = group.sort_values("z")
            omega_interp = np.interp(
                z,
                group["z"].to_numpy(float),
                group["Omega_R_plus_3Omega_Q"].to_numpy(float),
            )
            pred = whitening @ omega_interp
            family_chi2 = chi2(target, pred)
            k1_chi2 = chi2(target, k1)
            k2_chi2 = chi2(target, k2)
            score_rows.append(
                {
                    "AuditID": "REGISTERED_PROTOCOL_GUIDED_BRIDGE_SCORECARD_V1",
                    "RouteID": route["RouteID"],
                    "FamilyID": family_id,
                    "SampleID": sample_id,
                    "Rows": len(target),
                    "FamilyBackreactionChi2": family_chi2,
                    "K1Chi2AgainstTarget": k1_chi2,
                    "K2Chi2AgainstTarget": k2_chi2,
                    "DeltaChi2_K2_minus_FamilyBackreaction": k2_chi2 - family_chi2,
                    "DeltaChi2_K2_minus_K1": k2_chi2 - k1_chi2,
                    "CorrelationFamilyWithTarget": corr(target, pred),
                    "CorrelationFamilyWithK2": corr(k2, pred),
                    "StableSignMatchesTarget": sign_matches(pred, target, stable),
                    "StableSignMatchesK2": sign_matches(pred, k2, stable),
                    "StableRows": int(np.sum(stable)),
                    "LockedK2Changed": False,
                    "K1Refit": False,
                    "ScaleFitAllowed": False,
                    "SourceExport": False,
                    "SourceNative": False,
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
            for i, vector_row in vector.iterrows():
                row_rows.append(
                    {
                        "AuditID": "REGISTERED_PROTOCOL_GUIDED_BRIDGE_ROW_V1",
                        "RouteID": route["RouteID"],
                        "FamilyID": family_id,
                        "SampleID": sample_id,
                        "GridIndex": int(vector_row["GridIndex"]),
                        "z_grid": float(vector_row["z_grid"]),
                        "FamilyBackreactionInterpolated": float(omega_interp[i]),
                        "FamilyBackreactionWhitened": float(pred[i]),
                        "WhitenedTarget": float(target[i]),
                        "K1Whitened": float(k1[i]),
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

    k2_beats_family = int((score["DeltaChi2_K2_minus_FamilyBackreaction"] < 0.0).sum())
    best_family = score.groupby("FamilyID")["FamilyBackreactionChi2"].mean().sort_values().index[0]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "REGISTERED_PROTOCOL_GUIDED_BRIDGE_SCORECARD_V1",
                "RowsScored": len(row),
                "RoutesScored": score["RouteID"].nunique(),
                "FamiliesScored": score["FamilyID"].nunique(),
                "RouteFamilyCases": len(score),
                "K2BeatsFamilyBackreactionCases": k2_beats_family,
                "K2BeatsK1Cases": int((score["DeltaChi2_K2_minus_K1"] < 0.0).sum()),
                "BestFamilyByMeanChi2": best_family,
                "MedianCorrelationFamilyWithK2": float(score["CorrelationFamilyWithK2"].median()),
                "MedianCorrelationFamilyWithTarget": float(score["CorrelationFamilyWithTarget"].median()),
                "MedianDeltaChi2_K2_minus_FamilyBackreaction": float(
                    score["DeltaChi2_K2_minus_FamilyBackreaction"].median()
                ),
                "LockedK2Changed": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "SourceExport": False,
                "SourceNative": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "REGISTERED_PROTOCOL_GUIDED_BRIDGE_SCORED_SOURCE_NATIVE_BLOCKED",
                "StrongestAllowedClaim": (
                    "published protocol-guided local families can be scored against locked K2 as preflight comparators"
                ),
                "PrimaryResidualRisk": (
                    "manual protocol-selection details and branch-specific DESI/eBOSS exports remain unavailable"
                ),
                "NextAction": "run row/zone dominance and implement DESI/eBOSS branch-specific reproductions",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Registered-Protocol-Guided Bridge Scorecard",
                "",
                f"Status: {summary.iloc[0]['CurrentStatus']}.",
                "",
                "This scorecard compares publication-protocol-guided local reproduction families against locked K2. It does not use author exports, fit a scale, refit K1, or modify locked K2.",
                "",
                "## Key Numbers",
                "",
                f"- Families scored: {score['FamilyID'].nunique()}",
                f"- Routes scored: {score['RouteID'].nunique()}",
                f"- K2 beats family cases: {k2_beats_family}/{len(score)}",
                f"- Best family by mean chi2: `{best_family}`",
                f"- Median DeltaChi2 K2-family: {float(score['DeltaChi2_K2_minus_FamilyBackreaction'].median())}",
                "",
                "## Boundary",
                "",
                "This is a preflight artifact only. It is not source-native validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_SCORE.relative_to(ROOT)}")
    print(f"Wrote {OUT_ROW.relative_to(ROOT)}")
    print(f"Wrote {OUT_DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
