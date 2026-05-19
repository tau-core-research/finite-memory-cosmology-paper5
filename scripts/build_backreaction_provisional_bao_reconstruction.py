#!/usr/bin/env python3
"""Build a provisional BAO-only backreaction reconstruction.

This is a fallback/preflight reconstruction from public DESI DR2 BAO mean and
covariance files. It is intentionally labeled provisional because it does not
reproduce the authors' full Pantheon+ plus BAO symbolic-regression bootstrap
pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.backreaction import omega_r_plus_3omega_q  # noqa: E402

DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

DESI_DR2_MEAN = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR2_COV = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

OUT_VECTOR = DATA / "provisional_bao_backreaction_reconstruction_vector.csv"
OUT_INPUT_COV = DATA / "provisional_bao_backreaction_reconstruction_covariance.csv"
OUT_OMEGA = DATA / "provisional_bao_backreaction_omega_curve.csv"
OUT_OMEGA_COV = DATA / "provisional_bao_backreaction_omega_covariance.csv"
OUT_BOOTSTRAP = DATA / "provisional_bao_backreaction_bootstrap_samples.csv"
OUT_SUMMARY = EVIDENCE / "backreaction_provisional_bao_reconstruction_summary.csv"
OUT_DOC = DOCS / "backreaction_provisional_bao_reconstruction.md"

RNG_SEED = 260411249
BOOTSTRAP_DRAWS = 3000
D_POLY_DEGREE = 3
H_POLY_DEGREE = 2


def load_desi_dr2() -> tuple[pd.DataFrame, np.ndarray]:
    mean = pd.read_csv(
        DESI_DR2_MEAN,
        sep=r"\s+",
        comment="#",
        names=["z", "value", "quantity"],
        engine="python",
    )
    cov = np.loadtxt(DESI_DR2_COV)
    if cov.shape != (len(mean), len(mean)):
        raise ValueError(f"DESI DR2 covariance shape {cov.shape} does not match mean length {len(mean)}")
    mean["RowIndex"] = np.arange(len(mean))
    return mean, cov


def paired_dm_dh(mean: pd.DataFrame, cov: np.ndarray) -> tuple[pd.DataFrame, np.ndarray]:
    rows = []
    indices = []
    for z, group in mean.groupby("z", sort=True):
        dm = group[group["quantity"].eq("DM_over_rs")]
        dh = group[group["quantity"].eq("DH_over_rs")]
        if dm.empty or dh.empty:
            continue
        dm_row = dm.iloc[0]
        dh_row = dh.iloc[0]
        rows.append(
            {
                "z": float(z),
                "DM_over_rs": float(dm_row["value"]),
                "DH_over_rs": float(dh_row["value"]),
                "DM_RowIndex": int(dm_row["RowIndex"]),
                "DH_RowIndex": int(dh_row["RowIndex"]),
            }
        )
        indices.extend([int(dm_row["RowIndex"]), int(dh_row["RowIndex"])])
    paired = pd.DataFrame(rows)
    paired_cov = cov[np.ix_(indices, indices)]
    return paired, paired_cov


def unpack_draw(draw: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    values = draw.reshape(n, 2)
    return values[:, 0], values[:, 1]


def fit_poly_values(z: np.ndarray, y: np.ndarray, degree: int, eval_z: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    degree = min(degree, len(z) - 1)
    coeff = np.polyfit(z, y, degree)
    poly = np.poly1d(coeff)
    first = np.polyder(poly, 1)
    second = np.polyder(poly, 2)
    return poly(eval_z), first(eval_z), second(eval_z)


def reconstruct_one(z: np.ndarray, dm: np.ndarray, dh: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if np.any(dh <= 0.0):
        raise ValueError("DH_over_rs draw contains non-positive values")
    H_dimensionless = 1.0 / dh
    D, Dp, Dpp = fit_poly_values(z, dm, D_POLY_DEGREE, z)
    H, Hp, _ = fit_poly_values(z, H_dimensionless, H_POLY_DEGREE, z)
    omega = omega_r_plus_3omega_q(z, D, Dp, Dpp, H, Hp)
    return D, Dp, Dpp, H, Hp, omega


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    mean, cov = load_desi_dr2()
    paired, paired_cov = paired_dm_dh(mean, cov)
    z = paired["z"].to_numpy(float)
    n = len(paired)
    observed = paired[["DM_over_rs", "DH_over_rs"]].to_numpy(float).reshape(2 * n)

    D, Dp, Dpp, H, Hp, omega = reconstruct_one(
        z,
        paired["DM_over_rs"].to_numpy(float),
        paired["DH_over_rs"].to_numpy(float),
    )

    rng = np.random.default_rng(RNG_SEED)
    draws = rng.multivariate_normal(observed, paired_cov, size=BOOTSTRAP_DRAWS)
    vector_samples: list[np.ndarray] = []
    omega_samples: list[np.ndarray] = []
    skipped = 0
    for draw in draws:
        dm_draw, dh_draw = unpack_draw(draw, n)
        try:
            d_i, dp_i, dpp_i, h_i, hp_i, omega_i = reconstruct_one(z, dm_draw, dh_draw)
        except ValueError:
            skipped += 1
            continue
        vector_samples.append(np.column_stack([d_i, dp_i, dpp_i, h_i, hp_i]).reshape(5 * n))
        omega_samples.append(omega_i)

    vector_arr = np.asarray(vector_samples)
    omega_arr = np.asarray(omega_samples)
    vector_mean = vector_arr.mean(axis=0).reshape(n, 5)
    omega_mean = omega_arr.mean(axis=0)
    vector_cov = np.cov(vector_arr, rowvar=False)
    omega_cov = np.cov(omega_arr, rowvar=False)

    vector = pd.DataFrame(
        {
            "z": z,
            "D": vector_mean[:, 0],
            "D_prime": vector_mean[:, 1],
            "D_double_prime": vector_mean[:, 2],
            "H_D": vector_mean[:, 3],
            "H_D_prime": vector_mean[:, 4],
            "D_observed_DM_over_rs": paired["DM_over_rs"],
            "DH_observed_over_rs": paired["DH_over_rs"],
            "SourceRowID": [f"DESI_DR2_DM_DH_PAIR_{i}" for i in range(n)],
            "Source": "DESI_DR2_BAO_public_mean_covariance_polynomial_bootstrap_provisional",
            "ReconstructionStatus": "provisional_bao_only_not_source_native_symbolic_regression",
            "AllowedForMeasurementValidation": False,
            "ClaimBoundary": "provisional_backreaction_reconstruction_no_measurement_validation",
        }
    )
    vector.to_csv(OUT_VECTOR, index=False)
    np.savetxt(OUT_INPUT_COV, vector_cov, delimiter=",")

    omega_df = pd.DataFrame(
        {
            "z": z,
            "Omega_R_plus_3Omega_Q": omega_mean,
            "OmegaSigma": np.sqrt(np.diag(omega_cov)),
            "OmegaP16": np.percentile(omega_arr, 16, axis=0),
            "OmegaP84": np.percentile(omega_arr, 84, axis=0),
            "SourceVector": str(OUT_VECTOR.relative_to(ROOT)),
            "SourceCovariance": str(OUT_INPUT_COV.relative_to(ROOT)),
            "ReconstructionStatus": "provisional_bao_only_not_source_native_symbolic_regression",
            "AllowedForMeasurementValidation": False,
            "ClaimBoundary": "provisional_backreaction_reconstruction_no_measurement_validation",
        }
    )
    omega_df.to_csv(OUT_OMEGA, index=False)
    np.savetxt(OUT_OMEGA_COV, omega_cov, delimiter=",")

    sample_rows = []
    for i, sample in enumerate(omega_arr[: min(500, len(omega_arr))]):
        row = {"SampleID": i}
        for j, val in enumerate(sample):
            row[f"Omega_z{j}"] = val
        sample_rows.append(row)
    pd.DataFrame(sample_rows).to_csv(OUT_BOOTSTRAP, index=False)

    summary = pd.DataFrame(
        [
            {
                "SummaryID": "BACKREACTION_PROVISIONAL_BAO_RECONSTRUCTION_V1",
                "InputProduct": "DESI_DR2_BAO_GCcomb_mean_covariance",
                "Rows": n,
                "BootstrapDrawsRequested": BOOTSTRAP_DRAWS,
                "BootstrapDrawsUsed": len(omega_arr),
                "BootstrapDrawsSkipped": skipped,
                "DPolynomialDegree": D_POLY_DEGREE,
                "HPolynomialDegree": H_POLY_DEGREE,
                "FormulaOutputReady": True,
                "CovarianceOutputReady": True,
                "SourceNativeSymbolicRegressionReproduction": False,
                "AllowedForBackreactionPreflightScoring": True,
                "AllowedForMeasurementValidation": False,
                "OmegaMin": float(np.min(omega_mean)),
                "OmegaMax": float(np.max(omega_mean)),
                "OmegaAbsMedian": float(np.median(np.abs(omega_mean))),
                "CurrentStatus": "PROVISIONAL_BAO_ONLY_BACKREACTION_CURVE_READY_FOR_PREFLIGHT_SENSITIVITY",
                "StrongestAllowedClaim": (
                    "a provisional BAO-only backreaction curve is available for sensitivity checks; "
                    "it is not the source-native Koksbang-Heinesen symbolic-regression reconstruction"
                ),
                "PrimaryResidualRisk": "Pantheon+ distance reconstruction and symbolic-regression bootstrap are not reproduced",
                "NextAction": "run a provisional backreaction preflight comparison, labeled as sensitivity-only",
                "ClaimBoundary": "provisional_backreaction_reconstruction_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    lines = [
        "# Provisional BAO-Only Backreaction Reconstruction",
        "",
        "Status: provisional sensitivity input, not source-native measurement calibration.",
        "",
        "This reconstruction uses public DESI DR2 BAO `DM/rs` and `DH/rs` pairs. It fits simple polynomials to build `D`, `D_prime`, `D_double_prime`, `H_D`, and `H_D_prime`, then evaluates the fixed backreaction formula. It does not reproduce the Pantheon+ plus BAO symbolic-regression bootstrap pipeline from the source papers.",
        "",
        "## Outputs",
        "",
        f"- Reconstruction vector: `{OUT_VECTOR.relative_to(ROOT)}`",
        f"- Reconstruction covariance: `{OUT_INPUT_COV.relative_to(ROOT)}`",
        f"- Backreaction curve: `{OUT_OMEGA.relative_to(ROOT)}`",
        f"- Backreaction covariance: `{OUT_OMEGA_COV.relative_to(ROOT)}`",
        f"- Bootstrap preview: `{OUT_BOOTSTRAP.relative_to(ROOT)}`",
        f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
        "",
        "## Claim Boundary",
        "",
        "Allowed for preflight sensitivity only. Not measurement validation, not a backreaction-null rejection, and not a replacement for source-native symbolic-regression reconstruction.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_VECTOR}")
    print(f"Wrote {OUT_INPUT_COV}")
    print(f"Wrote {OUT_OMEGA}")
    print(f"Wrote {OUT_OMEGA_COV}")
    print(f"Wrote {OUT_BOOTSTRAP}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
