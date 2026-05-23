#!/usr/bin/env python3
"""Validate the parent-action scorecard script freeze."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_p_taucov_parent_action_scorecard.py"
FREEZE = ROOT / "evidence/p_taucov_parent_action_scorecard_script_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_scorecard_script_freeze_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_scorecard_script_freeze.md"
OUT = ROOT / "evidence/p_taucov_parent_action_scorecard_script_freeze_validation.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_PARENT_ACTION_SCORECARD_SCRIPT_FREEZE_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [SCRIPT, FREEZE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [SCRIPT, FREEZE, SUMMARY, DOC]):
        freeze = pd.read_csv(FREEZE).iloc[0]
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_PARENT_ACTION_SCORECARD_SCRIPT_FROZEN_NO_SCORING")
        add("hash_current", str(freeze["SHA256"]) == sha256(SCRIPT))
        add("inert_mode", str(freeze["ScriptMode"]) == "inert_until_final_manifest")
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_blocked", "intentionally blocked" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_SCORECARD_SCRIPT_FREEZE_VALID" if ok else "P_TAUCOV_PARENT_ACTION_SCORECARD_SCRIPT_FREEZE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
