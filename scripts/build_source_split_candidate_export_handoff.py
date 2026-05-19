#!/usr/bin/env python3
"""Build a handoff manifest for the missing source-split candidate export."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CANDIDATE = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
VALIDATION = EVIDENCE / "source_split_reconstruction_family_export_validation.csv"
PROMOTION = EVIDENCE / "source_split_sign_rule_promotion_readiness.csv"
AUTHORIZATION = EVIDENCE / "source_split_k2_scoring_authorization.csv"
OUT = EVIDENCE / "source_split_candidate_export_handoff_manifest.csv"
SUMMARY = EVIDENCE / "source_split_candidate_export_handoff_summary.csv"


HANDOFF_ROWS = [
    {
        "StepID": "CEH1_TARGET_SCHEMA",
        "StepName": "Use frozen reconstruction-family export schema",
        "InputArtifact": "evidence/source_split_reconstruction_family_export_schema.csv",
        "OutputArtifact": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "Required": True,
        "CurrentStatus": "schema_available",
        "BlockingIssue": "",
        "ValidationCommand": "python3 scripts/build_source_split_reconstruction_family_export_schema.py",
        "NextAction": "Use the schema columns exactly; do not add scoring-only columns.",
    },
    {
        "StepID": "CEH2_SN_BRANCH",
        "StepName": "Export SN residual branch as reconstruction family",
        "InputArtifact": "evidence/source_split_sn_branch_export_handoff.csv",
        "OutputArtifact": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "Required": True,
        "CurrentStatus": "handoff_ready_not_exported",
        "BlockingIssue": "candidate_export_missing",
        "ValidationCommand": "python3 scripts/build_source_split_sn_branch_export_handoff.py",
        "NextAction": "Populate RFAM_SN_RESIDUAL_BRANCH rows for every usable coordinate-native target row.",
    },
    {
        "StepID": "CEH3_BAO_BRANCH",
        "StepName": "Export BAO residual branch as reconstruction family",
        "InputArtifact": "evidence/source_split_bao_branch_export_handoff.csv",
        "OutputArtifact": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "Required": True,
        "CurrentStatus": "handoff_ready_not_exported",
        "BlockingIssue": "candidate_export_missing",
        "ValidationCommand": "python3 scripts/build_source_split_bao_branch_export_handoff.py",
        "NextAction": "Populate RFAM_BAO_RESIDUAL_BRANCH rows for every usable coordinate-native target row.",
    },
    {
        "StepID": "CEH4_VALIDATE_EXPORT",
        "StepName": "Validate candidate export",
        "InputArtifact": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "OutputArtifact": "evidence/source_split_reconstruction_family_export_validation.csv",
        "Required": True,
        "CurrentStatus": "candidate_missing",
        "BlockingIssue": "candidate_export_missing",
        "ValidationCommand": "python3 scripts/validate_source_split_reconstruction_family_export.py",
        "NextAction": "Candidate must pass schema, row-alignment, family-count, sigma, sign, and no-fit checks.",
    },
    {
        "StepID": "CEH5_SIGN_RULE_PROMOTION",
        "StepName": "Promote family sign rule only after export validation",
        "InputArtifact": "evidence/source_split_reconstruction_family_export_validation.csv",
        "OutputArtifact": "evidence/source_split_sign_rule_promotion_readiness.csv",
        "Required": True,
        "CurrentStatus": "blocked",
        "BlockingIssue": "candidate_export_missing;scoring_rule_not_locked",
        "ValidationCommand": "python3 scripts/check_source_split_sign_rule_promotion.py",
        "NextAction": "Keep warning rows as warnings; promote only after valid export exists.",
    },
    {
        "StepID": "CEH6_AUTHORIZATION_GUARD",
        "StepName": "Run final K2 scoring authorization guard",
        "InputArtifact": "evidence/source_split_gate_dashboard.csv",
        "OutputArtifact": "evidence/source_split_k2_scoring_authorization.csv",
        "Required": True,
        "CurrentStatus": "blocked",
        "BlockingIssue": "upstream_gates_blocked",
        "ValidationCommand": "python3 scripts/check_source_split_k2_scoring_authorization.py",
        "NextAction": "Do not run K2/null scorecard unless authorization returns AUTHORIZED.",
    },
]


def validation_clean() -> bool:
    if not VALIDATION.exists():
        return False
    validation = pd.read_csv(VALIDATION)
    if validation.empty:
        return False
    return bool(validation.iloc[0]["AllowedForK2Scoring"])


def sign_rule_promoted() -> bool:
    if not PROMOTION.exists():
        return False
    promotion = pd.read_csv(PROMOTION)
    rows = promotion[promotion["CheckID"].eq("SRP5_RULE_PROMOTION_AUTHORIZED")]
    if rows.empty:
        return False
    return bool(rows.iloc[0].get("AllowedForK2Scoring", False))


def authorization_granted() -> bool:
    if not AUTHORIZATION.exists():
        return False
    authorization = pd.read_csv(AUTHORIZATION)
    if authorization.empty or "K2ScoringAuthorized" not in authorization.columns:
        return False
    return authorization["K2ScoringAuthorized"].astype(str).str.lower().eq("true").all()


def main() -> None:
    output = pd.DataFrame(HANDOFF_ROWS)
    candidate_exists = CANDIDATE.exists()
    export_valid = validation_clean()
    rule_promoted = sign_rule_promoted()
    authorized = authorization_granted()

    if candidate_exists:
        output.loc[output["StepID"].isin(["CEH2_SN_BRANCH", "CEH3_BAO_BRANCH"]), "CurrentStatus"] = "exported"
        output.loc[output["StepID"].isin(["CEH2_SN_BRANCH", "CEH3_BAO_BRANCH"]), "BlockingIssue"] = ""
        output.loc[output["StepID"].isin(["CEH2_SN_BRANCH", "CEH3_BAO_BRANCH"]), "NextAction"] = (
            "Candidate export contains this branch; keep source handoff for provenance."
        )
        output.loc[output["StepID"].eq("CEH4_VALIDATE_EXPORT"), "CurrentStatus"] = (
            "validation_clean" if export_valid else "candidate_present_needs_fix"
        )
        output.loc[output["StepID"].eq("CEH4_VALIDATE_EXPORT"), "BlockingIssue"] = (
            "" if export_valid else "candidate_export_not_validated"
        )
        output.loc[output["StepID"].eq("CEH4_VALIDATE_EXPORT"), "NextAction"] = (
            "Validation is clean; proceed to sign-rule promotion and remaining gates."
            if export_valid
            else "Fix candidate export until validation is clean."
        )

    if rule_promoted:
        output.loc[output["StepID"].eq("CEH5_SIGN_RULE_PROMOTION"), "CurrentStatus"] = "authorized"
        output.loc[output["StepID"].eq("CEH5_SIGN_RULE_PROMOTION"), "BlockingIssue"] = ""
        output.loc[output["StepID"].eq("CEH5_SIGN_RULE_PROMOTION"), "NextAction"] = (
            "Carry warning labels into any later scorecard; do not hide warning rows."
        )

    if authorized:
        output.loc[output["StepID"].eq("CEH6_AUTHORIZATION_GUARD"), "CurrentStatus"] = "authorized"
        output.loc[output["StepID"].eq("CEH6_AUTHORIZATION_GUARD"), "BlockingIssue"] = ""
        output.loc[output["StepID"].eq("CEH6_AUTHORIZATION_GUARD"), "NextAction"] = (
            "Run source-split K2/null scorecard under locked preflight protocol."
        )

    output["AllowedForK2ScoringNow"] = False
    output["ClaimBoundary"] = "candidate_export_handoff_only_no_measurement_validation"
    output.to_csv(OUT, index=False)
    blockers = output[output["BlockingIssue"].astype(str).ne("")]
    primary_issue = "candidate_export_missing"
    next_action = "Create the candidate export at the declared path, then run validation and authorization guards."
    if authorized:
        primary_issue = ""
        next_action = "Run source-split K2/null scorecard under locked preflight protocol."
    elif candidate_exists and export_valid:
        primary_issue = "upstream_gates_blocked"
        next_action = "Resolve remaining transform, K1, covariance, and sign-family gates before K2 scoring."
    summary = pd.DataFrame(
        [
            {
                "HandoffID": "SOURCE_SPLIT_CANDIDATE_EXPORT_HANDOFF_V1",
                "Steps": len(output),
                "BlockedSteps": len(blockers),
                "CandidatePath": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
                "PrimaryBlockingIssue": primary_issue,
                "AllowedForK2ScoringNow": False,
                "NextAction": next_action,
                "ClaimBoundary": "candidate_export_handoff_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
