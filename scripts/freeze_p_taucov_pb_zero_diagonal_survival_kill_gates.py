#!/usr/bin/env python3
"""Freeze PB zero-diagonal survival and kill gates."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_pb_zero_diagonal_survival_kill_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_pb_zero_diagonal_survival_kill_gates_summary.csv"
DOC = ROOT / "docs/p_taucov_pb_zero_diagonal_survival_kill_gates.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_SURVIVAL_KILL_GATES_FREEZE_v1"
CLAIM_BOUNDARY = "pb_zero_diagonal_survival_kill_gates_freeze_no_scoring"


def main() -> int:
    gates = [
        ("SURV-G1_PRIMARY_OOS_POSITIVE", "survival", "aggregate primary OOS DeltaNLL must be positive", True),
        ("SURV-G2_FAMILY_AGGREGATE_POSITIVE", "survival", "leave-one-family-out aggregate must be positive", True),
        ("SURV-G3_CLOCK_AGGREGATE_POSITIVE", "survival", "contiguous clock-block aggregate must be positive", True),
        ("SURV-G4_CONTEXT_AGGREGATE_POSITIVE", "survival", "observing-context aggregate must be positive", True),
        ("SURV-G5_BEATS_ALL_REQUIRED_NULLS", "survival", "primary score must exceed every required null comparator", True),
        ("SURV-G6_NOT_SINGLE_FAMILY_CLOCK_OR_CONTEXT_DOMINATED", "survival", "largest family, clock, or context contribution must not dominate", True),
        ("SURV-G7_ALPHA_STABLE", "survival", "fitted alpha must remain positive/stable across primary folds", True),
        ("SURV-G8_AIC_BIC_POLICY_PASS", "survival", "declared information-criterion policy must pass", True),
        ("KILL-K1_PRIMARY_OOS_NONPOSITIVE", "kill", "nonpositive primary OOS aggregate kills survival", True),
        ("KILL-K2_REQUIRED_NULL_BEATS_PRIMARY", "kill", "any required null beating primary kills survival", True),
        ("KILL-K3_FAMILY_CLOCK_OR_CONTEXT_DOMINANCE", "kill", "single-family, clock, or context dominance kills survival", True),
        ("KILL-K4_ALPHA_INSTABILITY", "kill", "unstable alpha kills survival", True),
        ("KILL-K5_POLICY_OR_HASH_MISMATCH", "kill", "policy/hash mismatch blocks scoring interpretation", True),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gid,
                "GateType": gtype,
                "Definition": definition,
                "Required": bool(required),
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gid, gtype, definition, required in gates
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PB_ZERO_DIAGONAL_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING",
                "SurvivalGates": int(table["GateType"].eq("survival").sum()),
                "KillGates": int(table["GateType"].eq("kill").sum()),
                "RequiredGates": int(table["Required"].sum()),
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "# P-TauCov PB Zero-Diagonal Survival/Kill Gates\n\n"
        "Status: `P_TAUCOV_PB_ZERO_DIAGONAL_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING`.\n\n"
        "Survival requires positive primary OOS behavior, positive family/clock/context\n"
        "aggregates, defeat of all required nulls, no family/clock/context dominance,\n"
        "alpha stability, and the declared information-criterion pass.\n",
        encoding="utf-8",
    )
    print("P_TAUCOV_PB_ZERO_DIAGONAL_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
