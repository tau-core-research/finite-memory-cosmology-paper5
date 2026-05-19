#!/usr/bin/env python3
"""Build and score a normalized-PySR backreaction smoke null.

The normalized criteria-set-3 bootstrap smoke provides a source-native-style
H_D branch. The D, D_prime, D_double_prime branch is still taken from the fixed
derivative pilot, so this is a hybrid smoke null, not a final source-native
backreaction vector.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fmc.backreaction import omega_r_plus_3omega_q

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

D_PILOT = DATA / "source_native_derivative_pilot_reconstruction_vector.csv"
H_VECTOR = DATA / "source_native_normalized_criteria3_bootstrap_smoke_reconstruction_vector.csv"
H_SAMPLES = DATA / "source_native_normalized_criteria3_bootstrap_smoke_samples.csv"

OUT_RECON = DATA / "normalized_pysr_backreaction_smoke_reconstruction_vector.csv"
OUT_OMEGA = DATA / "normalized_pysr_backreaction_smoke_omega_vector.csv"
OUT_OMEGA_SAMPLES = DATA / "normalized_pysr_backreaction_smoke_omega_samples.csv"
OUT_COV = DATA / "normalized_pysr_backreaction_smoke_omega_covariance.csv"
OUT_SCORE = EVIDENCE / "normalized_pysr_backreaction_smoke_bridge_scorecard.csv"
OUT_ROW = EVIDENCE / "normalized_pysr_backreaction_smoke_bridge_row_audit.csv"
OUT_SUMMARY = EVIDENCE / "normalized_pysr_backreaction_smoke_summary.csv"
OUT_DOC = DOCS / "normalized_pysr_backreaction_smoke_null.md"

CLAIM_BOUNDARY = "normalized_pysr_backreaction_smoke_null_no_measurement_validation"

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


def build_reconstruction() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    d = pd.read_csv(D_PILOT).sort_values("z")
    h = pd.read_csv(H_VECTOR).sort_values("z")
    h_samples = pd.read_csv(H_SAMPLES).sort_values(["BootstrapIndex", "z"])

    z = h["z"].to_numpy(float)
    d_z = d["z"].to_numpy(float)
    D = np.interp(z, d_z, d["D"].to_numpy(float))
    Dp = np.interp(z, d_z, d["D_prime"].to_numpy(float))
    Dpp = np.interp(z, d_z, d["D_double_prime"].to_numpy(float))
    H = h["H_D_proxy_median"].to_numpy(float)
    Hp = h["H_D_prime_proxy_median"].to_numpy(float)

    omega = omega_r_plus_3omega_q(z, D, Dp, Dpp, H, Hp)
    recon = pd.DataFrame(
        {
            "FamilyID": "NORMALIZED_PYSR_H_BRANCH_DERIVATIVE_PILOT_D_BRANCH",
            "SampleID": 0,
            "z": z,
            "D": D,
            "D_prime": Dp,
            "D_double_prime": Dpp,
            "H_D": H,
            "H_D_prime": Hp,
            "Source": "D_branch_from_derivative_pilot_H_branch_from_normalized_pysr_bootstrap_smoke",
            "SelectionRule": "hybrid_smoke_no_K2_fit_no_K1_refit",
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    omega_df = pd.DataFrame(
        {
            "FamilyID": "NORMALIZED_PYSR_H_BRANCH_DERIVATIVE_PILOT_D_BRANCH",
            "SampleID": 0,
            "z": z,
            "Omega_R_plus_3Omega_Q": omega,
            "Source": "normalized_pysr_backreaction_smoke_reconstruction_vector",
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )

    sample_rows = []
    for sample_id, group in h_samples.groupby("BootstrapIndex"):
        group = group.sort_values("z")
        z_s = group["z"].to_numpy(float)
        D_s = np.interp(z_s, d_z, d["D"].to_numpy(float))
        Dp_s = np.interp(z_s, d_z, d["D_prime"].to_numpy(float))
        Dpp_s = np.interp(z_s, d_z, d["D_double_prime"].to_numpy(float))
        H_s = group["H_D_proxy"].to_numpy(float)
        Hp_s = group["H_D_prime_proxy"].to_numpy(float)
        omega_s = omega_r_plus_3omega_q(z_s, D_s, Dp_s, Dpp_s, H_s, Hp_s)
        for z_val, omega_val in zip(z_s, omega_s):
            sample_rows.append(
                {
                    "FamilyID": "NORMALIZED_PYSR_H_BRANCH_DERIVATIVE_PILOT_D_BRANCH",
                    "SampleID": int(sample_id),
                    "z": float(z_val),
                    "Omega_R_plus_3Omega_Q": float(omega_val),
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    omega_samples = pd.DataFrame(sample_rows)
    return recon, omega_df, omega_samples


def covariance_from_samples(samples: pd.DataFrame) -> pd.DataFrame:
    pivot = samples.pivot_table(index="SampleID", columns="z", values="Omega_R_plus_3Omega_Q", aggfunc="first")
    cov = np.cov(pivot.to_numpy(float), rowvar=False)
    cov_df = pd.DataFrame(cov, columns=[f"z_{z:.6g}" for z in pivot.columns])
    cov_df.insert(0, "CovRow", [f"z_{z:.6g}" for z in pivot.columns])
    cov_df["ClaimBoundary"] = CLAIM_BOUNDARY
    return cov_df


def score_bridge(omega_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    row_rows = []
    score_rows = []
    group = omega_df.sort_values("z")
    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        grid_indices = vector["GridIndex"].astype(int).to_list()
        whitening = load_whitening(route, grid_indices)
        z = vector["z_grid"].to_numpy(float)
        target = vector["WhitenedTarget"].to_numpy(float)
        k1 = vector["K1Whitened"].to_numpy(float)
        k2 = vector["K2LockedWhitened"].to_numpy(float)
        stable = vector["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()
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
                "AuditID": "NORMALIZED_PYSR_BACKREACTION_SMOKE_BRIDGE_V1",
                "RouteID": route["RouteID"],
                "FamilyID": "NORMALIZED_PYSR_H_BRANCH_DERIVATIVE_PILOT_D_BRANCH",
                "SampleID": 0,
                "Rows": len(target),
                "SmokeBackreactionChi2": source_chi2,
                "K1Chi2AgainstTarget": k1_chi2,
                "K2Chi2AgainstTarget": k2_chi2,
                "DeltaChi2_K2_minus_SmokeBackreaction": k2_chi2 - source_chi2,
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
        for i, vector_row in vector.iterrows():
            row_rows.append(
                {
                    "AuditID": "NORMALIZED_PYSR_BACKREACTION_SMOKE_ROW_V1",
                    "RouteID": route["RouteID"],
                    "GridIndex": int(vector_row["GridIndex"]),
                    "z_grid": float(vector_row["z_grid"]),
                    "SmokeBackreactionInterpolated": float(omega_interp[i]),
                    "SmokeBackreactionWhitened": float(pred[i]),
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
    return pd.DataFrame(row_rows), pd.DataFrame(score_rows)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    recon, omega_df, omega_samples = build_reconstruction()
    cov_df = covariance_from_samples(omega_samples)
    row, score = score_bridge(omega_df)

    recon.to_csv(OUT_RECON, index=False)
    omega_df.to_csv(OUT_OMEGA, index=False)
    omega_samples.to_csv(OUT_OMEGA_SAMPLES, index=False)
    cov_df.to_csv(OUT_COV, index=False)
    row.to_csv(OUT_ROW, index=False)
    score.to_csv(OUT_SCORE, index=False)

    k2_beats_smoke = int((score["DeltaChi2_K2_minus_SmokeBackreaction"] < 0.0).sum())
    k2_beats_k1 = int((score["DeltaChi2_K2_minus_K1"] < 0.0).sum())
    omega_finite = bool(np.isfinite(omega_df["Omega_R_plus_3Omega_Q"].to_numpy(float)).all())
    cov_finite = bool(np.isfinite(cov_df.drop(columns=["CovRow", "ClaimBoundary"]).to_numpy(float)).all())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "NORMALIZED_PYSR_BACKREACTION_SMOKE_NULL_V1",
                "HybridSmokeNullBuilt": True,
                "OmegaRows": int(len(omega_df)),
                "OmegaSamples": int(omega_samples["SampleID"].nunique()),
                "FiniteOmega": omega_finite,
                "SmokeCovarianceReady": cov_finite,
                "RoutesScored": int(score["RouteID"].nunique()),
                "K2BeatsSmokeBackreactionCases": k2_beats_smoke,
                "K2BeatsK1Cases": k2_beats_k1,
                "MedianCorrelationSmokeWithK2": float(score["CorrelationWithK2"].median()),
                "MedianCorrelationSmokeWithTarget": float(score["CorrelationWithTarget"].median()),
                "MedianDeltaChi2_K2_minus_SmokeBackreaction": float(score["DeltaChi2_K2_minus_SmokeBackreaction"].median()),
                "DBranchSourceNative": False,
                "HBranchNormalizedPySRSmoke": True,
                "FullBootstrapScale": False,
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "HYBRID_NORMALIZED_PYSR_BACKREACTION_SMOKE_SCORED",
                "StrongestAllowedClaim": (
                    "a hybrid normalized-PySR H_D plus derivative-pilot D backreaction smoke null can be built and scored against locked K2"
                ),
                "PrimaryResidualRisk": (
                    "D branch is still derivative-pilot rather than source-native PySR, and the bootstrap is smoke-scale"
                ),
                "NextAction": (
                    "add source-native D-branch symbolic-regression bootstrap before treating this as a physical-null benchmark"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Normalized PySR Backreaction Smoke Null",
                "",
                "Status: HYBRID_NORMALIZED_PYSR_BACKREACTION_SMOKE_SCORED.",
                "",
                "This artifact combines the normalized-PySR H_D bootstrap-smoke branch with the existing derivative-pilot D branch and evaluates the fixed backreaction formula. It is a hybrid smoke null, not a final source-native physical-null benchmark.",
                "",
                "## Result",
                "",
                f"- Omega rows: {len(omega_df)}",
                f"- Omega bootstrap samples: {omega_samples['SampleID'].nunique()}",
                f"- K2 beats smoke backreaction cases: {k2_beats_smoke}/{len(score)}",
                f"- Median correlation with K2: {float(score['CorrelationWithK2'].median())}",
                f"- Median DeltaChi2 K2-smoke: {float(score['DeltaChi2_K2_minus_SmokeBackreaction'].median())}",
                "",
                "## Boundary",
                "",
                "The D branch is not yet source-native PySR, no scale fit is allowed, K2 is unchanged, and measurement validation remains closed.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_RECON.relative_to(ROOT)}")
    print(f"Wrote {OUT_OMEGA.relative_to(ROOT)}")
    print(f"Wrote {OUT_SCORE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
