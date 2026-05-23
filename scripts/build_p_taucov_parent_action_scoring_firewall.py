#!/usr/bin/env python3
"""Build the P-TauCov parent-action scoring firewall."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PARENT_PACKET = ROOT / "evidence/p_taucov_candidate_full_parent_action_packet_summary.csv"
OUT_CHECKLIST = ROOT / "evidence/p_taucov_parent_action_scoring_firewall_checklist.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_parent_action_scoring_firewall_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_scoring_firewall.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FIREWALL_ID = "P_TAUCOV_PARENT_ACTION_SCORING_FIREWALL_v1"
CLAIM_BOUNDARY = "parent_action_scoring_firewall_no_scoring"


def main() -> int:
    parent = pd.read_csv(PARENT_PACKET).iloc[0]
    parent_packet_pass = str(parent["Status"]).endswith("PASS_NO_SCORING")

    required_items = [
        (
            "PARENT_ACTION_PACKET_PASS",
            "full parent-action embedding packet passes its no-scoring gates",
            parent_packet_pass,
        ),
        (
            "PRIMARY_SCORECARD_SCRIPT_FROZEN",
            "new parent-action P-TauCov scorecard script hash is frozen",
            False,
        ),
        (
            "FOLD_POLICY_FROZEN",
            "fold design is frozen before score access",
            False,
        ),
        (
            "NULL_COMPARATOR_POLICY_FROZEN",
            "outside-branch, shuffled, morphology-null, projection-null, and generic baseline nulls are frozen",
            False,
        ),
        (
            "SURVIVAL_AND_KILL_GATES_FROZEN",
            "success/failure criteria are frozen before scoring",
            False,
        ),
        (
            "DF_AND_COVARIANCE_POLICY_FROZEN",
            "degrees-of-freedom and covariance regularization policy are frozen",
            False,
        ),
        (
            "HASH_MANIFEST_READY",
            "all inputs and scripts have stable SHA256 records",
            False,
        ),
        (
            "NO_TARGET_OR_SCORE_INPUTS",
            "authorization packet itself uses no residual scores or score outcomes",
            True,
        ),
    ]
    checklist = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FirewallID": FIREWALL_ID,
                "ItemID": item_id,
                "Requirement": requirement,
                "Satisfied": bool(satisfied),
                "RequiredForScoring": True,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for item_id, requirement, satisfied in required_items
        ]
    )
    checklist.to_csv(OUT_CHECKLIST, index=False)
    satisfied_count = int(checklist["Satisfied"].sum())
    scoring_authorized = bool(checklist["Satisfied"].all())
    missing = checklist.loc[~checklist["Satisfied"], "ItemID"].tolist()
    status = (
        "P_TAUCOV_PARENT_ACTION_SCORING_AUTHORIZED"
        if scoring_authorized
        else "P_TAUCOV_PARENT_ACTION_SCORING_BLOCKED_FREEZE_REQUIRED"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FirewallID": FIREWALL_ID,
                "Status": status,
                "SatisfiedItems": satisfied_count,
                "TotalItems": len(checklist),
                "MissingItems": ";".join(missing),
                "ParentActionPacketPass": parent_packet_pass,
                "PTauCovScoringAuthorized": scoring_authorized,
                "SurvivalClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Action Scoring Firewall",
                "",
                f"Status: `{status}`.",
                "",
                "The parent-action packet now passes its no-scoring embedding gates,",
                "but that does not authorize empirical scoring. This firewall records",
                "what must be frozen before any parent-action P-TauCov scorecard can",
                "be run.",
                "",
                "## Current State",
                "",
                f"- parent-action packet pass: `{parent_packet_pass}`",
                f"- satisfied firewall items: `{satisfied_count}/{len(checklist)}`",
                f"- scoring authorized: `{scoring_authorized}`",
                f"- missing items: `{';'.join(missing)}`",
                "",
                "## Required Before Scoring",
                "",
                "- primary scorecard script hash",
                "- fold policy",
                "- null comparator policy",
                "- survival and kill gates",
                "- degrees-of-freedom and covariance policy",
                "- final SHA256 manifest",
                "",
                "## Claim Boundary",
                "",
                "Allowed: the parent-action side is ready for a future freeze packet.",
                "",
                "Forbidden: no empirical scoring, no survival claim, and no measurement",
                "validation are authorized by this packet.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
