#!/usr/bin/env python3
"""Build machine-readable contract for the A2 full source-split transform."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "k2_a2_likelihood_native_transform_contract.csv"
READINESS = ROOT / "evidence" / "k2_a2_likelihood_native_transform_contract_readiness.csv"


def main() -> None:
    rows = [
        {
            "ComponentID": "LNTR_SN_VECTOR",
            "ComponentClass": "input_transform",
            "RequiredObject": "r_SN",
            "MathematicalRole": "Pantheon+ residual vector under frozen nuisance/baseline policy",
            "CurrentArtifact": "data/public_ingest/pantheon_plus/Pantheon_SH0ES.dat",
            "CurrentStatus": "INPUT_AVAILABLE_TRANSFORM_NOT_FROZEN",
            "AllowedForScoring": False,
            "BlockingIssue": "sn_residual_nuisance_centering_and_transform_matrix_not_frozen",
            "NextAction": "freeze SN residual definition, nuisance treatment, centering rule, and L_SN matrix",
            "ClaimBoundary": "a2_likelihood_native_transform_contract_no_measurement_validation",
        },
        {
            "ComponentID": "LNTR_BAO_VECTOR",
            "ComponentClass": "input_transform",
            "RequiredObject": "r_BAO",
            "MathematicalRole": "DESI DR2 BAO residual vector under frozen baseline policy",
            "CurrentArtifact": "data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt",
            "CurrentStatus": "INPUT_AVAILABLE_TRANSFORM_NOT_FROZEN",
            "AllowedForScoring": False,
            "BlockingIssue": "bao_observable_prediction_anchor_and_transform_matrix_not_frozen",
            "NextAction": "freeze BAO residual definition, observable prediction vector, and L_BAO matrix",
            "ClaimBoundary": "a2_likelihood_native_transform_contract_no_measurement_validation",
        },
        {
            "ComponentID": "LNTR_SOURCE_SPLIT_VECTOR",
            "ComponentClass": "joint_transform",
            "RequiredObject": "y_split = L_SN*r_SN - L_BAO*r_BAO",
            "MathematicalRole": "shared source-split diagnostic vector for A2 scoring",
            "CurrentArtifact": "evidence/source_split_coordinate_native_target.csv",
            "CurrentStatus": "PREFLIGHT_VECTOR_AVAILABLE_NOT_FULL_LIKELIHOOD_NATIVE",
            "AllowedForScoring": False,
            "BlockingIssue": "joint_likelihood_native_vector_not_frozen",
            "NextAction": "construct y_split only after L_SN and L_BAO are frozen independently",
            "ClaimBoundary": "a2_likelihood_native_transform_contract_no_measurement_validation",
        },
        {
            "ComponentID": "LNTR_COVARIANCE",
            "ComponentClass": "joint_covariance",
            "RequiredObject": "C_split = L_SN*C_SN*L_SN^T + L_BAO*C_BAO*L_BAO^T - C_cross - C_cross^T",
            "MathematicalRole": "full covariance in source-split space",
            "CurrentArtifact": "evidence/source_split_likelihood_native_public_covariance_proxy.csv",
            "CurrentStatus": "PUBLIC_PROXY_AVAILABLE_NOT_FULL_LIKELIHOOD_NATIVE",
            "AllowedForScoring": False,
            "BlockingIssue": "sn_bao_cross_covariance_policy_missing",
            "NextAction": "freeze zero/shrinkage/public cross-covariance policy before rerun",
            "ClaimBoundary": "a2_likelihood_native_transform_contract_no_measurement_validation",
        },
        {
            "ComponentID": "LNTR_K1_BASELINE",
            "ComponentClass": "baseline",
            "RequiredObject": "K1_split",
            "MathematicalRole": "no-memory baseline in the same source-split vector space",
            "CurrentArtifact": "data/k1/source_split_external_k1_response.csv",
            "CurrentStatus": "PREFLIGHT_BASELINE_AVAILABLE_NOT_FULL_LIKELIHOOD_NATIVE",
            "AllowedForScoring": False,
            "BlockingIssue": "likelihood_native_k1_baseline_not_promoted",
            "NextAction": "freeze K1/no-memory baseline under the same transform and covariance policy",
            "ClaimBoundary": "a2_likelihood_native_transform_contract_no_measurement_validation",
        },
        {
            "ComponentID": "LNTR_A2_PREDICTION",
            "ComponentClass": "locked_prediction",
            "RequiredObject": "K2_SOURCE_SPLIT_A2_PRIOR_V1",
            "MathematicalRole": "frozen A2 prediction applied without kernel/gain changes",
            "CurrentArtifact": "data/predictions/k2_source_split_a2_prior_v1.csv",
            "CurrentStatus": "LOCKED",
            "AllowedForScoring": True,
            "BlockingIssue": "",
            "NextAction": "do not modify; wait for transform/covariance/K1/null gates",
            "ClaimBoundary": "a2_likelihood_native_transform_contract_no_measurement_validation",
        },
        {
            "ComponentID": "LNTR_NULL_POLICY",
            "ComponentClass": "null_comparators",
            "RequiredObject": "frozen null comparator set",
            "MathematicalRole": "controls scored under same transform/covariance policy",
            "CurrentArtifact": "evidence/null_model_registry.csv",
            "CurrentStatus": "MVP_NULLS_AVAILABLE_FULL_GATE_POLICY_NOT_FROZEN",
            "AllowedForScoring": False,
            "BlockingIssue": "full_gate_null_policy_not_frozen",
            "NextAction": "freeze K1, polynomial, sign-randomized, coordinate-remap, optical/backreaction policies",
            "ClaimBoundary": "a2_likelihood_native_transform_contract_no_measurement_validation",
        },
    ]
    contract = pd.DataFrame(rows)
    contract.to_csv(OUT, index=False)

    required = contract[contract["ComponentID"].ne("LNTR_A2_PREDICTION")]
    ready = bool(contract["AllowedForScoring"].all())
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "K2_A2_LIKELIHOOD_NATIVE_TRANSFORM_CONTRACT",
                "Rows": len(contract),
                "LockedA2Ready": bool(contract.loc[contract["ComponentID"].eq("LNTR_A2_PREDICTION"), "AllowedForScoring"].iloc[0]),
                "RequiredNonA2ComponentsReady": bool(required["AllowedForScoring"].all()),
                "AllowedForFullGateScorecard": ready,
                "BlockingComponents": ";".join(contract.loc[~contract["AllowedForScoring"], "ComponentID"]),
                "CurrentStatus": "CONTRACT_DEFINED_FULL_GATE_BLOCKED",
                "PrimaryNextAction": "freeze L_SN, L_BAO, C_split cross-covariance policy, K1 baseline, and null policy",
                "ClaimBoundary": "a2_likelihood_native_transform_contract_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(READINESS, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {READINESS}")


if __name__ == "__main__":
    main()
