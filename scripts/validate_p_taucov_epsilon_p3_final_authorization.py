#!/usr/bin/env python3
"""Validate epsilon-P3 final authorization."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_final_authorization.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization_summary.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization_validation.csv"


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
        records.append({"AuditID": "P_TAUCOV_EPSILON_P3_FINAL_AUTHORIZATION_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [DOC, MANIFEST, SHA256, SUMMARY]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [DOC, MANIFEST, SHA256, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_FINAL_AUTHORIZATION_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    summary = pd.read_csv(SUMMARY).iloc[0]
    text = DOC.read_text(encoding="utf-8")
    recorded = SHA256.read_text(encoding="utf-8").split()[0]

    add("status_authorized", manifest.get("Status") == "PRIMARY_BRIDGE_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM")
    add("scoring_authorized", manifest.get("PTauCovScoringAuthorized") is True)
    add("summary_scoring_authorized", bool_from_csv(summary["PTauCovScoringAuthorized"]))
    add("survival_not_authorized", manifest.get("SurvivalClaimAuthorized") is False)
    add("measurement_not_authorized", manifest.get("MeasurementValidationAuthorized") is False)
    add("null_suite_not_authorized", manifest.get("NullSurvivalSuiteAuthorized") is False)
    add("scope_primary_only", manifest.get("AuthorizedScope") == "primary_bridge_projected_covariance_scorecard_only")
    add("manifest_sha", recorded == file_sha256(MANIFEST))
    for key, rel in manifest.get("InputFiles", {}).items():
        path = ROOT / rel
        add(f"input_exists_{key}", path.exists())
        if path.exists():
            add(f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == file_sha256(path))
    for phrase in ["PRIMARY_BRIDGE_SCORECARD_AUTHORIZED", "SurvivalClaimAuthorized: false", "MeasurementValidationAuthorized: false"]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_FINAL_AUTHORIZATION_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_FINAL_AUTHORIZATION_VALID_PRIMARY_SCORECARD_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
