#!/usr/bin/env python3
"""Freeze parent-action P-TauCov survival and kill gates."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_parent_action_survival_kill_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_survival_kill_gates_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_survival_kill_gates.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_FREEZE_v1"
CLAIM_BOUNDARY = "parent_action_survival_kill_gates_freeze_no_scoring"


def main() -> int:
    gates = [
        ("SURV-G1_PRIMARY_OOS_POSITIVE", "survival", "aggregate primary OOS DeltaNLL must be positive", True),
        ("SURV-G2_FAMILY_AGGREGATE_POSITIVE", "survival", "leave-one-family-out aggregate must be positive", True),
        ("SURV-G3_CLOCK_AGGREGATE_POSITIVE", "survival", "contiguous clock-block aggregate must be positive", True),
        ("SURV-G4_BEATS_ALL_REQUIRED_NULLS", "survival", "primary score must exceed every required null comparator", True),
        ("SURV-G5_NOT_SINGLE_FAMILY_DOMINATED", "survival", "largest family contribution must not dominate the aggregate", True),
        ("SURV-G6_ALPHA_STABLE", "survival", "fitted alpha/sign/scale must remain stable across primary folds", True),
        ("SURV-G7_AIC_BIC_POLICY_PASS", "survival", "declared information-criterion policy must pass", True),
        ("KILL-K1_PRIMARY_OOS_NONPOSITIVE", "kill", "nonpositive primary OOS aggregate kills survival", True),
        ("KILL-K2_REQUIRED_NULL_BEATS_PRIMARY", "kill", "any required null beating primary kills survival", True),
        ("KILL-K3_SINGLE_FAMILY_DOMINANCE", "kill", "single-family dominance kills survival", True),
        ("KILL-K4_ALPHA_INSTABILITY", "kill", "unstable alpha/sign/scale kills survival", True),
        ("KILL-K5_POLICY_OR_HASH_MISMATCH", "kill", "policy/hash mismatch blocks scoring interpretation", True),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "GateType": gate_type,
                "Definition": definition,
                "Required": bool(required),
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, gate_type, definition, required in gates
        ]
    )
    table.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING",
                "SurvivalGates": int(table["GateType"].eq("survival").sum()),
                "KillGates": int(table["GateType"].eq("kill").sum()),
                "RequiredGates": int(table["Required"].sum()),
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Action Survival/Kill Gates",
                "",
                "Status: `P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING`.",
                "",
                "Survival requires positive primary out-of-sample behavior, positive",
                "family and clock aggregates, defeat of all required nulls, no",
                "single-family dominance, alpha stability, and the declared",
                "information-criterion pass.",
                "",
                "Any primary nonpositive result, required-null defeat, single-family",
                "dominance, alpha instability, or hash/policy mismatch kills or blocks",
                "the survival interpretation.",
                "",
                "These gates are frozen before scoring and do not authorize scoring.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
