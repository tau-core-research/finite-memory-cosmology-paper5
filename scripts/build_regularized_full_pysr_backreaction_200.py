#!/usr/bin/env python3
"""Build and score a derivative-regularized D + normalized-PySR H smoke null."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fmc.backreaction import omega_r_plus_3omega_q

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

D_VECTOR = DATA / "d_branch_derivative_regularized_bootstrap_200_reconstruction_vector.csv"
D_SAMPLES = DATA / "d_branch_derivative_regularized_bootstrap_200_samples.csv"
H_VECTOR = DATA / "h_branch_normalized_criteria3_bootstrap_200_reconstruction_vector.csv"
H_SAMPLES = DATA / "h_branch_normalized_criteria3_bootstrap_200_samples.csv"

OUT_RECON = DATA / "regularized_full_pysr_backreaction_200_reconstruction_vector.csv"
OUT_OMEGA = DATA / "regularized_full_pysr_backreaction_200_omega_vector.csv"
OUT_OMEGA_SAMPLES = DATA / "regularized_full_pysr_backreaction_200_omega_samples.csv"
OUT_COV = DATA / "regularized_full_pysr_backreaction_200_omega_covariance.csv"
OUT_SCORE = EVIDENCE / "regularized_full_pysr_backreaction_200_bridge_scorecard.csv"
OUT_ROW = EVIDENCE / "regularized_full_pysr_backreaction_200_bridge_row_audit.csv"
OUT_SUMMARY = EVIDENCE / "regularized_full_pysr_backreaction_200_summary.csv"
OUT_DOC = DOCS / "regularized_full_pysr_backreaction_200.md"

CLAIM_BOUNDARY = "regularized_full_pysr_backreaction_200_no_measurement_validation"

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
    d = pd.read_csv(D_VECTOR).sort_values("z")
    h = pd.read_csv(H_VECTOR).sort_values("z")
    z = h["z"].to_numpy(float)
    D = np.interp(z, d["z"].to_numpy(float), d["D_median"].to_numpy(float))
    Dp = np.interp(z, d["z"].to_numpy(float), d["D_prime_median"].to_numpy(float))
    Dpp = np.interp(z, d["z"].to_numpy(float), d["D_double_prime_median"].to_numpy(float))
    H = h["H_D_proxy_median"].to_numpy(float)
    Hp = h["H_D_prime_proxy_median"].to_numpy(float)

    omega = omega_r_plus_3omega_q(z, D, Dp, Dpp, H, Hp)
    recon = pd.DataFrame(
        {
            "FamilyID": "REGULARIZED_FULL_NORMALIZED_PYSR_D_AND_H_BRANCHES",
            "SampleID": 0,
            "z": z,
            "D": D,
            "D_prime": Dp,
            "D_double_prime": Dpp,
            "H_D": H,
            "H_D_prime": Hp,
            "Source": "D_derivative_regularized_and_H_from_normalized_pysr_bootstrap_smoke",
            "SelectionRule": "regularized_full_normalized_pysr_smoke_no_K2_fit_no_K1_refit",
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    omega_df = pd.DataFrame(
        {
            "FamilyID": "REGULARIZED_FULL_NORMALIZED_PYSR_D_AND_H_BRANCHES",
            "SampleID": 0,
            "z": z,
            "Omega_R_plus_3Omega_Q": omega,
            "Source": "regularized_full_pysr_backreaction_smoke_reconstruction_vector",
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )

    d_samples = pd.read_csv(D_SAMPLES)
    h_samples = pd.read_csv(H_SAMPLES)
    sample_rows = []
    common_samples = sorted(set(d_samples["BootstrapIndex"]).intersection(set(h_samples["BootstrapIndex"])))
    for sample_id in common_samples:
        dg = d_samples[d_samples["BootstrapIndex"].eq(sample_id)].sort_values("z")
        hg = h_samples[h_samples["BootstrapIndex"].eq(sample_id)].sort_values("z")
        z_s = hg["z"].to_numpy(float)
        D_s = np.interp(z_s, dg["z"].to_numpy(float), dg["D"].to_numpy(float))
        Dp_s = np.interp(z_s, dg["z"].to_numpy(float), dg["D_prime"].to_numpy(float))
        Dpp_s = np.interp(z_s, dg["z"].to_numpy(float), dg["D_double_prime"].to_numpy(float))
        H_s = hg["H_D_proxy"].to_numpy(float)
        Hp_s = hg["H_D_prime_proxy"].to_numpy(float)
        omega_s = omega_r_plus_3omega_q(z_s, D_s, Dp_s, Dpp_s, H_s, Hp_s)
        for z_val, omega_val in zip(z_s, omega_s):
            sample_rows.append(
                {
                    "FamilyID": "REGULARIZED_FULL_NORMALIZED_PYSR_D_AND_H_BRANCHES",
                    "SampleID": int(sample_id),
                    "z": float(z_val),
                    "Omega_R_plus_3Omega_Q": float(omega_val),
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    return recon, omega_df, pd.DataFrame(sample_rows)


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
        omega_interp = np.interp(z, group["z"].to_numpy(float), group["Omega_R_plus_3Omega_Q"].to_numpy(float))
        pred = whitening @ omega_interp
        smoke_chi2 = chi2(target, pred)
        k1_chi2 = chi2(target, k1)
        k2_chi2 = chi2(target, k2)
        score_rows.append(
            {
                "AuditID": "REGULARIZED_FULL_PYSR_BACKREACTION_200_BRIDGE_V1",
                "RouteID": route["RouteID"],
                "FamilyID": "REGULARIZED_FULL_NORMALIZED_PYSR_D_AND_H_BRANCHES",
                "SampleID": 0,
                "Rows": len(target),
                "SmokeBackreactionChi2": smoke_chi2,
                "K1Chi2AgainstTarget": k1_chi2,
                "K2Chi2AgainstTarget": k2_chi2,
                "DeltaChi2_K2_minus_SmokeBackreaction": k2_chi2 - smoke_chi2,
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
                    "AuditID": "REGULARIZED_FULL_PYSR_BACKREACTION_200_ROW_V1",
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
    omega_abs_max = float(np.max(np.abs(omega_df["Omega_R_plus_3Omega_Q"].to_numpy(float))))
    summary = pd.DataFrame(
        [
            {
                "AuditID": "REGULARIZED_FULL_PYSR_BACKREACTION_200_V1",
                "RegularizedFull200NullBuilt": True,
                "OmegaRows": int(len(omega_df)),
                "OmegaSamples": int(omega_samples["SampleID"].nunique()),
                "FiniteOmega": omega_finite,
                "OmegaAbsMax": omega_abs_max,
                "SmokeCovarianceReady": cov_finite,
                "RoutesScored": int(score["RouteID"].nunique()),
                "K2BeatsSmokeBackreactionCases": k2_beats_smoke,
                "K2BeatsK1Cases": k2_beats_k1,
                "MedianCorrelationSmokeWithK2": float(score["CorrelationWithK2"].median()),
                "MedianCorrelationSmokeWithTarget": float(score["CorrelationWithTarget"].median()),
                "MedianDeltaChi2_K2_minus_SmokeBackreaction": float(score["DeltaChi2_K2_minus_SmokeBackreaction"].median()),
                "DBranchDerivativeRegularized": True,
                "HBranchNormalizedPySRSmoke": True,
                "FullBootstrapScale": True,
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "REGULARIZED_FULL_PYSR_BACKREACTION_200_SCORED",
                "StrongestAllowedClaim": (
                    "a derivative-regularized D + H 200-bootstrap backreaction null can be built and scored against locked K2"
                ),
                "PrimaryResidualRisk": (
                    "the 200-bootstrap branches are preflight proxy exports and source-native covariance is still missing"
                ),
                "NextAction": "diagnose 200-bootstrap low-depth Omega sensitivity without changing locked K2",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Regularized Full PySR Backreaction 200",
                "",
                "Status: REGULARIZED_FULL_PYSR_BACKREACTION_200_SCORED.",
                "",
                "This artifact combines the 200-bootstrap derivative-regularized D branch with the 200-bootstrap normalized-PySR H_D branch and evaluates the fixed backreaction formula. It is not a measurement-validating physical-null benchmark.",
                "",
                "## Result",
                "",
                f"- Omega rows: {len(omega_df)}",
                f"- Omega bootstrap samples: {omega_samples['SampleID'].nunique()}",
                f"- K2 beats smoke backreaction cases: {k2_beats_smoke}/{len(score)}",
                f"- Median correlation with K2: {float(score['CorrelationWithK2'].median())}",
                f"- Median DeltaChi2 K2-smoke: {float(score['DeltaChi2_K2_minus_SmokeBackreaction'].median())}",
                f"- Omega absolute max: {omega_abs_max}",
                "",
                "## Boundary",
                "",
                "No scale fit is allowed, K2 is unchanged, K1 is not refit, and measurement validation remains closed.",
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
