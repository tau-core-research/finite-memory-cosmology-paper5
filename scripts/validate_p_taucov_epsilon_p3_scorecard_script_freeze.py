#!/usr/bin/env python3
"""Validate epsilon-P3 scorecard script freeze."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_p_taucov_epsilon_p3_alignment_scorecard.py"
DOC = ROOT / "docs/p_taucov_epsilon_p3_scorecard_script_freeze.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_scorecard_script_freeze.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_scorecard_script_freeze.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_scorecard_script_freeze_summary.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_scorecard_script_freeze_validation.csv"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bool_from_csv(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append({"AuditID": "P_TAUCOV_EPSILON_P3_SCORECARD_SCRIPT_FREEZE_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [SCRIPT, DOC, MANIFEST, SHA256, SUMMARY]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [SCRIPT, DOC, MANIFEST, SHA256, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_SCORECARD_SCRIPT_FREEZE_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    summary = pd.read_csv(SUMMARY).iloc[0]
    text = DOC.read_text(encoding="utf-8")
    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}

    add("status_frozen_no_auth", manifest.get("Status") == "SCORECARD_SCRIPT_FROZEN_NO_SCORING_AUTHORIZATION")
    add("script_hash_matches", manifest.get("ScorecardSHA256") == file_sha256(SCRIPT))
    add("script_requires_auth", manifest.get("ScriptRequiresFinalAuthorization") is True)
    add("manifest_no_scoring", manifest.get("PTauCovScoringAuthorized") is False)
    add("summary_script_frozen", bool_from_csv(summary["ScorecardScriptFrozen"]))
    add("summary_no_scoring", not bool_from_csv(summary["PTauCovScoringAuthorized"]))
    add("sha_script", hash_map.get(str(SCRIPT.relative_to(ROOT))) == file_sha256(SCRIPT))
    add("sha_manifest", hash_map.get(str(MANIFEST.relative_to(ROOT))) == file_sha256(MANIFEST))
    for phrase in ["scorecard script is frozen", "PTauCovScoringAuthorized: true", "does not run the scorecard"]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_SCORECARD_SCRIPT_FREEZE_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_SCORECARD_SCRIPT_FREEZE_VALID_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
