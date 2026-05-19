#!/usr/bin/env python3
"""Guard the real candidate path against accidental preview promotion."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
PREVIEW = ROOT / "evidence" / "source_split_reconstruction_family_response_preview.csv"
OUT = ROOT / "evidence" / "source_split_candidate_path_guard.csv"


def same_table(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    """Return true if two dataframes match after column and row normalization."""
    if set(left.columns) != set(right.columns):
        return False
    columns = sorted(left.columns)
    left_norm = left[columns].sort_values(columns).reset_index(drop=True)
    right_norm = right[columns].sort_values(columns).reset_index(drop=True)
    return left_norm.equals(right_norm)


def main() -> None:
    preview_exists = PREVIEW.exists()
    candidate_exists = CANDIDATE.exists()
    copied_from_preview = False
    issue = "candidate_export_missing"
    status = "CANDIDATE_MISSING_EXPECTED_BLOCK"
    next_action = "Create a genuine public candidate export; do not copy the preview."

    if candidate_exists:
        candidate = pd.read_csv(CANDIDATE)
        if preview_exists:
            preview = pd.read_csv(PREVIEW)
            copied_from_preview = same_table(candidate, preview)
        if copied_from_preview:
            issue = "candidate_matches_non_scoring_preview"
            status = "BLOCKED_PREVIEW_COPY_DETECTED"
            next_action = "Replace candidate with a documented public reconstruction-family export."
        else:
            issue = ""
            status = "CANDIDATE_PRESENT_NEEDS_VALIDATION"
            next_action = "Run validate_source_split_reconstruction_family_export.py and downstream gates."
    allowed = candidate_exists and not copied_from_preview

    row = {
        "GuardID": "SOURCE_SPLIT_CANDIDATE_PATH_GUARD_V1",
        "CandidatePath": str(CANDIDATE.relative_to(ROOT)),
        "PreviewPath": str(PREVIEW.relative_to(ROOT)),
        "CandidateExists": candidate_exists,
        "PreviewExists": preview_exists,
        "CandidateMatchesPreview": copied_from_preview,
        "Status": status,
        "BlockingIssue": issue,
        "AllowedForK2Scoring": allowed,
        "NextAction": next_action,
        "ClaimBoundary": "candidate_path_guard_only_no_measurement_validation",
    }
    pd.DataFrame([row]).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
