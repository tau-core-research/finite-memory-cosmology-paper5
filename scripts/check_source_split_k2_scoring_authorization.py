#!/usr/bin/env python3
"""Final guard for source-split K2 scoring authorization."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "source_split_k2_scoring_authorization.csv"

REQUIRED_GATES = [
    "SS_TRANSFORM",
    "SS_K1_TARGET",
    "SS_JOINT_COVARIANCE",
    "SS_CANDIDATE_PATH_GUARD",
    "SS_RECONSTRUCTION_FAMILY_EXPORT",
    "SS_SIGN_RULE_PROMOTION",
]


def main() -> None:
    dashboard = pd.read_csv(EVIDENCE / "source_split_gate_dashboard.csv")
    summary = pd.read_csv(EVIDENCE / "source_split_gate_dashboard_summary.csv").iloc[0]
    rows = []
    for gate_id in REQUIRED_GATES:
        gate = dashboard[dashboard["GateID"].eq(gate_id)]
        if gate.empty:
            rows.append(
                {
                    "AuthorizationID": "SOURCE_SPLIT_K2_AUTHORIZATION_V1",
                    "GateID": gate_id,
                    "Required": True,
                    "GatePresent": False,
                    "GateAllowed": False,
                    "BlockingIssue": "gate_missing",
                    "NextAction": "Create and pass the missing gate before K2 scoring.",
                    "ClaimBoundary": "authorization_guard_only_no_measurement_validation",
                }
            )
            continue
        gate_row = gate.iloc[0]
        rows.append(
            {
                "AuthorizationID": "SOURCE_SPLIT_K2_AUTHORIZATION_V1",
                "GateID": gate_id,
                "Required": True,
                "GatePresent": True,
                "GateAllowed": bool(gate_row["AllowedForK2Scoring"]),
                "BlockingIssue": "" if bool(gate_row["AllowedForK2Scoring"]) else str(gate_row["BlockingIssue"]),
                "NextAction": str(gate_row["NextAction"]),
                "ClaimBoundary": "authorization_guard_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    all_required_allowed = bool(output["GateAllowed"].all())
    dashboard_authorized = bool(summary["K2ScoringAuthorized"])
    final_authorized = all_required_allowed and dashboard_authorized
    output["AllRequiredGatesAllowed"] = all_required_allowed
    output["DashboardAuthorized"] = dashboard_authorized
    output["K2ScoringAuthorized"] = final_authorized
    output["AuthorizationDecision"] = "AUTHORIZED" if final_authorized else "BLOCKED"
    output["PrimaryNextAction"] = (
        "Run source-split K2/null scorecard under locked K2 protocol."
        if final_authorized
        else str(summary["PrimaryNextAction"])
    )
    output.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
