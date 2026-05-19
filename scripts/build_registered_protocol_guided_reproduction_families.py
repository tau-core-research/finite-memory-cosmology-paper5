#!/usr/bin/env python3
"""Build predeclared-protocol-guided local reproduction families.

The family taxonomy follows the published symbolic-reconstruction protocol,
but the numerical exports are local reproductions from the existing 200
bootstrap D/H branches. Manual author choices and unpublished hall-of-fame
exports are not available, so fully source-native reproduction remains closed.
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
PROTOCOL = EVIDENCE / "source_native_symbolic_protocol_extract.csv"

OUT_REGISTRY = EVIDENCE / "registered_protocol_family_registry.csv"
OUT_RECON = DATA / "registered_protocol_guided_reproduction_reconstruction_vector.csv"
OUT_META = DATA / "registered_protocol_guided_reproduction_selection_metadata.csv"
OUT_OMEGA = DATA / "registered_protocol_guided_reproduction_backreaction_vector.csv"
OUT_SAMPLES = DATA / "registered_protocol_guided_reproduction_backreaction_bootstrap_samples.csv"
OUT_COV = DATA / "registered_protocol_guided_reproduction_backreaction_covariance.csv"
OUT_SUMMARY = EVIDENCE / "registered_protocol_guided_reproduction_summary.csv"
OUT_DOC = DOCS / "registered_protocol_guided_reproduction_families.md"

CLAIM_BOUNDARY = "registered_protocol_guided_reproduction_no_measurement_validation"


def contains_nonlinear(expr: object) -> bool:
    text = str(expr)
    markers = ["**2", "square", "sin", "cos", "exp", "log", "/", "*"]
    return any(marker in text for marker in markers)


def build_registry() -> pd.DataFrame:
    rows = [
        {
            "FamilyID": "REGISTERED_DA_FILTERED_PROXY",
            "PublishedProtocolBasis": "d_A criteria I-III: MSE threshold plus derivative/oscillation rejection",
            "LocalProxyRule": "D derivative-regularized branch; finite predictions; curvature-regularized selection",
            "SourceNative": False,
            "ManualJudgmentRequiredByPaper": True,
            "NumericalExportAvailable": True,
            "UsedInThisRun": True,
            "ResidualRisk": "manual shape rejection and source expression exports are unavailable",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "FamilyID": "REGISTERED_HD_CRITERIA_1_SIMPLE_PROXY",
            "PublishedProtocolBasis": "H_D criteria set 1: three simplest nonconstant nonlinear hall-of-fame expressions",
            "LocalProxyRule": "lowest H complexity nonconstant bootstrap expressions; nonlinear marker preferred when present",
            "SourceNative": False,
            "ManualJudgmentRequiredByPaper": True,
            "NumericalExportAvailable": True,
            "UsedInThisRun": True,
            "ResidualRisk": "local metadata lacks the full PySR hall-of-fame and exact three-expression selection",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "FamilyID": "REGISTERED_HD_CRITERIA_2_LOW_LOSS_PROXY",
            "PublishedProtocolBasis": "H_D criteria set 2: up to three lowest-loss nonpathological hall-of-fame expressions",
            "LocalProxyRule": "lowest H loss bootstrap expressions with finite prediction; pathology rejection approximated by finite outputs",
            "SourceNative": False,
            "ManualJudgmentRequiredByPaper": True,
            "NumericalExportAvailable": True,
            "UsedInThisRun": True,
            "ResidualRisk": "manual nonpathological filtering is approximated, not source-native",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "FamilyID": "REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY",
            "PublishedProtocolBasis": "H_D criteria set 3: minimize Loss + 1.0 * Complexity",
            "LocalProxyRule": "registered normalized criteria-3 bootstrap selector",
            "SourceNative": False,
            "ManualJudgmentRequiredByPaper": False,
            "NumericalExportAvailable": True,
            "UsedInThisRun": True,
            "ResidualRisk": "PySR/cp3-bench implementation details and upstream seeds may differ",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "FamilyID": "REGISTERED_DESI_BRANCH_TARGET",
            "PublishedProtocolBasis": "DESI radial BAO branch",
            "LocalProxyRule": "requires branch-specific D/H bootstrap rerun using DESI-only training input",
            "SourceNative": False,
            "ManualJudgmentRequiredByPaper": False,
            "NumericalExportAvailable": False,
            "UsedInThisRun": False,
            "ResidualRisk": "current H branch uses combined radial BAO training input, not isolated DESI-only family",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "FamilyID": "REGISTERED_BOSS_EBOSS_BRANCH_TARGET",
            "PublishedProtocolBasis": "BOSS/eBOSS radial BAO branch",
            "LocalProxyRule": "requires branch-specific D/H bootstrap rerun using BOSS/eBOSS-only training input",
            "SourceNative": False,
            "ManualJudgmentRequiredByPaper": False,
            "NumericalExportAvailable": False,
            "UsedInThisRun": False,
            "ResidualRisk": "current H branch uses combined radial BAO training input, not isolated BOSS/eBOSS-only family",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
    ]
    return pd.DataFrame(rows)


def family_masks(meta: pd.DataFrame) -> dict[str, pd.Series]:
    h_nonconstant = ~meta["SelectedIsConstant_H"].astype(str).str.lower().eq("true")
    h_nonlinear = meta["SelectedSympyExpression_H"].map(contains_nonlinear)
    simple = h_nonconstant & h_nonlinear & (
        meta["SelectedComplexity_H"].astype(float) <= meta["SelectedComplexity_H"].astype(float).quantile(0.40)
    )
    if int(simple.sum()) < 10:
        simple = h_nonconstant & (
            meta["SelectedComplexity_H"].astype(float) <= meta["SelectedComplexity_H"].astype(float).quantile(0.40)
        )

    low_loss = h_nonconstant & (
        meta["SelectedLoss_H"].astype(float) <= meta["SelectedLoss_H"].astype(float).quantile(0.20)
    )
    criteria3 = (
        meta["NormalizedCriteria3Score_H"].astype(float)
        <= meta["NormalizedCriteria3Score_H"].astype(float).quantile(0.20)
    )
    da_filtered = (
        meta["DLowDepthCurvatureMetric"].astype(float)
        <= meta["DLowDepthCurvatureMetric"].astype(float).quantile(0.80)
    )

    return {
        "REGISTERED_HD_CRITERIA_1_SIMPLE_PROXY": da_filtered & simple,
        "REGISTERED_HD_CRITERIA_2_LOW_LOSS_PROXY": da_filtered & low_loss,
        "REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY": da_filtered & criteria3,
    }


def covariance_long(samples: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family_id, group in samples.groupby("FamilyID", sort=False):
        pivot = group.pivot_table(
            index="BootstrapIndex",
            columns="z",
            values="Omega_R_plus_3Omega_Q",
            aggfunc="first",
        )
        cov = np.cov(pivot.to_numpy(float), rowvar=False)
        for i, zi in enumerate(pivot.columns):
            for j, zj in enumerate(pivot.columns):
                rows.append(
                    {
                        "FamilyID": family_id,
                        "z_i": float(zi),
                        "z_j": float(zj),
                        "Covariance": float(cov[i, j]),
                        "Samples": int(len(pivot)),
                        "Source": "registered_protocol_guided_local_reproduction_bootstrap_covariance",
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    registry = build_registry()
    registry.to_csv(OUT_REGISTRY, index=False)

    protocol = pd.read_csv(PROTOCOL)
    d_meta = pd.read_csv(D_META)
    h_meta = pd.read_csv(H_META)
    d_samples = pd.read_csv(D_SAMPLES)
    h_samples = pd.read_csv(H_SAMPLES)
    meta = d_meta.merge(h_meta, on="BootstrapIndex", suffixes=("_D", "_H"))
    meta["DLowDepthCurvatureMetric"] = meta["LowDepthCurvatureMetric"].astype(float)

    recon_rows = []
    metadata_rows = []
    omega_rows = []
    omega_sample_rows = []

    for family_id, mask in family_masks(meta).items():
        selected = meta[mask].copy()
        if selected.empty:
            continue
        sample_ids = sorted(selected["BootstrapIndex"].astype(int).unique().tolist())
        family_recon_samples = []
        family_omega_samples = []
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
            for values in zip(z, D, Dp, Dpp, H, Hp, omega):
                z_val, d_val, dp_val, dpp_val, h_val, hp_val, omega_val = values
                family_recon_samples.append(
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
                family_omega_samples.append(
                    {
                        "FamilyID": family_id,
                        "BootstrapIndex": int(sample_id),
                        "z": float(z_val),
                        "Omega_R_plus_3Omega_Q": float(omega_val),
                        "Source": "registered_protocol_guided_local_reproduction_bootstrap",
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )

        recon_df = pd.DataFrame(family_recon_samples)
        omega_df = pd.DataFrame(family_omega_samples)
        for z_val, group in recon_df.groupby("z", sort=True):
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
                    "Source": "registered_protocol_guided_local_reproduction_median",
                    "SelectionRule": family_id,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
        for z_val, group in omega_df.groupby("z", sort=True):
            omega_rows.append(
                {
                    "FamilyID": family_id,
                    "SampleID": 0,
                    "z": float(z_val),
                    "Omega_R_plus_3Omega_Q": float(group["Omega_R_plus_3Omega_Q"].median()),
                    "Source": "registered_protocol_guided_local_reproduction_median",
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
        omega_sample_rows.extend(family_omega_samples)
        reg = registry[registry["FamilyID"].eq(family_id)].iloc[0]
        metadata_rows.append(
            {
                "FamilyID": family_id,
                "DataCombination": "public_SN_proxy_plus_combined_radial_BAO_HD_proxy",
                "CriteriaSet": str(reg["PublishedProtocolBasis"]),
                "Algorithm": "local_bootstrap_filter_using_published_protocol_proxy",
                "ExpressionID": "multiple_local_bootstrap_expressions",
                "SelectionRule": str(reg["LocalProxyRule"]),
                "BootstrapSamples": len(sample_ids),
                "MedianHComplexity": float(selected["SelectedComplexity_H"].median()),
                "MedianHLoss": float(selected["SelectedLoss_H"].median()),
                "MedianDLowDepthCurvatureMetric": float(selected["DLowDepthCurvatureMetric"].median()),
                "ProtocolItemsAvailable": int(len(protocol)),
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "FittedInThisNote": True,
                "SourceExport": False,
                "SourceNative": False,
                "ReproductionFamily": True,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    recon = pd.DataFrame(recon_rows)
    metadata = pd.DataFrame(metadata_rows)
    omega = pd.DataFrame(omega_rows)
    samples = pd.DataFrame(omega_sample_rows)
    cov = covariance_long(samples)

    recon.to_csv(OUT_RECON, index=False)
    metadata.to_csv(OUT_META, index=False)
    omega.to_csv(OUT_OMEGA, index=False)
    samples.to_csv(OUT_SAMPLES, index=False)
    cov.to_csv(OUT_COV, index=False)

    finite = bool(
        np.isfinite(recon[["D", "D_prime", "D_double_prime", "H_D", "H_D_prime"]].to_numpy(float)).all()
    )
    omega_finite = bool(np.isfinite(omega["Omega_R_plus_3Omega_Q"].to_numpy(float)).all())
    used_registry = registry[registry["UsedInThisRun"].astype(bool)]
    blocked_registry = registry[~registry["NumericalExportAvailable"].astype(bool)]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "REGISTERED_PROTOCOL_GUIDED_REPRODUCTION_V1",
                "RegisteredFamilies": int(len(registry)),
                "UsedFamilies": int(metadata["FamilyID"].nunique()),
                "BlockedProtocolFamilies": int(len(blocked_registry)),
                "ReconstructionRows": int(len(recon)),
                "OmegaRows": int(len(omega)),
                "OmegaBootstrapRows": int(len(samples)),
                "MinBootstrapSamplesPerFamily": int(metadata["BootstrapSamples"].min()),
                "MaxBootstrapSamplesPerFamily": int(metadata["BootstrapSamples"].max()),
                "FiniteDerivativeVectors": finite,
                "FiniteOmegaVectors": omega_finite,
                "OmegaAbsMax": float(omega["Omega_R_plus_3Omega_Q"].abs().max()),
                "PublishedProtocolBasisAvailable": int(len(used_registry)) > 0,
                "SourceExport": False,
                "SourceNative": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "REGISTERED_PROTOCOL_GUIDED_LOCAL_REPRODUCTION_READY",
                "StrongestAllowedClaim": (
                    "published selection protocols can define local reproduction-family labels and proxy filters"
                ),
                "PrimaryResidualRisk": (
                    "manual hall-of-fame decisions and branch-specific source exports remain unavailable"
                ),
                "NextAction": (
                    "score predeclared-protocol-guided families against locked K2 and separately implement DESI/eBOSS branch-specific reruns"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Registered-Protocol-Guided Reproduction Families",
                "",
                "Status: REGISTERED_PROTOCOL_GUIDED_LOCAL_REPRODUCTION_READY.",
                "",
                "These families use labels and selection logic derived from the published symbolic-reconstruction protocol, while the numerical curves are local 200-bootstrap reproductions. They are not source/source-native exports.",
                "",
                "## Available Families",
                "",
                "- `REGISTERED_HD_CRITERIA_1_SIMPLE_PROXY`",
                "- `REGISTERED_HD_CRITERIA_2_LOW_LOSS_PROXY`",
                "- `REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY`",
                "",
                "## Registered But Not Yet Numerically Exported",
                "",
                "- `REGISTERED_DESI_BRANCH_TARGET`",
                "- `REGISTERED_BOSS_EBOSS_BRANCH_TARGET`",
                "",
                "## Outputs",
                "",
                f"- Registry: `{OUT_REGISTRY.relative_to(ROOT)}`",
                f"- Reconstruction vector: `{OUT_RECON.relative_to(ROOT)}`",
                f"- Metadata: `{OUT_META.relative_to(ROOT)}`",
                f"- Backreaction vector: `{OUT_OMEGA.relative_to(ROOT)}`",
                f"- Bootstrap samples: `{OUT_SAMPLES.relative_to(ROOT)}`",
                f"- Covariance: `{OUT_COV.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "No K2 change, no K1 refit, no amplitude fit, and no measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_REGISTRY.relative_to(ROOT)}")
    print(f"Wrote {OUT_OMEGA.relative_to(ROOT)}")
    print(f"Wrote {OUT_SAMPLES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
