#!/usr/bin/env python3
"""Validate local public inputs for source-native backreaction reproduction."""

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
PANTHEON_COV = PUBLIC / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
DESI_DR1_MEAN = PUBLIC / "desi_dr1" / "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR1_COV = PUBLIC / "desi_dr1" / "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt"
DESI_DR2_MEAN = PUBLIC / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR2_COV = PUBLIC / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
UPSTREAM_BAO = BR / "upstream_2604_05822_bao_radial_table.csv"

OUT_SN = EVIDENCE / "source_native_sn_input_validation.csv"
OUT_BAO = EVIDENCE / "source_native_bao_input_validation.csv"
OUT_SUMMARY = EVIDENCE / "source_native_public_input_validation_summary.csv"
OUT_DOC = DOCS / "source_native_public_input_validation.md"


def read_pantheon_cov_shape(path: Path) -> tuple[int, int, int]:
    values = np.loadtxt(path)
    n_declared = int(values[0])
    flat = values[1:]
    n_side = int(round(np.sqrt(len(flat))))
    return n_declared, len(flat), n_side


def cov_status(cov: np.ndarray) -> tuple[bool, float]:
    sym = 0.5 * (cov + cov.T)
    eig_min = float(np.linalg.eigvalsh(sym).min())
    return eig_min > 0.0, eig_min


def load_bao_mean(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, comment="#", sep=r"\s+", names=["z", "value", "quantity"])


def validate_bao(label: str, mean_path: Path, cov_path: Path, upstream: pd.DataFrame) -> dict[str, object]:
    mean = load_bao_mean(mean_path)
    cov = np.loadtxt(cov_path)
    posdef, eig_min = cov_status(cov)
    radial = mean[mean["quantity"].eq("DH_over_rs")].copy()
    upstream_matches = int(sum(np.any(np.isclose(upstream["z_eff"].to_numpy(float), z, atol=0.01)) for z in radial["z"].to_numpy(float)))
    return {
        "ValidationID": f"{label}_BAO_INPUT_VALIDATION",
        "ProductID": label,
        "MeanRows": len(mean),
        "CovRows": cov.shape[0],
        "CovCols": cov.shape[1],
        "RowsMatchCovariance": len(mean) == cov.shape[0] == cov.shape[1],
        "CovariancePositiveDefinite": posdef,
        "MinCovarianceEigenvalue": eig_min,
        "RadialDHRows": len(radial),
        "UpstreamBAORowsWithinDz001": upstream_matches,
        "AvailableForHDInputValidation": len(mean) == cov.shape[0] == cov.shape[1] and posdef and len(radial) > 0,
        "AllowedForMeasurementValidation": False,
        "ClaimBoundary": "source_native_public_input_validation_no_measurement_validation",
    }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    pantheon = pd.read_csv(PANTHEON, sep=r"\s+")
    n_declared, flat_count, cov_side = read_pantheon_cov_shape(PANTHEON_COV)
    required_cols = {"zHD", "zCMB", "MU_SH0ES", "MU_SH0ES_ERR_DIAG"}
    sn = pd.DataFrame(
        [
            {
                "ValidationID": "PANTHEON_PLUS_SN_INPUT_VALIDATION",
                "Rows": len(pantheon),
                "RequiredColumnsPresent": required_cols.issubset(set(pantheon.columns)),
                "DeclaredCovarianceSize": n_declared,
                "CovarianceFlatEntries": flat_count,
                "CovarianceSideFromFlatEntries": cov_side,
                "RowsMatchDeclaredCovariance": len(pantheon) == n_declared,
                "CovarianceShapeConsistent": n_declared == cov_side,
                "RedshiftMin": float(pantheon["zCMB"].min()),
                "RedshiftMax": float(pantheon["zCMB"].max()),
                "AvailableForDInputValidation": required_cols.issubset(set(pantheon.columns))
                and len(pantheon) == n_declared
                and n_declared == cov_side,
                "AllowedForMeasurementValidation": False,
                "ClaimBoundary": "source_native_public_input_validation_no_measurement_validation",
            }
        ]
    )
    sn.to_csv(OUT_SN, index=False)

    upstream = pd.read_csv(UPSTREAM_BAO)
    bao = pd.DataFrame(
        [
            validate_bao("DESI_DR1", DESI_DR1_MEAN, DESI_DR1_COV, upstream),
            validate_bao("DESI_DR2", DESI_DR2_MEAN, DESI_DR2_COV, upstream),
        ]
    )
    bao.to_csv(OUT_BAO, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_PUBLIC_INPUT_VALIDATION_V1",
                "SNInputValidated": bool(sn["AvailableForDInputValidation"].iloc[0]),
                "BAOProductsValidated": int(bao["AvailableForHDInputValidation"].map(bool).sum()),
                "BAOProductsAudited": len(bao),
                "AllPublicInputsValidated": bool(sn["AvailableForDInputValidation"].iloc[0])
                and bool(bao["AvailableForHDInputValidation"].map(bool).all()),
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "PUBLIC_INPUTS_VALIDATED_FOR_REPRODUCTION_PREFLIGHT",
                "StrongestAllowedClaim": (
                    "local Pantheon+ and DESI BAO inputs pass structural validation for a source-native reproduction preflight"
                ),
                "PrimaryResidualRisk": (
                    "input validation does not provide symbolic-regression reconstructions, derivative vectors, or source-native covariance"
                ),
                "NextAction": "construct or obtain D/H_D symbolic-regression family exports",
                "ClaimBoundary": "source_native_public_input_validation_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Public Input Validation",
                "",
                "Status: public inputs structurally validated for reproduction preflight.",
                "",
                "This validates local Pantheon+ and DESI BAO input structure only. It does not produce the symbolic-regression reconstruction vectors needed for source-native backreaction scoring.",
                "",
                "## Outputs",
                "",
                f"- SN validation: `{OUT_SN.relative_to(ROOT)}`",
                f"- BAO validation: `{OUT_BAO.relative_to(ROOT)}`",
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
