#!/usr/bin/env python3
"""Build local source-native-style reproduction families from 200 bootstraps.

This promotes the single local reproduction candidate into several transparent
reproduction-family exports formed only from D/H branch metadata. The family
rules do not use K2, target signs, amplitude fits, or source-native author
exports.
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

D_META = DATA / "d_branch_derivative_regularized_bootstrap_200_selection_metadata.csv"
H_META = DATA / "h_branch_normalized_criteria3_bootstrap_200_selection_metadata.csv"
D_SAMPLES = DATA / "d_branch_derivative_regularized_bootstrap_200_samples.csv"
H_SAMPLES = DATA / "h_branch_normalized_criteria3_bootstrap_200_samples.csv"

OUT_RECON = DATA / "source_native_reproduction_family_reconstruction_vector.csv"
OUT_META = DATA / "source_native_reproduction_family_selection_metadata.csv"
OUT_OMEGA = DATA / "source_native_reproduction_family_backreaction_vector.csv"
OUT_OMEGA_SAMPLES = DATA / "source_native_reproduction_family_backreaction_bootstrap_samples.csv"
OUT_COV = DATA / "source_native_reproduction_family_backreaction_family_covariance.csv"
OUT_SUMMARY = EVIDENCE / "source_native_reproduction_family_export_summary.csv"
OUT_DOC = DOCS / "source_native_reproduction_family_exports.md"

CLAIM_BOUNDARY = "source_native_reproduction_family_exports_no_measurement_validation"


def quantile_mask(values: pd.Series, lo: float | None = None, hi: float | None = None) -> pd.Series:
    mask = pd.Series(True, index=values.index)
    if lo is not None:
        mask &= values >= float(values.quantile(lo))
    if hi is not None:
        mask &= values <= float(values.quantile(hi))
    return mask


def family_rules(meta: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "LOCAL_BEST_SCORE_Q20": quantile_mask(meta["CombinedScore"], hi=0.20),
        "LOCAL_SMOOTH_D_Q20": quantile_mask(meta["DLowDepthCurvatureMetric"], hi=0.20),
        "LOCAL_LOW_COMPLEXITY_TERCILE": quantile_mask(meta["CombinedComplexity"], hi=0.33),
        "LOCAL_MID_COMPLEXITY_TERCILE": quantile_mask(meta["CombinedComplexity"], lo=0.33, hi=0.67),
        "LOCAL_HIGH_COMPLEXITY_TERCILE": quantile_mask(meta["CombinedComplexity"], lo=0.67),
    }


def covariance_long(samples: pd.DataFrame) -> pd.DataFrame:
    cov_rows = []
    for family_id, group in samples.groupby("FamilyID", sort=False):
        pivot = group.pivot_table(
            index="BootstrapIndex",
            columns="z",
            values="Omega_R_plus_3Omega_Q",
            aggfunc="first",
        )
        cov = np.cov(pivot.to_numpy(float), rowvar=False)
        z_vals = [float(z) for z in pivot.columns]
        for i, zi in enumerate(z_vals):
            for j, zj in enumerate(z_vals):
                cov_rows.append(
                    {
                        "FamilyID": family_id,
                        "z_i": zi,
                        "z_j": zj,
                        "Covariance": float(cov[i, j]),
                        "Samples": int(len(pivot)),
                        "Source": "local_reproduction_family_bootstrap_covariance",
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    return pd.DataFrame(cov_rows)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    d_meta = pd.read_csv(D_META)
    h_meta = pd.read_csv(H_META)
    d_samples = pd.read_csv(D_SAMPLES)
    h_samples = pd.read_csv(H_SAMPLES)

    meta = d_meta.merge(
        h_meta,
        on="BootstrapIndex",
        suffixes=("_D", "_H"),
    )
    meta["CombinedScore"] = (
        meta["DerivativeRegularizedScore"].astype(float) + meta["NormalizedCriteria3Score_H"].astype(float)
    )
    meta["CombinedComplexity"] = meta["SelectedComplexity_D"].astype(float) + meta["SelectedComplexity_H"].astype(float)
    meta["DLowDepthCurvatureMetric"] = meta["LowDepthCurvatureMetric"].astype(float)

    recon_rows: list[dict[str, object]] = []
    meta_rows: list[dict[str, object]] = []
    omega_rows: list[dict[str, object]] = []
    omega_sample_rows: list[dict[str, object]] = []

    for family_id, mask in family_rules(meta).items():
        selected = meta[mask].copy()
        if selected.empty:
            continue
        sample_ids = sorted(selected["BootstrapIndex"].astype(int).unique().tolist())

        family_sample_recon = []
        family_sample_omega = []
        for sample_id in sample_ids:
            dg = d_samples[d_samples["BootstrapIndex"].eq(sample_id)].sort_values("z")
            hg = h_samples[h_samples["BootstrapIndex"].eq(sample_id)].sort_values("z")
            z = hg["z"].to_numpy(float)
            d_z = dg["z"].to_numpy(float)
            D = np.interp(z, d_z, dg["D"].to_numpy(float))
            Dp = np.interp(z, d_z, dg["D_prime"].to_numpy(float))
            Dpp = np.interp(z, d_z, dg["D_double_prime"].to_numpy(float))
            H = hg["H_D_proxy"].to_numpy(float)
            Hp = hg["H_D_prime_proxy"].to_numpy(float)
            omega = omega_r_plus_3omega_q(z, D, Dp, Dpp, H, Hp)
            for values in zip(z, D, Dp, Dpp, H, Hp, omega, strict=True):
                z_val, d_val, dp_val, dpp_val, h_val, hp_val, omega_val = values
                family_sample_recon.append(
                    {
                        "FamilyID": family_id,
                        "BootstrapIndex": int(sample_id),
                        "z": float(z_val),
                        "D": float(d_val),
                        "D_prime": float(dp_val),
                        "D_double_prime": float(dpp_val),
                        "H_D": float(h_val),
                        "H_D_prime": float(hp_val),
                    }
                )
                family_sample_omega.append(
                    {
                        "FamilyID": family_id,
                        "BootstrapIndex": int(sample_id),
                        "z": float(z_val),
                        "Omega_R_plus_3Omega_Q": float(omega_val),
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )

        family_recon_df = pd.DataFrame(family_sample_recon)
        family_omega_df = pd.DataFrame(family_sample_omega)
        for z_val, group in family_recon_df.groupby("z", sort=True):
            recon_rows.append(
                {
                    "FamilyID": family_id,
                    "SampleID": 0,
                    "z": float(z_val),
                    "D": float(group["D"].median()),
                    "D_prime": float(group["D_prime"].median()),
                    "D_double_prime": float(group["D_double_prime"].median()),
                    "H_D": float(group["H_D"].median()),
                    "H_D_prime": float(group["H_D_prime"].median()),
                    "Source": "local_reproduction_family_bootstrap_median",
                    "SelectionRule": family_id,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
        for z_val, group in family_omega_df.groupby("z", sort=True):
            omega_rows.append(
                {
                    "FamilyID": family_id,
                    "SampleID": 0,
                    "z": float(z_val),
                    "Omega_R_plus_3Omega_Q": float(group["Omega_R_plus_3Omega_Q"].median()),
                    "Source": "local_reproduction_family_bootstrap_median",
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
        omega_sample_rows.extend(family_sample_omega)
        meta_rows.append(
            {
                "FamilyID": family_id,
                "SelectionRule": family_id,
                "BootstrapSamples": len(sample_ids),
                "MedianCombinedScore": float(selected["CombinedScore"].median()),
                "MedianCombinedComplexity": float(selected["CombinedComplexity"].median()),
                "MedianDLowDepthCurvatureMetric": float(selected["DLowDepthCurvatureMetric"].median()),
                "MinBootstrapIndex": int(min(sample_ids)),
                "MaxBootstrapIndex": int(max(sample_ids)),
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "AuthorExport": False,
                "ReproductionFamily": True,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    recon = pd.DataFrame(recon_rows)
    metadata = pd.DataFrame(meta_rows)
    omega = pd.DataFrame(omega_rows)
    omega_samples = pd.DataFrame(omega_sample_rows)
    cov = covariance_long(omega_samples)

    recon.to_csv(OUT_RECON, index=False)
    metadata.to_csv(OUT_META, index=False)
    omega.to_csv(OUT_OMEGA, index=False)
    omega_samples.to_csv(OUT_OMEGA_SAMPLES, index=False)
    cov.to_csv(OUT_COV, index=False)

    finite = bool(
        np.isfinite(recon[["D", "D_prime", "D_double_prime", "H_D", "H_D_prime"]].to_numpy(float)).all()
    )
    omega_finite = bool(np.isfinite(omega["Omega_R_plus_3Omega_Q"].to_numpy(float)).all())
    family_count = int(metadata["FamilyID"].nunique())
    min_samples = int(metadata["BootstrapSamples"].min())
    max_samples = int(metadata["BootstrapSamples"].max())
    omega_abs_max = float(omega["Omega_R_plus_3Omega_Q"].abs().max())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_REPRODUCTION_FAMILY_EXPORTS_V1",
                "Families": family_count,
                "MinBootstrapSamplesPerFamily": min_samples,
                "MaxBootstrapSamplesPerFamily": max_samples,
                "ReconstructionRows": len(recon),
                "OmegaRows": len(omega),
                "OmegaBootstrapRows": len(omega_samples),
                "FiniteDerivativeVectors": finite,
                "FiniteOmegaVectors": omega_finite,
                "OmegaAbsMax": omega_abs_max,
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "AuthorExport": False,
                "ReproductionFamily": True,
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "LOCAL_REPRODUCTION_FAMILY_EXPORTS_READY_NOT_AUTHOR_SOURCE_NATIVE",
                "StrongestAllowedClaim": (
                    "local source-native-style reproduction families can be exported from the 200-bootstrap D/H branches"
                ),
                "PrimaryResidualRisk": (
                    "family rules are local metadata-based reproductions, not author/source-native symbolic-regression exports"
                ),
                "NextAction": "score local reproduction families against locked K2 and compare with the single criteria-set-3 candidate",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Reproduction Family Exports",
                "",
                "Status: LOCAL_REPRODUCTION_FAMILY_EXPORTS_READY_NOT_AUTHOR_SOURCE_NATIVE.",
                "",
                "This artifact forms several local reproduction families from the 200-bootstrap D and H_D branch metadata. The rules use score, derivative smoothness, and complexity only. They do not use K2, target signs, amplitude fitting, or author exports.",
                "",
                "## Outputs",
                "",
                f"- Reconstruction vector: `{OUT_RECON.relative_to(ROOT)}`",
                f"- Metadata: `{OUT_META.relative_to(ROOT)}`",
                f"- Backreaction vector: `{OUT_OMEGA.relative_to(ROOT)}`",
                f"- Bootstrap samples: `{OUT_OMEGA_SAMPLES.relative_to(ROOT)}`",
                f"- Family covariance: `{OUT_COV.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "This is a local reproduction-family preflight layer. It is not author source-native validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_RECON.relative_to(ROOT)}")
    print(f"Wrote {OUT_OMEGA.relative_to(ROOT)}")
    print(f"Wrote {OUT_OMEGA_SAMPLES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
