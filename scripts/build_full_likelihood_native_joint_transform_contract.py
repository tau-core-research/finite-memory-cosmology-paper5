#!/usr/bin/env python3
"""Build the full likelihood-native joint transform contract for A2.

This contract describes what must be true before the locked A2 prediction can
be scored as a measurement-grade SN+BAO result. It deliberately keeps the
current route at preflight status.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"
DOCS = ROOT / "docs"

EXISTING_CONTRACT = EVIDENCE / "k2_a2_likelihood_native_transform_contract.csv"
CROSS_POLICY = EVIDENCE / "k2_a2_cross_covariance_policy_readiness_v1.csv"
NULL_POLICY = EVIDENCE / "k2_a2_full_gate_null_policy_readiness_v1.csv"
JOINT_ADJUDICATION = EVIDENCE / "joint_covariance_adjudication_summary.csv"
PUBLIC_COV = EVIDENCE / "full_public_covariance_transform_summary.csv"
INPUT_OBJECTS = EVIDENCE / "likelihood_native_input_object_summary.csv"
RESIDUAL_CONTRACT = EVIDENCE / "likelihood_native_residual_definition_readiness.csv"
RERUN_CANDIDATE = EVIDENCE / "likelihood_native_rerun_candidate_summary.csv"

OUT_CONTRACT = EVIDENCE / "full_likelihood_native_joint_transform_contract.csv"
OUT_READINESS = EVIDENCE / "full_likelihood_native_joint_transform_readiness.csv"
OUT_DOC = DOCS / "full_likelihood_native_joint_transform_contract.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty input: {path}")
    return df.iloc[0]


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def main() -> None:
    old_contract = pd.read_csv(EXISTING_CONTRACT)
    cross = first(CROSS_POLICY)
    nulls = first(NULL_POLICY)
    adjudication = first(JOINT_ADJUDICATION)
    public_cov = first(PUBLIC_COV)
    input_objects = first(INPUT_OBJECTS)
    residual_contract = first(RESIDUAL_CONTRACT)
    rerun_candidate = first(RERUN_CANDIDATE) if RERUN_CANDIDATE.exists() else None
    residual_rerun_ready = int(residual_contract.get("ResolvedForRerunCandidateContracts", 0))
    residual_total = int(residual_contract.get("ResidualContracts", 0))

    rows = [
        {
            "RequirementID": "FLN_1_SN_RESIDUAL_DEFINITION",
            "RequirementClass": "sn_likelihood_transform",
            "RequiredObject": "r_SN(theta_SN,nuisance)",
            "CurrentArtifact": "data/public_ingest/pantheon_plus/Pantheon_SH0ES.dat",
            "InputAvailable": exists("data/public_ingest/pantheon_plus/Pantheon_SH0ES.dat"),
            "PreflightSatisfied": True,
            "MeasurementSatisfied": False,
            "BlockingIssue": "SN nuisance centering and likelihood-native residual transform are not frozen",
            "AcceptanceCriterion": "SN residual vector and L_SN are derived from the public likelihood definition, including nuisance/marginalization policy",
            "NextAction": "freeze SN residual definition and transform before rerunning locked A2",
        },
        {
            "RequirementID": "FLN_2_BAO_RESIDUAL_DEFINITION",
            "RequirementClass": "bao_likelihood_transform",
            "RequiredObject": "r_BAO(theta_BAO)",
            "CurrentArtifact": "data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt",
            "InputAvailable": exists("data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt"),
            "PreflightSatisfied": True,
            "MeasurementSatisfied": False,
            "BlockingIssue": "BAO observable prediction and anchor policy are not likelihood-native frozen",
            "AcceptanceCriterion": "BAO residual vector and L_BAO are derived from the public BAO likelihood observable vector without nearest-anchor choices",
            "NextAction": "freeze BAO observable prediction vector and transform before rerunning locked A2",
        },
        {
            "RequirementID": "FLN_3_SOURCE_SPLIT_VECTOR",
            "RequirementClass": "joint_target",
            "RequiredObject": "y_split = L_SN*r_SN - L_BAO*r_BAO",
            "CurrentArtifact": "evidence/source_split_coordinate_native_target.csv",
            "InputAvailable": exists("evidence/source_split_coordinate_native_target.csv"),
            "PreflightSatisfied": True,
            "MeasurementSatisfied": False,
            "BlockingIssue": "source-split target is preflight/coordinate-native, not likelihood-native",
            "AcceptanceCriterion": "y_split is regenerated from frozen SN and BAO likelihood-native transforms only",
            "NextAction": "rebuild y_split after FLN_1 and FLN_2 are satisfied",
        },
        {
            "RequirementID": "FLN_4_JOINT_COVARIANCE",
            "RequirementClass": "joint_covariance",
            "RequiredObject": "C_split = L_SN C_SN L_SN^T + L_BAO C_BAO L_BAO^T - C_cross - C_cross^T",
            "CurrentArtifact": "evidence/joint_covariance_adjudication_summary.csv",
            "InputAvailable": True,
            "PreflightSatisfied": str(adjudication["CurrentStatus"]) == "FG4_EXECUTABLE_PREFLIGHT_MEASUREMENT_BLOCKED",
            "MeasurementSatisfied": False,
            "BlockingIssue": str(adjudication["PrimaryBlocker"]),
            "AcceptanceCriterion": "single declared covariance route scores A2, K1, polynomial, physical, sign, and coordinate controls without route switching",
            "NextAction": str(adjudication["NextAction"]),
        },
        {
            "RequirementID": "FLN_5_CROSS_COVARIANCE_POLICY",
            "RequirementClass": "cross_covariance",
            "RequiredObject": "C_cross policy",
            "CurrentArtifact": "evidence/k2_a2_cross_covariance_policy_v1.csv",
            "InputAvailable": exists("evidence/k2_a2_cross_covariance_policy_v1.csv"),
            "PreflightSatisfied": truthy(cross["PolicyFrozenForPreflight"]),
            "MeasurementSatisfied": False,
            "BlockingIssue": "preflight cross-covariance policy exists but is not a public full likelihood cross-covariance",
            "AcceptanceCriterion": "cross-covariance policy is either public-likelihood derived or explicitly justified as zero with sensitivity retained",
            "NextAction": "promote cross-covariance policy only after likelihood-native route is frozen",
        },
        {
            "RequirementID": "FLN_6_K1_BASELINE",
            "RequirementClass": "baseline",
            "RequiredObject": "K1_split",
            "CurrentArtifact": "data/k1/source_split_external_k1_response.csv",
            "InputAvailable": exists("data/k1/source_split_external_k1_response.csv"),
            "PreflightSatisfied": True,
            "MeasurementSatisfied": False,
            "BlockingIssue": "K1 is available as preflight export, not final likelihood-native baseline under the final covariance route",
            "AcceptanceCriterion": "K1 is exported under the final frozen transform/covariance policy with no same-data amplitude fit",
            "NextAction": "rerun K1 export after FLN_1 through FLN_5 are satisfied",
        },
        {
            "RequirementID": "FLN_7_NULL_POLICY",
            "RequirementClass": "null_comparators",
            "RequiredObject": "final comparator set",
            "CurrentArtifact": "evidence/k2_a2_full_gate_null_policy_v1.csv",
            "InputAvailable": exists("evidence/k2_a2_full_gate_null_policy_v1.csv"),
            "PreflightSatisfied": truthy(nulls["FullGateNullPolicyFrozen"]),
            "MeasurementSatisfied": False,
            "BlockingIssue": "null policy is frozen for preflight, but must be rerun under the final likelihood-native route",
            "AcceptanceCriterion": "K1, polynomial, physical, sign-randomized, and coordinate controls are scored under identical final covariance/transform policy",
            "NextAction": "reuse the frozen null registry after the final route is built; do not add post-hoc controls",
        },
        {
            "RequirementID": "FLN_8_LOCKED_A2",
            "RequirementClass": "locked_prediction",
            "RequiredObject": "K2_A2 = 2*K1*(1+4*x^3)",
            "CurrentArtifact": "data/predictions/k2_source_split_a2_prior_v1.csv",
            "InputAvailable": exists("data/predictions/k2_source_split_a2_prior_v1.csv"),
            "PreflightSatisfied": True,
            "MeasurementSatisfied": True,
            "BlockingIssue": "",
            "AcceptanceCriterion": "locked A2 remains unchanged: p=3, rho=4, A_tau=2, no K1 refit",
            "NextAction": "do not modify A2; rerun unchanged once the measurement route exists",
        },
    ]

    contract = pd.DataFrame(rows)
    contract["AllowedForMeasurementScoring"] = contract["MeasurementSatisfied"].map(truthy)
    contract["ClaimBoundary"] = "full_likelihood_native_joint_transform_no_measurement_validation"
    contract.to_csv(OUT_CONTRACT, index=False)

    blocking = contract[~contract["MeasurementSatisfied"].map(truthy)]
    summary = pd.DataFrame(
        [
            {
                "ContractID": "FULL_LIKELIHOOD_NATIVE_JOINT_TRANSFORM_CONTRACT_V1",
                "Requirements": len(contract),
                "PreflightSatisfied": int(contract["PreflightSatisfied"].map(truthy).sum()),
                "MeasurementSatisfied": int(contract["MeasurementSatisfied"].map(truthy).sum()),
                "RawPublicSNCovarianceAvailable": public_cov["RawPublicSNCovarianceAvailable"],
                "RawPublicBAOCovarianceAvailable": public_cov["RawPublicBAOCovarianceAvailable"],
                "InputObjectsPreflightUsable": input_objects["PreflightUsableObjects"],
                "InputObjectsMeasurementUsable": input_objects["MeasurementUsableObjects"],
                "ResidualContracts": residual_contract["ResidualContracts"],
                "ResidualContractsMeasurementReady": residual_contract["MeasurementReadyResidualContracts"],
                "ResidualContractsResolvedForRerunCandidate": residual_rerun_ready,
                "RerunCandidateStatus": "" if rerun_candidate is None else rerun_candidate["CurrentStatus"],
                "RerunCandidateK2ImprovesOverK1": "" if rerun_candidate is None else rerun_candidate["K2ImprovesOverK1"],
                "RerunCandidateK2BeatsBestPoly": "" if rerun_candidate is None else rerun_candidate["K2BeatsBestPoly"],
                "ExistingContractRows": len(old_contract),
                "CrossCovariancePolicyFrozenForPreflight": cross["PolicyFrozenForPreflight"],
                "NullPolicyFrozenForPreflight": nulls["FullGateNullPolicyFrozen"],
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "FULL_LIKELIHOOD_NATIVE_RERUN_ROUTE_READY_MEASUREMENT_BLOCKED"
                    if residual_total > 0 and residual_rerun_ready == residual_total
                    else "FULL_LIKELIHOOD_NATIVE_ROUTE_CONTRACTED_MEASUREMENT_BLOCKED"
                ),
                "StrongestAllowedClaim": "raw public covariance inputs and a locked A2 preflight route exist, but likelihood-native measurement scoring remains blocked",
                "BlockingRequirements": ";".join(blocking["RequirementID"].astype(str)),
                "PrimaryBlocker": (
                    "residual route is ready for locked rerun candidate; first candidate rerun is mixed/weakening and measurement remains blocked by joint covariance/K1/null adjudication"
                    if rerun_candidate is not None
                    and str(rerun_candidate["CurrentStatus"]) == "LOCKED_A2_RERUN_CANDIDATE_MIXED_OR_WEAKENING"
                    else "residual route is ready for locked rerun candidate; measurement remains blocked by joint covariance/K1/null adjudication"
                    if residual_total > 0 and residual_rerun_ready == residual_total
                    else "SN nuisance/offset policy, BAO baseline/r_d policy, and final joint covariance/K1/null rerun are not frozen"
                ),
                "NextAction": (
                    "build candidate y_split and C_split, then rerun K1/null/A2 scorecard unchanged"
                    if residual_total > 0 and residual_rerun_ready == residual_total
                    else "freeze residual-definition policies first, then build L_SN/L_BAO, y_split, C_split, K1, and null scorecard with locked A2 unchanged"
                ),
                "ClaimBoundary": "full_likelihood_native_joint_transform_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_READINESS, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Full Likelihood-Native Joint Transform Contract",
        "",
        "Status: measurement route contracted, not open.",
        "",
        "## Summary",
        "",
        f"- Requirements: {len(contract)}",
        f"- Preflight satisfied: {int(contract['PreflightSatisfied'].map(truthy).sum())}/{len(contract)}",
        f"- Measurement satisfied: {int(contract['MeasurementSatisfied'].map(truthy).sum())}/{len(contract)}",
        "- Measurement validation allowed: False",
        "- Locked A2 changes allowed: False",
        "",
        "## Required Route",
        "",
        "The measurement route must use the same likelihood-native SN transform, BAO transform, joint covariance, K1 baseline, and null policy for every scored model.",
        "The locked A2 prediction is rerun unchanged after those objects are frozen.",
        "",
        "## Requirements",
        "",
    ]
    for _, row in contract.iterrows():
        lines.extend(
            [
                f"### {row['RequirementID']}",
                "",
                f"- Class: {row['RequirementClass']}",
                f"- Required object: `{row['RequiredObject']}`",
                f"- Preflight satisfied: {row['PreflightSatisfied']}",
                f"- Measurement satisfied: {row['MeasurementSatisfied']}",
                f"- Blocking issue: {row['BlockingIssue'] if row['BlockingIssue'] else 'none'}",
                f"- Acceptance criterion: {row['AcceptanceCriterion']}",
                f"- Next action: {row['NextAction']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "This contract does not claim measurement validation. It defines the route required before measurement scoring can be considered.",
            "",
        ]
    )
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_CONTRACT}")
    print(f"Wrote {OUT_READINESS}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
