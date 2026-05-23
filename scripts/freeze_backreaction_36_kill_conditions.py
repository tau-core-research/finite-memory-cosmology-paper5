#!/usr/bin/env python3
"""Freeze kill conditions for Backreaction-36."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT = EVIDENCE / "backreaction_36_kill_conditions.csv"
SUMMARY = EVIDENCE / "backreaction_36_kill_conditions_summary.csv"
DOC = DOCS / "backreaction_36_kill_conditions.md"

PROTOCOL_ID = "P5B_BACKREACTION_36_FROZEN_MORPHOLOGY_PROTOCOL_v1"
CLAIM_BOUNDARY = "backreaction_36_kill_conditions_predeclared"


KILLS = [
    ("KPRE1", "pre_score", "M_BSTAR_36 remaining norm after POLY2 projection < 0.50."),
    ("KPRE2", "pre_score", "One family carries > 60% of vector norm."),
    ("KPRE3", "pre_score", "Target residual used in generator."),
    ("KPRE4", "pre_score", "Generator hash changes after target columns are removed."),
    ("KPRE5", "pre_score", "Null comparator generation depends on target."),
    ("KPRE6", "pre_score", "Row set changes after freeze."),
    ("KPRE7", "pre_score", "Fold design changes after seeing score."),
    ("KSCORE1", "score", "OOS delta <= 0."),
    ("KSCORE2", "score", "Leave-one-family-out aggregate fails."),
    ("KSCORE3", "score", "Contiguous clock-block aggregate fails."),
    ("KSCORE4", "score", "BIC/AICc negative."),
    ("KSCORE5", "score", "Any primary null comparator matches or beats real M_BSTAR_36."),
    ("KSCORE6", "score", "Amplitude sign unstable."),
    ("KSCORE7", "score", "Improvement dominated by one family."),
]


def main() -> int:
    rows = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "KillID": kill_id,
                "KillClass": kill_class,
                "Condition": condition,
                "FrozenBeforeScoring": True,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for kill_id, kill_class, condition in KILLS
        ]
    )
    rows.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "KillConditions": len(rows),
                "PreScoreKillConditions": int(rows["KillClass"].eq("pre_score").sum()),
                "ScoreKillConditions": int(rows["KillClass"].eq("score").sum()),
                "FamilyNormDominanceThreshold": 0.60,
                "CurrentStatus": "KILL_CONDITIONS_FROZEN",
                "ScoringAuthorizedByThisArtifact": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# Backreaction-36 Kill Conditions",
                "",
                "Status: kill conditions frozen; scoring is not authorized by this artifact.",
                "",
                "Pre-score and score kill conditions are fixed before the candidate generator.",
                "",
                "Key thresholds:",
                "",
                "- remaining norm after POLY2 projection must be at least 0.50;",
                "- no family may carry more than 60% of vector norm;",
                "- no primary null comparator may match or beat real M_BSTAR_36.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for path in [OUT, SUMMARY, DOC]:
        print(f"wrote {path.relative_to(ROOT)}")
    print("KILL_CONDITIONS_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
