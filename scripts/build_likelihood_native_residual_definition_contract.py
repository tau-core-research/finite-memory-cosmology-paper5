#!/usr/bin/env python3
"""Define SN/BAO residual contracts required before measurement scoring.

This contract turns the FLN_1/FLN_2 blockers into explicit, auditable choices.
It does not construct a new residual vector or change the locked A2 prediction.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SN_SUMMARY = EVIDENCE / "sn_residual_preflight_summary.csv"
BAO_SUMMARY = EVIDENCE / "bao_residual_transform_summary.csv"
INPUT_SUMMARY = EVIDENCE / "likelihood_native_input_object_summary.csv"
POLICY_READINESS = EVIDENCE / "likelihood_native_residual_policy_readiness.csv"

OUT_CONTRACT = EVIDENCE / "likelihood_native_residual_definition_contract.csv"
OUT_READINESS = EVIDENCE / "likelihood_native_residual_definition_readiness.csv"
OUT_DOC = DOCS / "likelihood_native_residual_definition_contract.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty input: {path}")
    return df.iloc[0]


def resolved_contracts() -> set[str]:
    if not POLICY_READINESS.exists():
        return set()
    row = first(POLICY_READINESS)
    return {
        item
        for item in str(row.get("ResolvedResidualContractIDs", "")).split(";")
        if item
    }


def main() -> None:
    sn = pd.read_csv(SN_SUMMARY)
    bao = pd.read_csv(BAO_SUMMARY)
    inputs = first(INPUT_SUMMARY)

    sn_raw = sn[sn["ArtifactID"].eq("SN_RAW_RESIDUAL_PREFLIGHT")].iloc[0]
    sn_binned = sn[sn["ArtifactID"].eq("SN_BINNED_TO_CURRENT_GRID_PREFLIGHT")].iloc[0]
    bao_dr2 = bao[bao["ProductID"].eq("DESI_DR2_BAO_ALL_GAUSSIAN")].iloc[0]
    resolved = resolved_contracts()

    rows = [
        {
            "ContractID": "RDEF_SN_1_OBSERVABLE",
            "Source": "Pantheon+SH0ES",
            "ResidualObject": "r_SN",
            "DefinitionStatus": "PREFLIGHT_EXISTS_NOT_MEASUREMENT_FROZEN",
            "CurrentDefinition": "MU_SH0ES - mu_flat_LCDM_audit",
            "CurrentArtifact": "evidence/sn_residual_preflight.csv",
            "ObservedRows": int(sn_raw["Rows"]),
            "PreflightMetric": f"median_sigma={sn_raw['MedianSigmaDiag']}",
            "MeasurementRequirement": "choose public-likelihood distance-modulus residual definition and redshift column",
            "BlockingIssue": "distance modulus baseline and nuisance/marginalization policy are not frozen",
            "AllowedForMeasurementTransform": False,
            "ResolvedForRerunCandidate": "RDEF_SN_1_OBSERVABLE" in resolved,
            "NextAction": "freeze SN residual as either raw public mu residual or nuisance-marginalized residual before L_SN",
        },
        {
            "ContractID": "RDEF_SN_2_OFFSET_POLICY",
            "Source": "Pantheon+SH0ES",
            "ResidualObject": "SN_offset",
            "DefinitionStatus": "PREFLIGHT_OFFSET_EXISTS_NOT_ALLOWED_AS_K1_TARGET",
            "CurrentDefinition": "inverse-variance same-sample offset subtraction",
            "CurrentArtifact": "evidence/sn_residual_preflight_summary.csv",
            "ObservedRows": int(sn_raw["Rows"]),
            "PreflightMetric": f"same_sample_offset_mu={sn_raw['SameSampleOffsetMu']}",
            "MeasurementRequirement": "declare whether absolute magnitude/nuisance offset is externally fixed, marginalized, or projected out",
            "BlockingIssue": "same-sample offset subtraction would leak target information into the residual",
            "AllowedForMeasurementTransform": False,
            "ResolvedForRerunCandidate": "RDEF_SN_2_OFFSET_POLICY" in resolved,
            "NextAction": "replace same-sample centering with predeclared nuisance treatment",
        },
        {
            "ContractID": "RDEF_SN_3_GRID_TRANSFORM",
            "Source": "Pantheon+SH0ES",
            "ResidualObject": "L_SN",
            "DefinitionStatus": "BINNED_PREFLIGHT_EXISTS_NOT_MEASUREMENT_FROZEN",
            "CurrentDefinition": "diagonal-weighted binning to current 8-point grid",
            "CurrentArtifact": "evidence/sn_residual_binned_preflight.csv",
            "ObservedRows": int(sn_binned["Rows"]),
            "PreflightMetric": f"median_sigma_proxy={sn_binned['MedianSigmaDiag']}",
            "MeasurementRequirement": "construct L_SN from the likelihood-native SN residual vector with full covariance propagation",
            "BlockingIssue": "current grid transform is binned/diagonal proxy",
            "AllowedForMeasurementTransform": False,
            "ResolvedForRerunCandidate": "RDEF_SN_3_GRID_TRANSFORM" in resolved,
            "NextAction": "build likelihood-native L_SN after RDEF_SN_1 and RDEF_SN_2 are frozen",
        },
        {
            "ContractID": "RDEF_BAO_1_OBSERVABLE",
            "Source": "DESI DR2 BAO",
            "ResidualObject": "r_BAO",
            "DefinitionStatus": "PREFLIGHT_EXISTS_NOT_MEASUREMENT_FROZEN",
            "CurrentDefinition": "log(observed / audit_flat_LCDM_prediction) for DH/DM/DV over rs",
            "CurrentArtifact": "evidence/bao_residual_transform_preflight.csv",
            "ObservedRows": int(bao_dr2["Rows"]),
            "PreflightMetric": f"mean_abs_log_residual={bao_dr2['MeanAbsLogResidual']}",
            "MeasurementRequirement": "freeze BAO prediction vector and residual convention for each observable type",
            "BlockingIssue": "audit fiducial baseline is not the final likelihood-native baseline",
            "AllowedForMeasurementTransform": False,
            "ResolvedForRerunCandidate": "RDEF_BAO_1_OBSERVABLE" in resolved,
            "NextAction": "define BAO residual against the frozen external baseline before L_BAO",
        },
        {
            "ContractID": "RDEF_BAO_2_RS_POLICY",
            "Source": "DESI DR2 BAO",
            "ResidualObject": "r_d / rs policy",
            "DefinitionStatus": "PREFLIGHT_BASELINE_EXISTS_NOT_MEASUREMENT_FROZEN",
            "CurrentDefinition": f"audit baseline rd={bao_dr2['BaselineRdMpc']}",
            "CurrentArtifact": "evidence/bao_residual_transform_summary.csv",
            "ObservedRows": int(bao_dr2["Rows"]),
            "PreflightMetric": f"H0={bao_dr2['BaselineH0']};OmegaM={bao_dr2['BaselineOmegaM']}",
            "MeasurementRequirement": "predeclare whether r_d is CMB-fixed, BAO-likelihood fitted, or externally marginalized",
            "BlockingIssue": "sound-horizon/baseline policy affects BAO residual amplitude",
            "AllowedForMeasurementTransform": False,
            "ResolvedForRerunCandidate": "RDEF_BAO_2_RS_POLICY" in resolved,
            "NextAction": "lock r_d/baseline policy before rerunning K1 and A2",
        },
        {
            "ContractID": "RDEF_BAO_3_GRID_TRANSFORM",
            "Source": "DESI DR2 BAO",
            "ResidualObject": "L_BAO",
            "DefinitionStatus": "ANCHOR_PREFLIGHT_EXISTS_NOT_MEASUREMENT_FROZEN",
            "CurrentDefinition": "nearest/anchor mapping into source-split grid",
            "CurrentArtifact": "data/transforms/k2_a2_l_bao_transform_v1.csv",
            "ObservedRows": int(bao_dr2["Rows"]),
            "PreflightMetric": f"median_sigma={bao_dr2['MedianSigmaDiag']}",
            "MeasurementRequirement": "construct L_BAO from observable-level BAO residuals without post-hoc nearest-anchor choices",
            "BlockingIssue": "current BAO transform is not a final likelihood-native source-split transform",
            "AllowedForMeasurementTransform": False,
            "ResolvedForRerunCandidate": "RDEF_BAO_3_GRID_TRANSFORM" in resolved,
            "NextAction": "build likelihood-native L_BAO after RDEF_BAO_1 and RDEF_BAO_2 are frozen",
        },
    ]

    contract = pd.DataFrame(rows)
    contract["ClaimBoundary"] = "likelihood_native_residual_definition_no_measurement_validation"
    contract.to_csv(OUT_CONTRACT, index=False)

    measurement_ready = int(contract["AllowedForMeasurementTransform"].map(truthy).sum())
    rerun_ready = int(contract["ResolvedForRerunCandidate"].map(truthy).sum())
    summary = pd.DataFrame(
        [
            {
                "ContractID": "LIKELIHOOD_NATIVE_RESIDUAL_DEFINITION_CONTRACT_V1",
                "ResidualContracts": len(contract),
                "PublicInputObjectsPreflightUsable": inputs["PreflightUsableObjects"],
                "MeasurementReadyResidualContracts": measurement_ready,
                "ResolvedForRerunCandidateContracts": rerun_ready,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "RESIDUAL_DEFINITIONS_RESOLVED_FOR_RERUN_MEASUREMENT_BLOCKED"
                    if rerun_ready == len(contract)
                    else "RESIDUAL_DEFINITIONS_CONTRACTED_MEASUREMENT_BLOCKED"
                ),
                "StrongestAllowedClaim": "SN and BAO residual routes have explicit preflight definitions and measurement blockers",
                "PrimaryBlocker": (
                    "residual policies are ready for a locked rerun candidate, but measurement validation still requires final joint covariance adjudication"
                    if rerun_ready == len(contract)
                    else "SN nuisance/offset policy and BAO baseline/r_d policy are not measurement-frozen"
                ),
                "BlockingContracts": ";".join(
                    contract.loc[~contract["ResolvedForRerunCandidate"].map(truthy), "ContractID"]
                ),
                "NextAction": (
                    "build candidate y_split and C_split using frozen residual policies, then rerun locked A2 unchanged"
                    if rerun_ready == len(contract)
                    else "choose SN nuisance treatment and BAO baseline/r_d policy, then build likelihood-native L_SN/L_BAO"
                ),
                "ClaimBoundary": "likelihood_native_residual_definition_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_READINESS, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Likelihood-Native Residual Definition Contract",
        "",
        "Status: residual definitions are explicit for preflight, but not measurement-frozen.",
        "",
        "## Summary",
        "",
        f"- Residual contracts: {len(contract)}",
        f"- Measurement-ready residual contracts: {measurement_ready}/{len(contract)}",
        f"- Resolved for locked rerun candidate: {rerun_ready}/{len(contract)}",
        "- Measurement validation allowed: False",
        "",
        "## Contracts",
        "",
    ]
    for _, row in contract.iterrows():
        lines.extend(
            [
                f"### {row['ContractID']}",
                "",
                f"- Source: {row['Source']}",
                f"- Object: `{row['ResidualObject']}`",
                f"- Current definition: {row['CurrentDefinition']}",
                f"- Measurement requirement: {row['MeasurementRequirement']}",
                f"- Blocking issue: {row['BlockingIssue']}",
                f"- Next action: {row['NextAction']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "This contract defines what must be frozen before measurement scoring. It does not alter A2 and does not score a new result.",
            "",
        ]
    )
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_CONTRACT}")
    print(f"Wrote {OUT_READINESS}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
