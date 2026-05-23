#!/usr/bin/env python3
"""Freeze survival gates for Backreaction-36."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT = EVIDENCE / "backreaction_36_survival_gates.csv"
SUMMARY = EVIDENCE / "backreaction_36_survival_gates_summary.csv"
DOC = DOCS / "backreaction_36_survival_gates.md"

PROTOCOL_ID = "P5B_BACKREACTION_36_FROZEN_MORPHOLOGY_PROTOCOL_v1"
CLAIM_BOUNDARY = "backreaction_36_survival_gates_predeclared"


GATES = [
    ("G1", "OOS_POLY2_INCREMENTAL_GAIN", "POLY_DEG2 + M_BSTAR_36 improves OOS score over POLY_DEG2."),
    ("G2", "LEAVE_ONE_FAMILY_OUT_POSITIVE", "Improvement is positive in leave-one-family-out aggregate."),
    ("G3", "CLOCK_BLOCK_HOLDOUT_POSITIVE", "Improvement is positive in contiguous clock-block aggregate."),
    ("G4", "AICC_BIC_NOT_ERASED", "AICc/BIC penalty does not erase the improvement."),
    ("G5", "BEATS_WRONG_CLOCK", "Real M_BSTAR_36 beats WRONG_CLOCK_BSTAR."),
    ("G6", "BEATS_PHASE_SHIFTED", "Real M_BSTAR_36 beats PHASE_SHIFTED_BSTAR."),
    ("G7", "BEATS_FAMILY_PERMUTED", "Real M_BSTAR_36 beats FAMILY_PERMUTED_BSTAR."),
    ("G8", "BEATS_RANDOM_SMOOTH_NULL", "Real M_BSTAR_36 beats RANDOM_SMOOTH_ACTIVE_SUPPORT_NULL."),
    ("G9", "AMPLITUDE_SIGN_STABLE", "Amplitude sign is stable across primary folds."),
    ("G10", "NO_SINGLE_FAMILY_DOMINANCE", "No single family contributes more than 60% of total positive OOS delta."),
]


def main() -> int:
    rows = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "GateID": gate_id,
                "GateName": name,
                "Requirement": requirement,
                "RequiredForMinimalSurvival": True,
                "FrozenBeforeScoring": True,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, name, requirement in GATES
        ]
    )
    rows.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SurvivalGates": len(rows),
                "RequiredForMinimalSurvival": len(rows),
                "SingleFamilyDominanceThreshold": 0.60,
                "CurrentStatus": "SURVIVAL_GATES_FROZEN",
                "ScoringAuthorizedByThisArtifact": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# Backreaction-36 Survival Gates",
                "",
                "Status: survival gates frozen; scoring is not authorized by this artifact.",
                "",
                "Minimal survival requires all 10 gates to pass.",
                "",
                "Single-family dominance threshold: no family may contribute more than 60%",
                "of total positive OOS delta.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for path in [OUT, SUMMARY, DOC]:
        print(f"wrote {path.relative_to(ROOT)}")
    print("SURVIVAL_GATES_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
