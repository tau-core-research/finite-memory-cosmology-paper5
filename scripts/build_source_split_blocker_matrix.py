#!/usr/bin/env python3
"""Build a compact blocker matrix for the source-split measurement gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CANDIDATE = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
OUT = EVIDENCE / "source_split_blocker_matrix.csv"
SUMMARY = EVIDENCE / "source_split_blocker_matrix_summary.csv"


def split_issues(value: object) -> list[str]:
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    return [part for part in text.split(";") if part]


def main() -> None:
    dashboard = pd.read_csv(EVIDENCE / "source_split_gate_dashboard.csv")
    handoff = pd.read_csv(EVIDENCE / "source_split_candidate_export_handoff_manifest.csv")
    auth = pd.read_csv(EVIDENCE / "source_split_k2_scoring_authorization.csv")
    final_authorized = (
        not auth.empty
        and "K2ScoringAuthorized" in auth.columns
        and auth["K2ScoringAuthorized"].astype(str).str.lower().eq("true").all()
    )

    rows: list[dict[str, object]] = []
    for _, gate in dashboard.iterrows():
        if str(gate["GateID"]) == "SS_INPUTS_AND_NULLS":
            continue
        if str(gate["GateID"]) == "SS_RECONSTRUCTION_FAMILY_PREVIEW" and final_authorized:
            continue
        issues = split_issues(gate["BlockingIssue"])
        if not issues and bool(gate["AllowedForK2Scoring"]):
            continue
        rows.append(
            {
                "BlockerID": f"BM_GATE_{gate['GateID']}",
                "BlockerType": "gate",
                "SourceArtifact": gate["Evidence"],
                "GateOrStep": gate["GateID"],
                "Status": gate["Status"],
                "BlockingIssue": ";".join(issues),
                "IssueCount": len(issues),
                "NextAction": gate["NextAction"],
                "BlocksK2Scoring": not bool(gate["AllowedForK2Scoring"]),
                "ResolutionOrder": 20,
                "ClaimBoundary": "blocker_matrix_only_no_measurement_validation",
            }
        )

    for _, step in handoff.iterrows():
        issues = split_issues(step["BlockingIssue"])
        if not issues:
            continue
        order = {
            "CEH2_SN_BRANCH": 1,
            "CEH3_BAO_BRANCH": 2,
            "CEH4_VALIDATE_EXPORT": 3,
            "CEH5_SIGN_RULE_PROMOTION": 4,
            "CEH6_AUTHORIZATION_GUARD": 5,
        }.get(str(step["StepID"]), 10)
        rows.append(
            {
                "BlockerID": f"BM_HANDOFF_{step['StepID']}",
                "BlockerType": "handoff",
                "SourceArtifact": step["InputArtifact"],
                "GateOrStep": step["StepID"],
                "Status": step["CurrentStatus"],
                "BlockingIssue": ";".join(issues),
                "IssueCount": len(issues),
                "NextAction": step["NextAction"],
                "BlocksK2Scoring": True,
                "ResolutionOrder": order,
                "ClaimBoundary": "blocker_matrix_only_no_measurement_validation",
            }
        )

    for _, gate in auth.iterrows():
        if bool(gate["GateAllowed"]):
            continue
        issues = split_issues(gate["BlockingIssue"])
        rows.append(
            {
                "BlockerID": f"BM_AUTH_{gate['GateID']}",
                "BlockerType": "authorization",
                "SourceArtifact": "source_split_k2_scoring_authorization.csv",
                "GateOrStep": gate["GateID"],
                "Status": gate["AuthorizationDecision"],
                "BlockingIssue": ";".join(issues),
                "IssueCount": len(issues),
                "NextAction": gate["NextAction"],
                "BlocksK2Scoring": True,
                "ResolutionOrder": 30,
                "ClaimBoundary": "blocker_matrix_only_no_measurement_validation",
            }
        )

    if rows:
        output = pd.DataFrame(rows).sort_values(["ResolutionOrder", "BlockerType", "GateOrStep"])
    else:
        output = pd.DataFrame(
            columns=[
                "BlockerID",
                "BlockerType",
                "SourceArtifact",
                "GateOrStep",
                "Status",
                "BlockingIssue",
                "IssueCount",
                "NextAction",
                "BlocksK2Scoring",
                "ResolutionOrder",
                "ClaimBoundary",
            ]
        )
    output.to_csv(OUT, index=False)

    if output.empty:
        primary_issue = ""
        primary_next_action = "K2/null scorecard is authorized under the locked source-split preflight protocol."
    else:
        primary = output.sort_values(["ResolutionOrder", "IssueCount"], ascending=[True, False]).iloc[0]
        primary_issue = primary["BlockingIssue"]
        primary_next_action = str(primary["NextAction"])
    summary = pd.DataFrame(
        [
            {
                "MatrixID": "SOURCE_SPLIT_BLOCKER_MATRIX_V1",
                "Blockers": len(output),
                "K2BlockingRows": int(output["BlocksK2Scoring"].sum()),
                "PrimaryBlockingIssue": primary_issue,
                "PrimaryNextAction": primary_next_action
                if CANDIDATE.exists()
                else "Populate RFAM_SN_RESIDUAL_BRANCH and RFAM_BAO_RESIDUAL_BRANCH rows in the real candidate export.",
                "K2ScoringAuthorized": final_authorized,
                "ClaimBoundary": "blocker_matrix_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
