#!/usr/bin/env python3
"""Validate final authorization for P3 balanced P-TauCov scorecard."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_p3_balanced_final_authorization.md"
MANIFEST = ROOT / "evidence/p_taucov_p3_balanced_final_authorization.yaml"
SHA = ROOT / "evidence/p_taucov_p3_balanced_final_authorization.sha256"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_final_authorization_summary.csv"
OUT = ROOT / "evidence/p_taucov_p3_balanced_final_authorization_validation.csv"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_FINAL_AUTHORIZATION_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_P3_BALANCED_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM"


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
    for path in [DOC, MANIFEST, SHA, SUMMARY]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [DOC, MANIFEST, SHA, SUMMARY]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_P3_BALANCED_FINAL_AUTHORIZATION_INVALID")
        return 1
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    recorded = SHA.read_text(encoding="utf-8").split()[0]
    add(rows, "status_authorized", manifest.get("Status") == EXPECTED_STATUS)
    add(rows, "summary_status_authorized", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "scoring_authorized", manifest.get("P3BalancedScoringAuthorized") is True)
    add(rows, "survival_not_authorized", manifest.get("SurvivalClaimAuthorized") is False)
    add(rows, "covariance_survival_not_authorized", manifest.get("CovarianceSurvivalClaimAuthorized") is False)
    add(rows, "tau_validation_not_authorized", manifest.get("TauCoreValidationClaimAuthorized") is False)
    add(rows, "measurement_not_authorized", manifest.get("MeasurementValidationAuthorized") is False)
    add(rows, "scope_signed_alignment_only", manifest.get("AuthorizedScope") == "p3_balanced_signed_alignment_scorecard_only")
    add(rows, "manifest_sha_valid", recorded == sha256(MANIFEST))
    for key, rel in manifest.get("InputFiles", {}).items():
        path = ROOT / rel
        add(rows, f"input_exists_{key}", path.exists())
        if path.exists():
            add(rows, f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == sha256(path))
    add(rows, "doc_mentions_authorized_scope", "p3_balanced_signed_alignment_scorecard_only" in doc)
    add(rows, "doc_mentions_no_tau_validation", "Tau Core validation claim" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_P3_BALANCED_FINAL_AUTHORIZATION_VALID" if ok else "P_TAUCOV_P3_BALANCED_FINAL_AUTHORIZATION_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
