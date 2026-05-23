#!/usr/bin/env python3
"""Build the P-TauCov branch-localized response protocol declaration."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NEGATIVE = ROOT / "evidence/p_taucov_parent_action_next_route_summary.csv"
OUT = ROOT / "evidence/p_taucov_branch_localized_response_protocol.csv"
SUMMARY = ROOT / "evidence/p_taucov_branch_localized_response_protocol_summary.csv"
DOC = ROOT / "docs/p_taucov_branch_localized_response_protocol.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
DECLARATION_ID = "P_TAUCOV_BRANCH_LOCALIZED_RESPONSE_PROTOCOL_v1"
CLAIM_BOUNDARY = "branch_localized_response_protocol_no_scoring"


def main() -> int:
    negative = pd.read_csv(NEGATIVE).iloc[0]
    negative_status_ok = str(negative["Status"]) == "P_TAUCOV_PARENT_ACTION_NEGATIVE_RESULT_ROUTE_DECLARED_NO_SCORING"
    rows = [
        (
            "BLR-01_ROUTE_TRIGGER",
            "the minimal global parent-action PSD lift failed primary OOS",
            negative_status_ok,
        ),
        (
            "BLR-02_SUPPORT_RULE",
            "branch support must be frozen from delta_C_Tau, parent-action coordinates, or held-out source metadata only",
            False,
        ),
        (
            "BLR-03_LOCALIZATION_MAP",
            "global PSD lift must be replaced by branch-localized block support or a signed-response protocol",
            False,
        ),
        (
            "BLR-04_NULL_POLICY",
            "outside-branch, shuffled-support, morphology-null, projection-null, and generic smooth PSD controls remain mandatory",
            False,
        ),
        (
            "BLR-05_DF_POLICY",
            "multi-channel or localized response must predeclare df penalty before scoring",
            False,
        ),
        (
            "BLR-06_NO_RESCUE_RULE",
            "negative parent-action result cannot be rescued by post-hoc family or signed diagnostics",
            True,
        ),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "DeclarationID": DECLARATION_ID,
                "GateID": gate,
                "Requirement": requirement,
                "Satisfied": bool(satisfied),
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate, requirement, satisfied in rows
        ]
    )
    table.to_csv(OUT, index=False)
    satisfied = int(table["Satisfied"].sum())
    status = "P_TAUCOV_BRANCH_LOCALIZED_RESPONSE_PROTOCOL_DECLARED_BLOCKED_NO_SCORING"
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "DeclarationID": DECLARATION_ID,
                "Status": status,
                "SatisfiedGates": satisfied,
                "TotalGates": len(table),
                "MissingGates": ";".join(table.loc[~table["Satisfied"], "GateID"]),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Branch-Localized Response Protocol",
                "",
                f"Status: `{status}`.",
                "",
                "The first parent-action primary scorecard showed that the minimal",
                "global two-coordinate PSD lift is too compressed. This protocol",
                "declares the next allowed model class without authorizing scoring.",
                "",
                "## Motivation",
                "",
                "The next candidate must explain branch-localized covariance response",
                "before seeing any new score. It must not be a post-hoc repair of the",
                "negative parent-action result.",
                "",
                "## Required Before Any New Score",
                "",
                "- frozen branch-support rule",
                "- frozen localization map or signed-response statistic",
                "- mandatory outside-branch, shuffled, morphology, projection, and",
                "  generic smooth PSD nulls",
                "- predeclared df penalty for any extra channel or block",
                "- explicit rule that diagnostics cannot rescue a failed primary",
                "",
                "## Claim Boundary",
                "",
                "Allowed: a stricter branch-localized response model class is now",
                "declared as the next route.",
                "",
                "Forbidden: this is not a v4 score search, not a survival claim, and",
                "not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
