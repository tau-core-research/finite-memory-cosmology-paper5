#!/usr/bin/env python3
"""Check readiness for the SN+BAO/source-split benchmark branch."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "source_split_readiness.csv"


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def main() -> None:
    public_inputs = pd.read_csv(EVIDENCE / "public_input_inventory.csv")
    diagnostic = pd.read_csv(EVIDENCE / "diagnostic_point_audit.csv")
    null_registry = pd.read_csv(EVIDENCE / "null_model_registry.csv")
    k1_audit = pd.read_csv(EVIDENCE / "k1_baseline_provenance_audit.csv")
    k1_target_path = EVIDENCE / "source_split_k1_target_readiness.csv"
    k1_target = pd.read_csv(k1_target_path) if k1_target_path.exists() else pd.DataFrame()
    covariance_path = EVIDENCE / "source_split_covariance_readiness.csv"
    covariance = pd.read_csv(covariance_path) if covariance_path.exists() else pd.DataFrame()
    sign_family_path = EVIDENCE / "sign_family_export_readiness.csv"
    sign_family = pd.read_csv(sign_family_path) if sign_family_path.exists() else pd.DataFrame()

    product_ids = set(public_inputs["ProductID"].astype(str))
    has_sn = "PANTHEON_PLUS_SH0ES_SN" in product_ids
    has_bao = "DESI_DR2_BAO_ALL_GAUSSIAN" in product_ids
    sign_columns = {"all_sign", "no_degree4_sign", "degree2_sign", "sign_stable"}
    has_sign_family = sign_columns.issubset(set(diagnostic.columns))
    sign_stable_count = int(diagnostic["sign_stable"].astype(str).str.lower().eq("true").sum())
    sign_unstable_count = int(len(diagnostic) - sign_stable_count)
    has_fair_nulls = null_registry["NullCategory"].astype(str).eq("fair_null").any()
    has_coordinate_native_k1 = (
        k1_audit.loc[k1_audit["BaselineID"].eq("K1_COORDINATE_NATIVE_TARGET"), "UsedInBenchmark"]
        .astype(str)
        .str.lower()
        .eq("true")
        .any()
    )
    has_likelihood_native_k1 = (
        k1_audit.loc[k1_audit["BaselineID"].eq("K1_LIKELIHOOD_NATIVE_TARGET"), "UsedInBenchmark"]
        .astype(str)
        .str.lower()
        .eq("true")
        .any()
    )
    has_source_split_k1 = (
        not k1_target.empty
        and k1_target["AllowedForK2Scoring"].astype(str).str.lower().eq("true").any()
    )
    has_source_split_k1_control = (
        not k1_target.empty
        and k1_target["TargetID"].astype(str).eq("SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET").any()
        and k1_target.loc[
            k1_target["TargetID"].astype(str).eq("SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET"),
            "Status",
        ]
        .astype(str)
        .str.lower()
        .eq("available")
        .any()
    )
    has_source_split_covariance = (
        not covariance.empty
        and covariance["AllowedForK2Scoring"].astype(str).str.lower().eq("true").any()
    )
    has_source_split_covariance_policy = (
        not covariance.empty
        and covariance["CovarianceID"].astype(str).eq("SSCOV_SHRINKAGE_SOURCE_SPLIT").any()
        and covariance.loc[
            covariance["CovarianceID"].astype(str).eq("SSCOV_SHRINKAGE_SOURCE_SPLIT"),
            "Status",
        ]
        .astype(str)
        .str.lower()
        .eq("available")
        .any()
    )
    has_public_sign_family = (
        not sign_family.empty
        and sign_family["AllowedForK2Scoring"].astype(str).str.lower().eq("true").any()
    )
    has_public_sign_family_preflight = (
        not sign_family.empty
        and sign_family["SignFamilyID"].astype(str).eq("SF_PUBLIC_SOURCE_SPLIT_FAMILIES").any()
        and sign_family.loc[
            sign_family["SignFamilyID"].astype(str).eq("SF_PUBLIC_SOURCE_SPLIT_FAMILIES"),
            "Status",
        ]
        .astype(str)
        .str.lower()
        .eq("available")
        .any()
    )

    checks = [
        {
            "CheckID": "SS1_PUBLIC_SN_INPUT",
            "Requirement": "Public SN data vector and covariance available",
            "Available": has_sn,
            "Evidence": "PANTHEON_PLUS_SH0ES_SN" if has_sn else "missing",
            "BlockingIssue": "" if has_sn else "missing_public_sn_input",
            "NextAction": "Use only after a source-split diagnostic transform is registered.",
        },
        {
            "CheckID": "SS2_PUBLIC_BAO_INPUT",
            "Requirement": "Public BAO data vector and covariance available",
            "Available": has_bao,
            "Evidence": "DESI_DR2_BAO_ALL_GAUSSIAN" if has_bao else "missing",
            "BlockingIssue": "" if has_bao else "missing_public_bao_input",
            "NextAction": "Use as BAO anchor/control, not as a same-data amplitude calibrator.",
        },
        {
            "CheckID": "SS3_SIGN_FAMILY_PACKET",
            "Requirement": "Current diagnostic packet contains sign-family splits",
            "Available": has_sign_family,
            "Evidence": f"sign_stable={sign_stable_count}; sign_unstable={sign_unstable_count}",
            "BlockingIssue": "" if has_sign_family else "missing_sign_family_columns",
            "NextAction": "Export the same sign-family logic from public reconstruction families.",
        },
        {
            "CheckID": "SS4_NULL_COMPARATORS",
            "Requirement": "Fair null comparators are registered",
            "Available": has_fair_nulls,
            "Evidence": ";".join(null_registry["NullID"].astype(str).tolist()),
            "BlockingIssue": "" if has_fair_nulls else "missing_fair_nulls",
            "NextAction": "Implement source-split versions of no-memory, optical, and backreaction controls.",
        },
        {
            "CheckID": "SS5_COORDINATE_NATIVE_K1",
            "Requirement": "Coordinate-native K1/no-memory target selected",
            "Available": has_coordinate_native_k1 or has_source_split_k1,
            "Evidence": "source_split_k1_target_readiness.csv",
            "BlockingIssue": ""
            if (has_coordinate_native_k1 or has_source_split_k1)
            else "k1_control_exported_not_scoring_target"
            if has_source_split_k1_control
            else "coordinate_native_k1_unavailable",
            "NextAction": "Use exported K1 control only after joint covariance and public sign-family exist."
            if has_source_split_k1_control and not (has_coordinate_native_k1 or has_source_split_k1)
            else "Build a coordinate-native K1 target before K2 measurement scoring.",
        },
        {
            "CheckID": "SS6_LIKELIHOOD_NATIVE_K1",
            "Requirement": "Likelihood-native K1/no-memory target selected",
            "Available": has_likelihood_native_k1,
            "Evidence": "K1_LIKELIHOOD_NATIVE_TARGET",
            "BlockingIssue": "" if has_likelihood_native_k1 else "likelihood_native_k1_unavailable",
            "NextAction": "Keep as Phase II target if coordinate-native export is not enough.",
        },
        {
            "CheckID": "SS7_JOINT_COVARIANCE",
            "Requirement": "Source-split joint covariance selected",
            "Available": has_source_split_covariance,
            "Evidence": "source_split_covariance_readiness.csv",
            "BlockingIssue": ""
            if has_source_split_covariance
            else "covariance_policy_exported_not_scoring_covariance"
            if has_source_split_covariance_policy
            else "joint_covariance_unavailable",
            "NextAction": "Use exported shrinkage policy only after public sign-family exists; replace with public full covariance when available."
            if has_source_split_covariance_policy and not has_source_split_covariance
            else "Select public joint covariance or declared shrinkage covariance before K2 scoring.",
        },
        {
            "CheckID": "SS8_PUBLIC_SIGN_FAMILY",
            "Requirement": "Public source-split sign-family export selected",
            "Available": has_public_sign_family,
            "Evidence": "sign_family_export_readiness.csv",
            "BlockingIssue": ""
            if has_public_sign_family
            else "branch_sign_family_exported_not_reconstruction_family"
            if has_public_sign_family_preflight
            else "public_sign_family_unavailable",
            "NextAction": "Replace branch-sign preflight with public reconstruction-family export before K2 scoring."
            if has_public_sign_family_preflight and not has_public_sign_family
            else "Export sign-family table from public source-split reconstruction families before K2 scoring.",
        },
        {
            "CheckID": "SS9_SCORING_AUTHORIZATION",
            "Requirement": "Source-split K2 measurement scoring authorized",
            "Available": has_sn
            and has_bao
            and has_sign_family
            and has_fair_nulls
            and (has_coordinate_native_k1 or has_source_split_k1)
            and has_source_split_covariance
            and has_public_sign_family,
            "Evidence": "requires SS1-SS5 and SS7-SS8 true",
            "BlockingIssue": ""
            if has_sn
            and has_bao
            and has_sign_family
            and has_fair_nulls
            and (has_coordinate_native_k1 or has_source_split_k1)
            and has_source_split_covariance
            and has_public_sign_family
            else "source_split_k2_scoring_not_ready",
            "NextAction": "Start with transform/export work, not K2 scoring.",
        },
    ]

    for row in checks:
        row["Available"] = bool_text(bool(row["Available"]))

    pd.DataFrame(checks).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
