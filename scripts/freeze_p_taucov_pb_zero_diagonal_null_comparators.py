#!/usr/bin/env python3
"""Freeze PB zero-diagonal null comparator policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_pb_zero_diagonal_null_comparators.csv"
SUMMARY = ROOT / "evidence/p_taucov_pb_zero_diagonal_null_comparators_summary.csv"
DOC = ROOT / "docs/p_taucov_pb_zero_diagonal_null_comparators.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_NULL_COMPARATORS_FREEZE_v1"
CLAIM_BOUNDARY = "pb_zero_diagonal_null_comparators_freeze_no_scoring"


def main() -> int:
    rows = [
        ("GENERIC_RANDOM_SMOOTH_PSD", "generic_baseline", "strong prior smooth PSD comparator", True, True),
        ("PROJECTION_NULL", "projection_null", "projection-like null direction", True, True),
        ("MORPHOLOGY_NULL", "morphology_null", "morphology/proxy duplicate comparator", True, True),
        ("PB_DIAGONAL_ONLY", "diagonal_null", "diagonal-only PB variance comparator", True, True),
        ("PB_FAMILY_MASKED", "family_null", "family-masked PB diagnostic comparator", True, True),
        ("GENERIC_WRONG_CLOCK", "generic_baseline", "wrong-clock support comparator", True, True),
        ("GENERIC_PHASE_SHIFT", "generic_baseline", "phase-shift support comparator", True, True),
        ("GENERIC_FAMILY_PERMUTED", "generic_baseline", "family-permuted structure", True, True),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "NullID": nid,
                "NullClass": cls,
                "Definition": definition,
                "Required": bool(required),
                "PrimaryDefeatRequired": bool(defeat),
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for nid, cls, definition, required, defeat in rows
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PB_ZERO_DIAGONAL_NULL_COMPARATORS_FROZEN_NO_SCORING",
                "NullComparators": len(table),
                "RequiredNullComparators": int(table["Required"].sum()),
                "PrimaryDefeatRequired": int(table["PrimaryDefeatRequired"].sum()),
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "# P-TauCov PB Zero-Diagonal Null Comparators\n\n"
        "Status: `P_TAUCOV_PB_ZERO_DIAGONAL_NULL_COMPARATORS_FROZEN_NO_SCORING`.\n\n"
        "The PB zero-diagonal object must defeat smooth PSD, projection-null,\n"
        "morphology-null, diagonal-only, family-masked, wrong-clock, phase-shift,\n"
        "and family-permuted comparators. This policy does not authorize scoring.\n",
        encoding="utf-8",
    )
    print("P_TAUCOV_PB_ZERO_DIAGONAL_NULL_COMPARATORS_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
