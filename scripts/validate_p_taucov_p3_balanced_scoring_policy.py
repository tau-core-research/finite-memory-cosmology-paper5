#!/usr/bin/env python3
"""Validate P3 balanced scoring policy freeze."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy.yaml"
SHA = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy.sha256"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_p3_balanced_scoring_policy.md"
OUT = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy_validation.csv"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_SCORING_POLICY_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_P3_BALANCED_SCORING_POLICY_FROZEN_NO_SCORING"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append(
        {
            "AuditID": AUDIT_ID,
            "CheckID": check_id,
            "Passed": bool(passed),
            "Required": True,
            "Status": "PASS" if passed else "FAIL",
        }
    )


def main() -> int:
    rows: list[dict] = []
    for path in [POLICY, SHA, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [POLICY, SHA, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_P3_BALANCED_SCORING_POLICY_INVALID")
        return 1

    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8")) or {}
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    recorded = SHA.read_text(encoding="utf-8").split()[0]
    add(rows, "status_expected", policy.get("Status") == EXPECTED_STATUS)
    add(rows, "summary_status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "scoring_not_authorized", policy.get("ScoringAuthorized") is False)
    add(rows, "survival_not_authorized", policy.get("SurvivalClaimAuthorized") is False)
    add(rows, "tau_validation_not_authorized", policy.get("TauCoreValidationClaimAuthorized") is False)
    add(rows, "measurement_not_allowed", policy.get("MeasurementValidationAllowed") is False)
    add(rows, "policy_sha_valid", recorded == sha256(POLICY))
    add(rows, "primary_object_hash_present", bool(policy.get("PrimaryObjectSHA256")) and policy.get("PrimaryObjectSHA256") != "MISSING")
    add(rows, "required_nulls_declared", len(policy.get("RequiredNullFamilies", [])) >= 6)
    add(rows, "required_gates_declared", len(policy.get("RequiredAggregationGates", [])) >= 6)
    add(rows, "doc_mentions_no_scoring", "does not authorize scoring" in doc)
    for key, rel in policy.get("PolicyInputs", {}).items():
        path = ROOT / rel
        add(rows, f"input_exists_{key}", path.exists())
        if path.exists():
            add(rows, f"input_hash_{key}", policy.get("PolicyInputSHA256", {}).get(key) == sha256(path))

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_P3_BALANCED_SCORING_POLICY_VALID" if ok else "P_TAUCOV_P3_BALANCED_SCORING_POLICY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
