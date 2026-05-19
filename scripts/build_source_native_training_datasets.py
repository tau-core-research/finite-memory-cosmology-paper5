#!/usr/bin/env python3
"""Build source-native training datasets for D(z) and H_D(z) reproduction.

These are input datasets for a future symbolic-regression reproduction route.
They are not source-native derivative exports and do not authorize scoring.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public_ingest"
BR = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PANTHEON = PUBLIC / "pantheon_plus" / "Pantheon_SH0ES.dat"
DESI_DR1_MEAN = PUBLIC / "desi_dr1" / "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR1_COV = PUBLIC / "desi_dr1" / "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt"
DESI_DR2_MEAN = PUBLIC / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR2_COV = PUBLIC / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
UPSTREAM_BAO = BR / "upstream_2604_05822_bao_radial_table.csv"

OUT_SN = BR / "source_native_training_sn_distance_proxy.csv"
OUT_BAO = BR / "source_native_training_bao_hd_proxy.csv"
OUT_SUMMARY = EVIDENCE / "source_native_training_dataset_summary.csv"
OUT_DOC = DOCS / "source_native_training_datasets.md"


def distance_proxy_from_mu(mu: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Return D=(1+z)D_A = D_L/(1+z) in Mpc from distance modulus."""
    dl_mpc = 10.0 ** ((mu - 25.0) / 5.0)
    return dl_mpc / (1.0 + z)


def fractional_sigma_from_mu_sigma(mu_sigma: np.ndarray) -> np.ndarray:
    return np.log(10.0) * np.asarray(mu_sigma, dtype=float) / 5.0


def load_bao_mean(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, comment="#", sep=r"\s+", names=["z", "value", "quantity"])


def build_bao_rows(product_id: str, mean_path: Path, cov_path: Path) -> pd.DataFrame:
    mean = load_bao_mean(mean_path).reset_index(drop=True)
    cov = np.loadtxt(cov_path)
    sigma = np.sqrt(np.diag(cov))
    mean["Sigma"] = sigma
    radial = mean[mean["quantity"].eq("DH_over_rs")].copy()
    radial["ProductID"] = product_id
    radial["Hrs_over_c_proxy"] = 1.0 / radial["value"].to_numpy(float)
    radial["Hrs_over_c_sigma_proxy"] = radial["Sigma"].to_numpy(float) / (radial["value"].to_numpy(float) ** 2)
    radial["Source"] = f"public_ingest/{product_id}"
    radial["ClaimBoundary"] = "source_native_training_dataset_no_measurement_validation"
    return radial[
        [
            "ProductID",
            "z",
            "value",
            "Sigma",
            "Hrs_over_c_proxy",
            "Hrs_over_c_sigma_proxy",
            "Source",
            "ClaimBoundary",
        ]
    ].rename(columns={"value": "DH_over_rs", "Sigma": "DH_over_rs_sigma"})


def main() -> None:
    BR.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    sn = pd.read_csv(PANTHEON, sep=r"\s+")
    z = sn["zCMB"].to_numpy(float)
    mu = sn["MU_SH0ES"].to_numpy(float)
    mu_sigma = sn["MU_SH0ES_ERR_DIAG"].to_numpy(float)
    d_proxy = distance_proxy_from_mu(mu, z)
    d_sigma = d_proxy * fractional_sigma_from_mu_sigma(mu_sigma)
    sn_out = pd.DataFrame(
        {
            "ProductID": "PANTHEON_PLUS_SH0ES",
            "RowID": np.arange(len(sn), dtype=int),
            "z": z,
            "mu": mu,
            "mu_sigma_diag": mu_sigma,
            "D_proxy_Mpc": d_proxy,
            "D_proxy_sigma_diag_Mpc": d_sigma,
            "IsCalibrator": sn["IS_CALIBRATOR"].astype(int),
            "UsedInSH0ESHF": sn["USED_IN_SH0ES_HF"].astype(int),
            "Source": "data/public_ingest/pantheon_plus/Pantheon_SH0ES.dat",
            "ClaimBoundary": "source_native_training_dataset_no_measurement_validation",
        }
    )
    sn_out.to_csv(OUT_SN, index=False)

    upstream = pd.read_csv(UPSTREAM_BAO)
    upstream_bao = pd.DataFrame(
        {
            "ProductID": "UPSTREAM_2604_05822_RADIAL_BAO_TABLE",
            "z": upstream["z_eff"].to_numpy(float),
            "DH_over_rs": upstream["c_over_H_rs"].to_numpy(float),
            "DH_over_rs_sigma": upstream["sigma"].to_numpy(float),
            "Hrs_over_c_proxy": 1.0 / upstream["c_over_H_rs"].to_numpy(float),
            "Hrs_over_c_sigma_proxy": upstream["sigma"].to_numpy(float)
            / (upstream["c_over_H_rs"].to_numpy(float) ** 2),
            "Source": upstream["SourceLocation"].astype(str),
            "ClaimBoundary": "source_native_training_dataset_no_measurement_validation",
        }
    )
    bao_out = pd.concat(
        [
            upstream_bao,
            build_bao_rows("DESI_DR1", DESI_DR1_MEAN, DESI_DR1_COV),
            build_bao_rows("DESI_DR2", DESI_DR2_MEAN, DESI_DR2_COV),
        ],
        ignore_index=True,
    )
    bao_out.to_csv(OUT_BAO, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_TRAINING_DATASETS_V1",
                "SNTrainingRows": len(sn_out),
                "BAOTrainingRows": len(bao_out),
                "BAOProducts": int(bao_out["ProductID"].nunique()),
                "SNRedshiftMin": float(sn_out["z"].min()),
                "SNRedshiftMax": float(sn_out["z"].max()),
                "BAORedshiftMin": float(bao_out["z"].min()),
                "BAORedshiftMax": float(bao_out["z"].max()),
                "TrainingDatasetsReady": True,
                "DerivativeExportsReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_TRAINING_INPUTS_READY_DERIVATIVES_MISSING",
                "StrongestAllowedClaim": (
                    "public SN and radial BAO training inputs are exported for a future symbolic-regression reproduction route"
                ),
                "PrimaryResidualRisk": (
                    "training inputs are not the symbolic-regression derivative families and cannot be scored as source-native backreaction"
                ),
                "NextAction": "run or obtain symbolic-regression family exports for D,D_prime,D_double_prime,H_D,H_D_prime",
                "ClaimBoundary": "source_native_training_dataset_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Training Datasets",
                "",
                "Status: public training inputs exported; derivative families still missing.",
                "",
                "This creates SN distance-proxy and radial-BAO H_D-proxy training datasets for a future symbolic-regression reproduction route. These files are not source-native derivative exports.",
                "",
                "## Outputs",
                "",
                f"- SN training input: `{OUT_SN.relative_to(ROOT)}`",
                f"- BAO training input: `{OUT_BAO.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SN}")
    print(f"Wrote {OUT_BAO}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
