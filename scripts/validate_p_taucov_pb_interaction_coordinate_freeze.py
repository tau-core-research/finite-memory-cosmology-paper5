#!/usr/bin/env python3
"""Validate the frozen P-TauCov PB interaction coordinate."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FREEZE_ID = "P_TAUCOV_PB_INTERACTION_COORDINATE_FREEZE_v1"
EXPECTED_STATUS = "P_TAUCOV_PB_INTERACTION_COORDINATE_FROZEN_NO_OBJECT_NO_SCORING"

FILES = {
    "coordinate": EVIDENCE / "p_taucov_pb_interaction_coordinate.csv",
    "manifest": EVIDENCE / "p_taucov_pb_interaction_coordinate_manifest.csv",
    "sha": EVIDENCE / "p_taucov_pb_interaction_coordinate.sha256",
    "doc": DOCS / "p_taucov_pb_interaction_coordinate_freeze.md",
}
OUT = EVIDENCE / "p_taucov_pb_interaction_coordinate_validation.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "FreezeID": FREEZE_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for key, path in FILES.items():
        add(f"exists_{key}", path.exists())
    if all(path.exists() for path in FILES.values()):
        coord = pd.read_csv(FILES["coordinate"])
        manifest = pd.read_csv(FILES["manifest"]).iloc[0]
        doc = FILES["doc"].read_text(encoding="utf-8")
        actual_hash = sha256(FILES["coordinate"])
        add("status_expected", str(manifest["Status"]) == EXPECTED_STATUS)
        add("coordinate_hash_matches_manifest", str(manifest["CoordinateSHA256"]) == actual_hash)
        add("coordinate_hash_matches_sha_file", FILES["sha"].read_text(encoding="utf-8").startswith(actual_hash))
        add("rows_match_manifest", len(coord) == int(manifest["RowsFrozen"]))
        add("freeze_authorized", bool(manifest["CoordinateFreezeAuthorized"]))
        add("object_construction_not_authorized", not bool(manifest["ObjectConstructionAuthorized"]))
        add("scoring_not_authorized", not bool(manifest["ScoringAuthorized"]))
        add("survival_not_authorized", not bool(manifest["SurvivalClaimAuthorized"]))
        add("tau_validation_not_authorized", not bool(manifest["TauCoreValidationClaimAuthorized"]))
        add("coordinate_no_target_residuals", not bool(coord["UsesTargetResiduals"].any()))
        add("coordinate_no_score_outcomes", not bool(coord["UsesScoreOutcomes"].any()))
        add("doc_links_source_gate", "p_taucov_admissible_source_coordinate_extension.md" in doc)
        add("doc_forbids_scorecard", "authorized empirical scorecard" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PB_INTERACTION_COORDINATE_FREEZE_VALID" if ok else "P_TAUCOV_PB_INTERACTION_COORDINATE_FREEZE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
