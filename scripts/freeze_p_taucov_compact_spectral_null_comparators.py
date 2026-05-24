#!/usr/bin/env python3
"""Freeze compact spectral null comparator policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_compact_spectral_null_comparators.csv"
SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_null_comparators_summary.csv"
DOC = ROOT / "docs/p_taucov_compact_spectral_null_comparators.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_COMPACT_SPECTRAL_NULL_COMPARATORS_FREEZE_v1"
CLAIM_BOUNDARY = "compact_spectral_null_comparators_freeze_no_scoring"


def main() -> int:
    rows = [
        ("GENERIC_RANDOM_SMOOTH_PSD", "generic_baseline", "strongest prior smooth PSD comparator", True, True),
        ("PROJECTION_NULL", "projection_null", "phase/projection-like null direction", True, True),
        ("SPECTRAL_MODE_SHUFFLE", "spectral_null", "shuffle selected compact spectral modes preserving count", True, True),
        ("SPECTRAL_LOW_PASS_COMPLEMENT", "spectral_null", "use low-frequency complement of selected compact modes", True, True),
        ("GENERIC_WRONG_CLOCK", "generic_baseline", "wrong-clock support comparator", True, True),
        ("GENERIC_PHASE_SHIFT", "generic_baseline", "phase-shift support comparator", True, True),
        ("GENERIC_FAMILY_PERMUTED", "generic_baseline", "family-permuted structure", True, True),
        ("GENERIC_DIAGONAL", "generic_baseline", "diagonal variance inflation comparator", True, True),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "NullID": null_id,
                "NullClass": null_class,
                "Definition": definition,
                "Required": bool(required),
                "PrimaryDefeatRequired": bool(primary_defeat),
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for null_id, null_class, definition, required, primary_defeat in rows
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_COMPACT_SPECTRAL_NULL_COMPARATORS_FROZEN_NO_SCORING",
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
        """# P-TauCov Compact Spectral Null Comparators

Status: `P_TAUCOV_COMPACT_SPECTRAL_NULL_COMPARATORS_FROZEN_NO_SCORING`.

The compact spectral source must defeat generic smooth PSD, projection-null,
spectral-mode shuffle, low-pass spectral complement, wrong-clock, phase-shift,
family-permuted, and diagonal comparators. This policy does not authorize
scoring.
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_COMPACT_SPECTRAL_NULL_COMPARATORS_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
