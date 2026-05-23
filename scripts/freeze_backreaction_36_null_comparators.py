#!/usr/bin/env python3
"""Freeze null comparators for Backreaction-36."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT = EVIDENCE / "backreaction_36_null_comparators.csv"
SUMMARY = EVIDENCE / "backreaction_36_null_comparators_summary.csv"
DOC = DOCS / "backreaction_36_null_comparators.md"

PROTOCOL_ID = "P5B_BACKREACTION_36_FROZEN_MORPHOLOGY_PROTOCOL_v1"
CLAIM_BOUNDARY = "backreaction_36_null_comparators_frozen_before_candidate"


COMPARATORS = [
    ("POLY_DEG2", "baseline_absorber", "primary", "Quadratic baseline absorber on declared clock coordinate."),
    ("WRONG_CLOCK_BSTAR", "bstar_like_negative_control", "primary", "Same generator with frozen wrong-clock convention."),
    ("PHASE_SHIFTED_BSTAR", "bstar_like_negative_control", "primary", "Same support and smoothness with frozen clock phase shift."),
    ("FAMILY_PERMUTED_BSTAR", "bstar_like_negative_control", "primary", "Same values permuted across family labels before scoring."),
    ("RANDOM_SMOOTH_ACTIVE_SUPPORT_NULL", "smooth_template_negative_control", "primary", "Target-blind random smooth active-support null with fixed seed manifest."),
    ("OSCILLATORY_NULL_DIAGNOSTIC_ONLY", "diagnostic_control", "secondary", "Oscillatory geometry control; not a natural smooth weak-response class."),
    ("LOW_DF_SPLINE_CONTROL", "baseline_absorber", "secondary", "Fixed-knot low-df smooth absorber robustness control."),
]


def main() -> int:
    rows = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "ComparatorID": comparator_id,
                "ComparatorClass": comparator_class,
                "Role": role,
                "Definition": definition,
                "FrozenBeforeCandidateScoring": True,
                "UsesTargetResiduals": False,
                "UsesCandidateScore": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for comparator_id, comparator_class, role, definition in COMPARATORS
        ]
    )
    rows.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "Comparators": len(rows),
                "PrimaryComparators": int(rows["Role"].eq("primary").sum()),
                "NegativeBstarLikeControls": int(
                    rows["ComparatorClass"].eq("bstar_like_negative_control").sum()
                ),
                "SurvivalRequiresRealBeatsPoly2": True,
                "SurvivalRequiresRealBeatsBstarLikeNulls": True,
                "CurrentStatus": "NULL_COMPARATORS_FROZEN",
                "ScoringAuthorizedByThisArtifact": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# Backreaction-36 Null Comparators",
                "",
                "Status: null comparator family frozen; scoring is not authorized by this artifact.",
                "",
                "Primary survival requires the real frozen M_BSTAR_36 candidate to beat:",
                "",
                "- POLY_DEG2;",
                "- wrong-clock Bstar;",
                "- phase-shifted Bstar;",
                "- family-permuted Bstar;",
                "- random smooth active-support null.",
                "",
                "The oscillatory null is diagnostic only, because it is not the natural smooth",
                "weak-response class motivated by the theorem.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for path in [OUT, SUMMARY, DOC]:
        print(f"wrote {path.relative_to(ROOT)}")
    print("NULL_COMPARATORS_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
