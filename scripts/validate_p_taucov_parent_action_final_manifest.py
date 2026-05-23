#!/usr/bin/env python3
"""Validate parent-action P-TauCov final manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence/p_taucov_parent_action_final_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_parent_action_final_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_final_manifest_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_final_manifest.md"
OUT = ROOT / "evidence/p_taucov_parent_action_final_manifest_validation.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_PARENT_ACTION_FINAL_MANIFEST_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [MANIFEST, SHA256, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [MANIFEST, SHA256, SUMMARY, DOC]):
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        recorded = SHA256.read_text(encoding="utf-8").split()[0]
        add("status_authorized_primary_only", manifest.get("Status") == "P_TAUCOV_PARENT_ACTION_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM")
        add("summary_authorized", bool(summary["PTauCovScoringAuthorized"]) is True)
        add("survival_not_authorized", manifest.get("SurvivalClaimAuthorized") is False)
        add("measurement_not_authorized", manifest.get("MeasurementValidationAuthorized") is False)
        add("null_suite_not_authorized", manifest.get("NullSurvivalSuiteAuthorized") is False)
        add("scope_primary_only", manifest.get("AuthorizedScope") == "parent_action_primary_covariance_scorecard_only")
        add("manifest_sha_valid", recorded == sha256(MANIFEST))
        for key, rel in manifest.get("InputFiles", {}).items():
            path = ROOT / rel
            add(f"input_exists_{key}", path.exists())
            if path.exists():
                add(f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == sha256(path))
        scorecard = ROOT / manifest.get("AuthorizedScorecard", "")
        add("scorecard_exists", scorecard.exists())
        if scorecard.exists():
            add("scorecard_hash_valid", manifest.get("ScorecardSHA256") == sha256(scorecard))
        add("doc_claim_boundary", "does not authorize survival" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_FINAL_MANIFEST_VALID" if ok else "P_TAUCOV_PARENT_ACTION_FINAL_MANIFEST_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
