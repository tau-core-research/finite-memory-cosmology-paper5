#!/usr/bin/env python3
"""Build the P-TauCov parent-action freeze plan."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FIREWALL = ROOT / "evidence/p_taucov_parent_action_scoring_firewall_summary.csv"
OUT = ROOT / "evidence/p_taucov_parent_action_freeze_plan.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_freeze_plan_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_freeze_plan.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PLAN_ID = "P_TAUCOV_PARENT_ACTION_FREEZE_PLAN_v1"
CLAIM_BOUNDARY = "parent_action_freeze_plan_no_scoring"


def main() -> int:
    firewall = pd.read_csv(FIREWALL).iloc[0]
    firewall_valid = str(firewall["Status"]) == "P_TAUCOV_PARENT_ACTION_SCORING_BLOCKED_FREEZE_REQUIRED"
    rows = [
        (
            "FREEZE_01_PRIMARY_SCORECARD_SCRIPT",
            "scripts/run_p_taucov_parent_action_scorecard.py",
            "must be written, hashed, and validated without reading target score outcomes",
        ),
        (
            "FREEZE_02_FOLD_POLICY",
            "evidence/p_taucov_parent_action_fold_policy.csv",
            "must declare folds, blocked aggregations, and leave-family/clock logic",
        ),
        (
            "FREEZE_03_NULL_COMPARATORS",
            "evidence/p_taucov_parent_action_null_comparators.csv",
            "must include outside-branch, shuffled, morphology-null, projection-null, and generic baseline controls",
        ),
        (
            "FREEZE_04_SURVIVAL_KILL_GATES",
            "evidence/p_taucov_parent_action_survival_kill_gates.csv",
            "must define success/failure before scorecard execution",
        ),
        (
            "FREEZE_05_DF_COVARIANCE_POLICY",
            "evidence/p_taucov_parent_action_df_covariance_policy.csv",
            "must define df=1 or other declared df, alpha bounds, PSD policy, and regularization",
        ),
        (
            "FREEZE_06_FINAL_MANIFEST",
            "evidence/p_taucov_parent_action_final_manifest.yaml",
            "must hash all inputs and explicitly authorize exactly one scorecard scope",
        ),
    ]
    plan = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PlanID": PLAN_ID,
                "FreezeStep": step,
                "ExpectedArtifact": artifact,
                "Requirement": requirement,
                "Completed": False,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for step, artifact, requirement in rows
        ]
    )
    plan.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PlanID": PLAN_ID,
                "Status": "P_TAUCOV_PARENT_ACTION_FREEZE_PLAN_DECLARED_NO_SCORING" if firewall_valid else "P_TAUCOV_PARENT_ACTION_FREEZE_PLAN_BLOCKED",
                "FreezeSteps": len(plan),
                "CompletedSteps": int(plan["Completed"].sum()),
                "FirewallValid": firewall_valid,
                "ScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Action Freeze Plan",
                "",
                f"Status: `{summary.iloc[0]['Status']}`.",
                "",
                "This document lists the artifacts that must be frozen before any",
                "parent-action P-TauCov scorecard can be authorized.",
                "",
                "## Freeze Steps",
                "",
                *[f"- `{step}` -> `{artifact}`" for step, artifact, _ in rows],
                "",
                "## Boundary",
                "",
                "This is a planning packet only. It does not authorize scoring, does",
                "not inspect target outcomes, and does not create a survival claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(summary.iloc[0]["Status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
