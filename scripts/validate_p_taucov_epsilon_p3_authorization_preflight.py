#!/usr/bin/env python3
"""Validate epsilon-P3 P-TauCov authorization preflight."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_authorization_preflight.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight_summary.csv"
CHECKLIST = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight_checklist.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight_validation.csv"


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
        records.append(
            {
                "AuditID": "P_TAUCOV_EPSILON_P3_AUTHORIZATION_PREFLIGHT_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required = [DOC, MANIFEST, SHA256, SUMMARY, CHECKLIST]
    for path in required:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in required):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_AUTHORIZATION_PREFLIGHT_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    checklist = pd.read_csv(CHECKLIST)
    summary = pd.read_csv(SUMMARY).iloc[0]
    text = DOC.read_text(encoding="utf-8")

    add("status_blocked", manifest.get("Status") == "BLOCKED_NO_SCORING_AUTHORIZATION")
    add("scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add("summary_scoring_not_authorized", not bool_from_csv(summary["PTauCovScoringAuthorized"]))
    add("has_open_required_checks", int(manifest.get("OpenRequiredChecks", 0)) >= 1)
    add("blocks_scorecard_script", "scorecard_script_frozen" in manifest.get("BlockingItems", []))
    add("blocks_input_contract", "observed_residual_input_contract_frozen" in manifest.get("BlockingItems", []))
    add("checklist_has_passes_and_blocks", checklist["Passed"].map(bool_from_csv).any() and (~checklist["Passed"].map(bool_from_csv)).any())
    add("all_rows_no_scoring", not checklist["PTauCovScoringAuthorized"].map(bool_from_csv).any())

    for key, rel in manifest.get("InputFiles", {}).items():
        path = ROOT / rel
        add(f"input_exists_{key}", path.exists())
        if path.exists():
            add(f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == file_sha256(path))

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    for path in [CHECKLIST, MANIFEST]:
        rel = str(path.relative_to(ROOT))
        add(f"sha256_{rel}", hash_map.get(rel) == file_sha256(path))

    for phrase in [
        "BLOCKED_NO_SCORING_AUTHORIZATION",
        "scorecard script",
        "observed residual/covariance input contract",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_AUTHORIZATION_PREFLIGHT_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_AUTHORIZATION_PREFLIGHT_VALID_BLOCKED_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
