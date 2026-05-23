#!/usr/bin/env python3
"""Validate authorization preflight for P3 balanced P-TauCov object."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_p3_balanced_authorization_preflight.md"
MANIFEST = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight.yaml"
SHA = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight.sha256"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight_summary.csv"
CHECKLIST = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight_checklist.csv"
OUT = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight_validation.csv"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_AUTHORIZATION_PREFLIGHT_VALIDATION"


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
    for path in [DOC, MANIFEST, SHA, SUMMARY, CHECKLIST]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [DOC, MANIFEST, SHA, SUMMARY, CHECKLIST]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_P3_BALANCED_AUTHORIZATION_PREFLIGHT_INVALID")
        return 1
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    checklist = pd.read_csv(CHECKLIST)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    hash_lines = [line.strip().split(maxsplit=1) for line in SHA.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}

    add(rows, "status_blocked_until_final_auth", manifest.get("Status") == "READY_FOR_FINAL_AUTHORIZATION_NO_SCORING")
    add(rows, "scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add(rows, "summary_scoring_not_authorized", str(summary["PTauCovScoringAuthorized"]).lower() == "false")
    add(rows, "scorecard_script_no_longer_blocks", "p3_balanced_scorecard_script_frozen" not in manifest.get("BlockingItems", []))
    add(rows, "blocks_final_authorization", "final_authorization_manifest_ready" in manifest.get("BlockingItems", []))
    add(rows, "base_inputs_passed", bool(checklist[~checklist["CheckID"].isin(["p3_balanced_scorecard_script_frozen", "final_authorization_manifest_ready"])]["Passed"].astype(bool).all()))
    add(rows, "all_rows_no_scoring", not checklist["PTauCovScoringAuthorized"].astype(bool).any())
    for path in [CHECKLIST, MANIFEST]:
        rel = str(path.relative_to(ROOT))
        add(rows, f"sha256_{rel}", hash_map.get(rel) == sha256(path))
    for key, rel in manifest.get("InputFiles", {}).items():
        path = ROOT / rel
        add(rows, f"input_exists_{key}", path.exists())
        if path.exists():
            add(rows, f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == sha256(path))
    add(rows, "doc_mentions_script_frozen", "scorecard\nscript are frozen" in doc)
    add(rows, "doc_mentions_forbidden_scoring_claim", "has been scored" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_P3_BALANCED_AUTHORIZATION_PREFLIGHT_VALID_BLOCKED_NO_SCORING" if ok else "P_TAUCOV_P3_BALANCED_AUTHORIZATION_PREFLIGHT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
