#!/usr/bin/env python3
"""Validate a future public source-split reconstruction-family export."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.reconstruction_family import validate_reconstruction_family_export

TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
CANDIDATE = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
OUT = ROOT / "evidence" / "source_split_reconstruction_family_export_validation.csv"


def main() -> None:
    target = pd.read_csv(TARGET)
    if not CANDIDATE.exists():
        rows = [
            {
                "CandidatePath": str(CANDIDATE.relative_to(ROOT)),
                "Available": False,
                "AllowedForK2Scoring": False,
                "FamilyCount": 0,
                "UsableTargetRows": int(target["HasSNAndBAO"].astype(str).str.lower().eq("true").sum()),
                "BlockingIssue": "candidate_export_missing",
                "NextAction": "Export public reconstruction-family responses using evidence/source_split_reconstruction_family_export_template.csv.",
                "ClaimBoundary": "validation_gate_only_no_measurement_validation",
            }
        ]
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print(f"Wrote {OUT}")
        return

    candidate = pd.read_csv(CANDIDATE)
    issues = validate_reconstruction_family_export(candidate, target)
    allowed = not issues
    rows = [
        {
            "CandidatePath": str(CANDIDATE.relative_to(ROOT)),
            "Available": True,
            "AllowedForK2Scoring": allowed,
            "FamilyCount": int(candidate["FamilyID"].nunique()) if "FamilyID" in candidate.columns else 0,
            "UsableTargetRows": int(target["HasSNAndBAO"].astype(str).str.lower().eq("true").sum()),
            "BlockingIssue": ";".join(issues),
            "NextAction": "Run source-split K2/null scorecard only if this validation is clean.",
            "ClaimBoundary": "validation_gate_only_no_measurement_validation",
        }
    ]
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
