#!/usr/bin/env python3
"""Build the A2 public-covariance replacement plan.

This is a planning artifact, not a new measurement gate. It identifies the
specific artifacts needed to replace the current calibrated preflight bridge
with one likelihood-native public covariance route while keeping locked A2
unchanged.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"
DOCS = ROOT / "docs"

FULL_PUBLIC_COV = EVIDENCE / "full_public_covariance_transform_summary.csv"
FULL_CONTRACT = EVIDENCE / "full_likelihood_native_joint_transform_readiness.csv"
JOINT_ADJUDICATION = EVIDENCE / "joint_covariance_adjudication_summary.csv"
K1_SUMMARY = EVIDENCE / "source_split_likelihood_native_baseline_prediction_summary.csv"
POLY = EVIDENCE / "k2_a2_polynomial_tension_diagnosis.csv"
INPUT_OBJECTS = EVIDENCE / "likelihood_native_input_object_summary.csv"
CROSS_POLICY = EVIDENCE / "a2_cross_covariance_policy_summary.csv"
RERUN_SUMMARY = EVIDENCE / "likelihood_native_rerun_candidate_summary.csv"
RERUN_VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
RERUN_COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"
RERUN_SCORE = EVIDENCE / "likelihood_native_rerun_candidate_scorecard.csv"

K2_FILE = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"
K1_FILE = DATA / "k1" / "source_split_external_k1_response.csv"
SN_COV = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_COV = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

OUT = EVIDENCE / "a2_public_covariance_replacement_plan.csv"
SUMMARY = EVIDENCE / "a2_public_covariance_replacement_summary.csv"
DOC = DOCS / "a2_public_covariance_replacement_plan.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def status_from(ready: bool, partial: bool = False) -> str:
    if ready:
        return "READY"
    if partial:
        return "PARTIAL"
    return "BLOCKED"


def rerun_status(ready: bool, partial: bool = False) -> str:
    if ready:
        return "RERUN_READY"
    if partial:
        return "RERUN_PARTIAL"
    return "BLOCKED"


def main() -> None:
    public_cov = first(FULL_PUBLIC_COV)
    contract = first(FULL_CONTRACT)
    adjudication = first(JOINT_ADJUDICATION)
    k1 = first(K1_SUMMARY)
    inputs = first(INPUT_OBJECTS)
    cross = first(CROSS_POLICY)
    rerun = first(RERUN_SUMMARY) if RERUN_SUMMARY.exists() else None
    poly = pd.read_csv(POLY)
    current_poly = poly[poly["DiagnosisID"].eq("CURRENT_DECISION")].iloc[0]

    raw_sn_cov = SN_COV.exists() and truthy(public_cov["RawPublicSNCovarianceAvailable"])
    raw_bao_cov = BAO_COV.exists() and truthy(public_cov["RawPublicBAOCovarianceAvailable"])
    locked_k2_ready = K2_FILE.exists()
    k1_export_exists = K1_FILE.exists()
    residuals_rerun_resolved = int(contract["ResidualContractsResolvedForRerunCandidate"]) == int(
        contract["ResidualContracts"]
    )
    rerun_vector_ready = RERUN_VECTOR.exists()
    rerun_cov_ready = RERUN_COV.exists() and rerun is not None and truthy(rerun["CovariancePositiveDefinite"])
    rerun_score_ready = RERUN_SCORE.exists() and rerun is not None

    rows = [
        {
            "ComponentID": "PCOV_01_LOCKED_A2_INPUT",
            "ComponentClass": "locked_prediction",
            "CurrentStatus": status_from(locked_k2_ready),
            "CurrentArtifact": str(K2_FILE.relative_to(ROOT)),
            "EvidenceSignal": "p=3 rho=4 A_tau=2 locked; keep unchanged",
            "BlocksMeasurement": False,
            "RequiredAction": "none; rerun unchanged under final public covariance",
            "AcceptanceCriterion": "same locked K2 vector is scored with no rho>4, no kernel change, no K1 refit",
        },
        {
            "ComponentID": "PCOV_02_PUBLIC_SN_COVARIANCE",
            "ComponentClass": "public_covariance_input",
            "CurrentStatus": status_from(raw_sn_cov),
            "CurrentArtifact": str(SN_COV.relative_to(ROOT)),
            "EvidenceSignal": f"raw SN covariance available={raw_sn_cov}",
            "BlocksMeasurement": False,
            "RequiredAction": "validate indexing against the final SN residual vector",
            "AcceptanceCriterion": "SN data vector and covariance rows/columns use the same public likelihood ordering",
        },
        {
            "ComponentID": "PCOV_03_PUBLIC_BAO_COVARIANCE",
            "ComponentClass": "public_covariance_input",
            "CurrentStatus": status_from(raw_bao_cov),
            "CurrentArtifact": str(BAO_COV.relative_to(ROOT)),
            "EvidenceSignal": f"raw BAO covariance available={raw_bao_cov}",
            "BlocksMeasurement": False,
            "RequiredAction": "validate indexing against the final BAO residual vector",
            "AcceptanceCriterion": "BAO data vector and covariance rows/columns use the same public likelihood ordering",
        },
        {
            "ComponentID": "PCOV_04_SN_RESIDUAL_POLICY",
            "ComponentClass": "likelihood_native_residual",
            "CurrentStatus": rerun_status(residuals_rerun_resolved),
            "CurrentArtifact": "evidence/likelihood_native_residual_definition_readiness.csv",
            "EvidenceSignal": f"rerun-resolved residual contracts={contract['ResidualContractsResolvedForRerunCandidate']}/{contract['ResidualContracts']}",
            "BlocksMeasurement": True,
            "RequiredAction": "freeze SN nuisance, marginalization, and residual definition used by the covariance transform",
            "AcceptanceCriterion": "SN residual vector is likelihood-native rather than binned diagnostic proxy",
        },
        {
            "ComponentID": "PCOV_05_BAO_RESIDUAL_POLICY",
            "ComponentClass": "likelihood_native_residual",
            "CurrentStatus": rerun_status(residuals_rerun_resolved),
            "CurrentArtifact": "evidence/likelihood_native_residual_definition_readiness.csv",
            "EvidenceSignal": f"rerun-resolved residual contracts={contract['ResidualContractsResolvedForRerunCandidate']}/{contract['ResidualContracts']}",
            "BlocksMeasurement": True,
            "RequiredAction": "freeze BAO observable, baseline/r_d policy, and residual definition used by the covariance transform",
            "AcceptanceCriterion": "BAO residual vector is likelihood-native rather than nearest-anchor diagnostic proxy",
        },
        {
            "ComponentID": "PCOV_06_SOURCE_SPLIT_VECTOR",
            "ComponentClass": "joint_target_vector",
            "CurrentStatus": rerun_status(rerun_vector_ready, int(inputs["PreflightUsableObjects"]) == int(inputs["Objects"])),
            "CurrentArtifact": str(RERUN_VECTOR.relative_to(ROOT)) if rerun_vector_ready else "evidence/likelihood_native_input_object_summary.csv",
            "EvidenceSignal": (
                f"candidate y_split ready={rerun_vector_ready}; "
                f"preflight usable objects={inputs['PreflightUsableObjects']}/{inputs['Objects']}; "
                f"measurement usable={inputs['MeasurementUsableObjects']}/{inputs['Objects']}"
            ),
            "BlocksMeasurement": True,
            "RequiredAction": "export final y_split vector from the same SN and BAO residual policies",
            "AcceptanceCriterion": "one coordinate-native source-split vector is shared by K1, locked A2, and all null comparators",
        },
        {
            "ComponentID": "PCOV_07_JOINT_COVARIANCE",
            "ComponentClass": "joint_covariance",
            "CurrentStatus": rerun_status(rerun_cov_ready),
            "CurrentArtifact": str(RERUN_COV.relative_to(ROOT)) if rerun_cov_ready else "evidence/joint_covariance_adjudication_summary.csv",
            "EvidenceSignal": (
                f"candidate C_split ready={rerun_cov_ready}; "
                f"positive definite={'' if rerun is None else rerun['CovariancePositiveDefinite']}; "
                f"measurement blocker={adjudication['PrimaryBlocker']}"
            ),
            "BlocksMeasurement": True,
            "RequiredAction": "construct C_split from the final SN/BAO transforms and an explicit SN-BAO cross-covariance policy",
            "AcceptanceCriterion": "same positive-definite C_split is used for K1, locked A2, polynomial, physical, and randomized controls",
        },
        {
            "ComponentID": "PCOV_08_CROSS_COVARIANCE_POLICY",
            "ComponentClass": "cross_covariance_policy",
            "CurrentStatus": "PARTIAL" if truthy(cross["PolicyFrozenForPreflight"]) else "BLOCKED",
            "CurrentArtifact": "evidence/a2_cross_covariance_policy_summary.csv",
            "EvidenceSignal": f"preflight rule={cross['PrimaryBenchmarkRule']}; PD rho range={cross['RhoMinPD']}..{cross['RhoMaxPD']}",
            "BlocksMeasurement": True,
            "RequiredAction": "promote or replace the zero-cross preflight rule with a public/source-native policy before measurement scoring",
            "AcceptanceCriterion": "cross-covariance policy is declared before scoring and is not selected by K2 performance",
        },
        {
            "ComponentID": "PCOV_09_COORDINATE_NATIVE_K1",
            "ComponentClass": "baseline",
            "CurrentStatus": status_from(False, k1_export_exists),
            "CurrentArtifact": str(K1_FILE.relative_to(ROOT)),
            "EvidenceSignal": str(k1["BlockingIssue"]),
            "BlocksMeasurement": True,
            "RequiredAction": "export K1 under the same coordinate map, residual vector, and C_split used by locked A2",
            "AcceptanceCriterion": "K1 is not fitted in this note and is not exported from a different covariance scale",
        },
        {
            "ComponentID": "PCOV_10_NULL_AND_POLY_CONTROLS",
            "ComponentClass": "null_policy",
            "CurrentStatus": "PARTIAL",
            "CurrentArtifact": "evidence/null_model_registry.csv",
            "EvidenceSignal": str(current_poly["Finding"]),
            "BlocksMeasurement": True,
            "RequiredAction": "freeze final fair nulls, polynomial complexity penalties, and physical-null controls under C_split",
            "AcceptanceCriterion": "locked A2 is compared against the registered null set with identical data vector and covariance",
        },
        {
            "ComponentID": "PCOV_11_LOCKED_RERUN_SCORECARD",
            "ComponentClass": "final_rerun",
            "CurrentStatus": "RERUN_COMPLETE" if rerun_score_ready else "BLOCKED",
            "CurrentArtifact": str(RERUN_SCORE.relative_to(ROOT)) if rerun_score_ready else "pending",
            "EvidenceSignal": (
                "depends on PCOV_04 through PCOV_10"
                if rerun is None
                else (
                    f"status={rerun['CurrentStatus']}; "
                    f"DeltaAIC K2-K1={rerun['DeltaAIC_K2_minus_K1']}; "
                    f"DeltaAIC K2-poly={rerun['DeltaAIC_K2_minus_BestPoly']}; "
                    f"K2>K1={rerun['K2ImprovesOverK1']}; "
                    f"K2>poly={rerun['K2BeatsBestPoly']}"
                )
            ),
            "BlocksMeasurement": True,
            "RequiredAction": "rerun K1, locked A2, polynomial, physical-null, sign-randomized, and coordinate controls without changing locked A2",
            "AcceptanceCriterion": "supportive, weakening, or strong-negative outcome is reported from the same final route",
        },
    ]

    detail = pd.DataFrame(rows)
    detail["RerunRule"] = "locked_A2_unchanged_no_rho_gt_4_no_K1_refit_no_target_sign_gate"
    detail["ClaimBoundary"] = "public_covariance_replacement_plan_no_measurement_validation"
    detail.to_csv(OUT, index=False)

    ready = int(detail["CurrentStatus"].eq("READY").sum())
    partial = int(detail["CurrentStatus"].eq("PARTIAL").sum())
    rerun_ready = int(detail["CurrentStatus"].eq("RERUN_READY").sum())
    rerun_partial = int(detail["CurrentStatus"].eq("RERUN_PARTIAL").sum())
    rerun_complete = int(detail["CurrentStatus"].eq("RERUN_COMPLETE").sum())
    blocked = int(detail["CurrentStatus"].eq("BLOCKED").sum())
    measurement_blockers = detail[detail["BlocksMeasurement"].map(truthy)]
    primary_blockers = ";".join(measurement_blockers["ComponentID"].astype(str).head(6))

    summary = pd.DataFrame(
        [
            {
                "PlanID": "A2_PUBLIC_COVARIANCE_REPLACEMENT_PLAN_V1",
                "Components": len(detail),
                "ReadyComponents": ready,
                "PartialComponents": partial,
                "RerunReadyComponents": rerun_ready,
                "RerunPartialComponents": rerun_partial,
                "RerunCompleteComponents": rerun_complete,
                "BlockedComponents": blocked,
                "MeasurementBlockingComponents": len(measurement_blockers),
                "RawPublicSNCovarianceAvailable": raw_sn_cov,
                "RawPublicBAOCovarianceAvailable": raw_bao_cov,
                "LockedA2InputReady": locked_k2_ready,
                "CoordinateNativeK1Ready": False,
                "CandidateJointCovarianceReady": rerun_cov_ready,
                "MeasurementGradeJointCovarianceReady": False,
                "FinalRerunReady": rerun_score_ready,
                "FinalRerunStatus": "" if rerun is None else rerun["CurrentStatus"],
                "FinalRerunK2ImprovesOverK1": "" if rerun is None else rerun["K2ImprovesOverK1"],
                "FinalRerunK2BeatsBestPoly": "" if rerun is None else rerun["K2BeatsBestPoly"],
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "PUBLIC_COVARIANCE_LOCKED_RERUN_COMPLETE_MEASUREMENT_BLOCKED"
                    if rerun_score_ready
                    else "PUBLIC_COVARIANCE_REPLACEMENT_PLAN_READY_MEASUREMENT_BLOCKED"
                ),
                "StrongestAllowedClaim": "the public-covariance replacement path is specified for a locked A2 rerun",
                "PrimaryBlockers": primary_blockers,
                "NextAction": (
                    "diagnose why the candidate public covariance rerun remains mixed/weakening; do not change locked A2"
                    if rerun_score_ready
                    else "freeze likelihood-native residual policies and construct C_split before rerunning locked A2 unchanged"
                ),
                "ClaimBoundary": "public_covariance_replacement_plan_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# A2 Public-Covariance Replacement Plan",
        "",
        "Status: implementation plan for replacing the calibrated preflight bridge. Measurement validation remains closed.",
        "",
        "## Summary",
        "",
        f"- Ready components: {ready}/{len(detail)}",
        f"- Partial components: {partial}",
        f"- Rerun-ready components: {rerun_ready}",
        f"- Rerun-complete components: {rerun_complete}",
        f"- Blocked components: {blocked}",
        f"- Measurement-blocking components: {len(measurement_blockers)}",
        f"- Raw public SN covariance available: {raw_sn_cov}",
        f"- Raw public BAO covariance available: {raw_bao_cov}",
        "- Locked A2 rerun rule: no kernel change, no rho>4, no K1 refit, no target-sign gate.",
        f"- Locked rerun candidate status: {'' if rerun is None else rerun['CurrentStatus']}",
        "",
        "## Components",
        "",
    ]
    for _, row in detail.iterrows():
        lines.extend(
            [
                f"### {row['ComponentID']}",
                "",
                f"- Class: {row['ComponentClass']}",
                f"- Status: {row['CurrentStatus']}",
                f"- Artifact: `{row['CurrentArtifact']}`",
                f"- Evidence signal: {row['EvidenceSignal']}",
                f"- Blocks measurement: {row['BlocksMeasurement']}",
                f"- Required action: {row['RequiredAction']}",
                f"- Acceptance criterion: {row['AcceptanceCriterion']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "This plan does not strengthen the empirical claim by itself. It turns the remaining public-covariance gap into an executable checklist for the next locked rerun.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
