#!/usr/bin/env python3
"""Build a concrete plan/readiness gate for likelihood-native source-split K1."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
PLAN_OUT = EVIDENCE / "source_split_likelihood_native_k1_plan.csv"
READINESS_OUT = EVIDENCE / "source_split_likelihood_native_k1_readiness.csv"
SPEC = ROOT / "docs" / "source_split_likelihood_native_k1_spec.md"
PARAMETERS = ROOT / "data" / "k1" / "source_split_likelihood_native_parameters.yaml"
BASELINE_PREDICTION = ROOT / "data" / "k1" / "source_split_likelihood_native_baseline_prediction.csv"
COORDINATE_MAP = ROOT / "data" / "k1" / "source_split_likelihood_native_coordinate_map.csv"
PROMOTION_SUMMARY = EVIDENCE / "source_split_likelihood_native_k1_promotion_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def promotion_gate_allows_primary_k1() -> bool:
    """Return whether the newer promotion gate has cleared primary K1 export."""
    if not PROMOTION_SUMMARY.exists():
        return False
    summary = pd.read_csv(PROMOTION_SUMMARY)
    if summary.empty or "PrimaryK1PromotionAllowed" not in summary.columns:
        return False
    return bool(summary["PrimaryK1PromotionAllowed"].map(truthy).all())


def plan_rows() -> list[dict[str, object]]:
    return [
        {
            "ArtifactID": "LNK1_PUBLIC_SN_INPUT",
            "ArtifactClass": "public_input",
            "Required": True,
            "CurrentStatus": "available",
            "ArtifactPath": "data/public_ingest/pantheon_plus/Pantheon_SH0ES.dat",
            "HasData": True,
            "HasCovariance": True,
            "AllowedForK1Export": True,
            "BlockingIssue": "",
            "NextAction": "Use as SN side of the joint likelihood-native baseline.",
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
        {
            "ArtifactID": "LNK1_PUBLIC_BAO_INPUT",
            "ArtifactClass": "public_input",
            "Required": True,
            "CurrentStatus": "available",
            "ArtifactPath": "data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt",
            "HasData": True,
            "HasCovariance": True,
            "AllowedForK1Export": True,
            "BlockingIssue": "",
            "NextAction": "Use as BAO side of the joint likelihood-native baseline.",
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
        {
            "ArtifactID": "LNK1_JOINT_LIKELIHOOD_SPEC",
            "ArtifactClass": "likelihood_definition",
            "Required": True,
            "CurrentStatus": "available" if SPEC.exists() else "missing",
            "ArtifactPath": "docs/source_split_likelihood_native_k1_spec.md",
            "HasData": SPEC.exists(),
            "HasCovariance": False,
            "AllowedForK1Export": SPEC.exists(),
            "BlockingIssue": "" if SPEC.exists() else "joint_likelihood_spec_missing",
            "NextAction": (
                "Use this spec to create the frozen parameter source and baseline prediction vector."
                if SPEC.exists()
                else "Define the joint SN+BAO likelihood vector, parameters, nuisance treatment, and no-memory baseline model."
            ),
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
        {
            "ArtifactID": "LNK1_FROZEN_PARAMETER_SOURCE",
            "ArtifactClass": "baseline_parameter_source",
            "Required": True,
            "CurrentStatus": "available" if PARAMETERS.exists() else "missing",
            "ArtifactPath": "data/k1/source_split_likelihood_native_parameters.yaml",
            "HasData": PARAMETERS.exists(),
            "HasCovariance": False,
            "AllowedForK1Export": PARAMETERS.exists(),
            "BlockingIssue": "" if PARAMETERS.exists() else "frozen_joint_parameter_source_missing",
            "NextAction": (
                "Use the frozen CMB-only parameter source to evaluate the baseline prediction vector and coordinate map."
                if PARAMETERS.exists()
                else "Export frozen no-memory baseline parameters from a public chain, independent baseline, or predeclared evaluator."
            ),
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
        {
            "ArtifactID": "LNK1_BASELINE_PREDICTION_VECTOR",
            "ArtifactClass": "baseline_prediction",
            "Required": True,
            "CurrentStatus": "preflight_available_not_primary" if BASELINE_PREDICTION.exists() else "missing",
            "ArtifactPath": "data/k1/source_split_likelihood_native_baseline_prediction.csv",
            "HasData": BASELINE_PREDICTION.exists(),
            "HasCovariance": False,
            "AllowedForK1Export": False,
            "BlockingIssue": (
                "baseline_prediction_preflight_not_likelihood_native"
                if BASELINE_PREDICTION.exists()
                else "baseline_prediction_vector_missing"
            ),
            "NextAction": (
                "Promote SN nuisance handling and covariance policy before using this as primary K1."
                if BASELINE_PREDICTION.exists()
                else "Evaluate the frozen no-memory baseline on the source-split target rows."
            ),
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
        {
            "ArtifactID": "LNK1_LIKELIHOOD_NATIVE_COORDINATE_MAP",
            "ArtifactClass": "coordinate_mapping",
            "Required": True,
            "CurrentStatus": "preflight_available_not_primary" if COORDINATE_MAP.exists() else "missing",
            "ArtifactPath": "data/k1/source_split_likelihood_native_coordinate_map.csv",
            "HasData": COORDINATE_MAP.exists(),
            "HasCovariance": False,
            "AllowedForK1Export": False,
            "BlockingIssue": (
                "coordinate_map_preflight_not_joint_likelihood_native"
                if COORDINATE_MAP.exists()
                else "likelihood_native_coordinate_map_missing"
            ),
            "NextAction": (
                "Promote the joint vector/covariance policy before using this map for primary K1."
                if COORDINATE_MAP.exists()
                else "Freeze the likelihood-native x coordinate used by W(x)."
            ),
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
        {
            "ArtifactID": "LNK1_JOINT_COVARIANCE",
            "ArtifactClass": "covariance",
            "Required": True,
            "CurrentStatus": "preflight_shrinkage_available",
            "ArtifactPath": "evidence/source_split_joint_covariance_policy.csv",
            "HasData": True,
            "HasCovariance": True,
            "AllowedForK1Export": False,
            "BlockingIssue": "public_full_joint_covariance_or_declared_likelihood_covariance_missing",
            "NextAction": "Replace or promote shrinkage covariance only after likelihood-native target definition is frozen.",
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
        {
            "ArtifactID": "LNK1_EXTERNAL_K1_EXPORT",
            "ArtifactClass": "k1_export",
            "Required": True,
            "CurrentStatus": "future_family_mean_candidate_available_not_likelihood_native",
            "ArtifactPath": "data/k1/source_split_external_k1_response.csv",
            "HasData": True,
            "HasCovariance": True,
            "AllowedForK1Export": False,
            "BlockingIssue": "current_export_is_family_mean_future_only_not_likelihood_native",
            "NextAction": "Generate likelihood-native K1 response export after the baseline prediction and coordinate map exist.",
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
        {
            "ArtifactID": "LNK1_NULL_COMPARATOR_SET",
            "ArtifactClass": "null_comparators",
            "Required": True,
            "CurrentStatus": "registered_not_likelihood_native_scored",
            "ArtifactPath": "evidence/null_model_registry.csv",
            "HasData": True,
            "HasCovariance": False,
            "AllowedForK1Export": False,
            "BlockingIssue": "nulls_not_scored_on_likelihood_native_vector",
            "NextAction": "Score no-memory, polynomial, backreaction, and optical nulls on the same likelihood-native vector.",
            "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
        },
    ]


def readiness(plan: pd.DataFrame) -> pd.DataFrame:
    required = plan[plan["Required"].astype(bool)]
    blockers = required[required["BlockingIssue"].astype(str).str.len() > 0]
    promotion_allowed = promotion_gate_allows_primary_k1()
    export_allowed = promotion_allowed or (
        len(blockers) == 0 and required["AllowedForK1Export"].astype(bool).all()
    )
    missing_blockers = blockers[~blockers["HasData"].astype(bool)]
    if promotion_allowed:
        preferred_next = "LIKELIHOOD_NATIVE_K1_EXPORT_READY_BY_PROMOTION_GATE"
    elif not missing_blockers.empty:
        preferred_next = str(missing_blockers["ArtifactID"].iloc[0])
    elif not blockers.empty:
        preferred_next = str(blockers["ArtifactID"].iloc[0])
    else:
        preferred_next = "LIKELIHOOD_NATIVE_K1_EXPORT_READY"
    return pd.DataFrame(
        [
            {
                "GateID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_K1_PLAN_V1",
                "RequiredArtifacts": len(required),
                "AvailableOrPreflightArtifacts": int(required["HasData"].astype(bool).sum()),
                "BlockingArtifacts": 0 if promotion_allowed else len(blockers),
                "LikelihoodNativeK1ExportAllowed": export_allowed,
                "PromotionGateReconciled": promotion_allowed,
                "PrimaryBlockingIssue": (
                    ""
                    if promotion_allowed
                    else ";".join(blockers["ArtifactID"].astype(str).tolist())
                ),
                "PreferredNextArtifact": preferred_next,
                "CurrentDecision": (
                    "likelihood_native_k1_ready_by_promotion_gate"
                    if export_allowed
                    else "likelihood_native_k1_not_ready"
                ),
                "NextAction": (
                    "Use the promoted K1 only inside preflight scorecards; do not treat as measurement validation."
                    if export_allowed
                    else "Create the preferred next blocking artifact, then rerun this readiness check."
                ),
                "ClaimBoundary": "likelihood_native_k1_plan_only_no_measurement_validation",
            }
        ]
    )


def main() -> None:
    plan = pd.DataFrame(plan_rows())
    plan.to_csv(PLAN_OUT, index=False)
    readiness(plan).to_csv(READINESS_OUT, index=False)
    print(f"Wrote {PLAN_OUT}")
    print(f"Wrote {READINESS_OUT}")


if __name__ == "__main__":
    main()
