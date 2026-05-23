#!/usr/bin/env python3
"""Build the next-candidate admissibility gate after P-TauCov failures."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "evidence/p_taucov_program_status_after_signed_scorecard.csv"
OUT = ROOT / "evidence/p_taucov_next_candidate_admissibility_gate.csv"
SUMMARY = ROOT / "evidence/p_taucov_next_candidate_admissibility_gate_summary.csv"
DOC = ROOT / "docs/p_taucov_next_candidate_admissibility_gate.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
GATE_ID = "P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_v1"
CLAIM_BOUNDARY = "next_candidate_admissibility_gate_no_scoring"


def main() -> int:
    status = pd.read_csv(STATUS).iloc[0]
    failure_confirmed = str(status["Status"]) == "P_TAUCOV_PROTOCOL_INFRASTRUCTURE_VALID_BUT_NO_SURVIVING_TAU_SPECIFIC_SIGNAL"
    rows = [
        ("NC-G1_FAILURE_CONFIRMED", "previous PSD and signed candidates are non-survivors", failure_confirmed),
        ("NC-G2_DIAGONAL_ORTHOGONALITY_REQUIRED", "candidate must remove or orthogonalize diagonal support before scoring", True),
        ("NC-G3_FAMILY_BALANCE_REQUIRED", "candidate must predeclare family-balance cap before scoring", True),
        ("NC-G4_HELD_OUT_SUPPORT_REQUIRED", "support rule must not use the same target residual score or observed family dominance", True),
        ("NC-G5_SAME_NULL_DISCIPLINE_REQUIRED", "signed/projection/morphology/generic null discipline must be retained", True),
        ("NC-G6_NO_V4_SCORE_SEARCH", "unconstrained score-driven v4 kernel search is forbidden", True),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "GateID": GATE_ID,
                "RequirementID": req_id,
                "Requirement": requirement,
                "SatisfiedAsMetaGate": bool(satisfied),
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for req_id, requirement, satisfied in rows
        ]
    )
    table.to_csv(OUT, index=False)
    passed = int(table["SatisfiedAsMetaGate"].sum())
    status_text = (
        "P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_PASS_NO_SCORING"
        if passed == len(table)
        else "P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_BLOCKED_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "GateID": GATE_ID,
                "Status": status_text,
                "GatesPassed": passed,
                "GatesTotal": len(table),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Next-Candidate Admissibility Gate",
                "",
                f"Status: `{status_text}`.",
                "",
                "The previous PSD and signed-response candidates failed. A next",
                "candidate is admissible only if it is designed to avoid the observed",
                "failure modes before any new score is computed.",
                "",
                "## Required Design Constraints",
                "",
                "- diagonal support must be removed or explicitly orthogonalized;",
                "- family-balance constraints must be frozen before scoring;",
                "- support must be held-out or parent-derived, not selected from the",
                "  observed score failure;",
                "- signed, projection, morphology, and generic-null discipline must be",
                "  retained;",
                "- unconstrained v4 score search is forbidden.",
                "",
                "## Claim Boundary",
                "",
                "This is a meta-gate only. It authorizes no scoring and no positive",
                "scientific claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
