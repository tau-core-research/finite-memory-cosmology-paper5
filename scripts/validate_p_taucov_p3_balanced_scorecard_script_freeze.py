#!/usr/bin/env python3
"""Validate P3 balanced scorecard script freeze."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_p_taucov_p3_balanced_scorecard.py"
DOC = ROOT / "docs/p_taucov_p3_balanced_scorecard_script_freeze.md"
MANIFEST = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze.yaml"
SHA = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze.sha256"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze_summary.csv"
OUT = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze_validation.csv"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FREEZE_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FROZEN_NO_SCORING"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})


def main() -> int:
    rows: list[dict] = []
    for path in [SCRIPT, DOC, MANIFEST, SHA, SUMMARY]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [SCRIPT, DOC, MANIFEST, SHA, SUMMARY]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FREEZE_INVALID")
        return 1
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    hash_lines = [line.strip().split(maxsplit=1) for line in SHA.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    add(rows, "status_expected", manifest.get("Status") == EXPECTED_STATUS)
    add(rows, "script_hash_matches", manifest.get("ScorecardSHA256") == sha256(SCRIPT))
    add(rows, "script_requires_auth", manifest.get("ScriptRequiresFinalAuthorization") is True)
    add(rows, "manifest_no_scoring", manifest.get("P3BalancedScoringAuthorized") is False)
    add(rows, "summary_script_frozen", bool(summary["ScorecardScriptFrozen"]) is True)
    add(rows, "summary_no_scoring", bool(summary["P3BalancedScoringAuthorized"]) is False)
    add(rows, "sha_script", hash_map.get(str(SCRIPT.relative_to(ROOT))) == sha256(SCRIPT))
    add(rows, "sha_manifest", hash_map.get(str(MANIFEST.relative_to(ROOT))) == sha256(MANIFEST))
    add(rows, "doc_mentions_inert", "script is inert" in doc)
    add(rows, "doc_mentions_no_scoring", "does not authorize empirical scoring" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FREEZE_VALID" if ok else "P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FREEZE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
