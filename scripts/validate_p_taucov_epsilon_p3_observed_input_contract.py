#!/usr/bin/env python3
"""Validate epsilon-P3 observed-input contract."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_observed_input_contract.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract_summary.csv"
SCHEMA = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract_schema.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract_validation.csv"


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
        records.append({"AuditID": "P_TAUCOV_EPSILON_P3_OBSERVED_INPUT_CONTRACT_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [DOC, MANIFEST, SHA256, SUMMARY, SCHEMA]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [DOC, MANIFEST, SHA256, SUMMARY, SCHEMA]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_OBSERVED_INPUT_CONTRACT_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    summary = pd.read_csv(SUMMARY).iloc[0]
    schema = pd.read_csv(SCHEMA)
    text = DOC.read_text(encoding="utf-8")
    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}

    add("status_valid", manifest.get("Status") in {"BLOCKED_COORDINATE_SPACE_MISMATCH", "BRIDGE_READY_CONTRACT_NO_SCORING"})
    add("shape_compat_matches_status", bool(manifest.get("ShapeCompatibility")) == (manifest.get("Status") == "BRIDGE_READY_CONTRACT_NO_SCORING"))
    add("summary_shape_compat_matches", bool_from_csv(summary["ShapeCompatibility"]) == bool(manifest.get("ShapeCompatibility")))
    add("scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add("required_bridge_declared", "coordinate_bridge" in str(manifest.get("RequiredBridge", "")))
    add("schema_has_required_fields", {"RowCoordinate", "ColumnCoordinate", "ObservedWhitenedCovarianceResidual"}.issubset(set(schema["Field"].astype(str))))
    add("sha_schema", hash_map.get(str(SCHEMA.relative_to(ROOT))) == file_sha256(SCHEMA))
    add("sha_manifest", hash_map.get(str(MANIFEST.relative_to(ROOT))) == file_sha256(MANIFEST))
    for phrase in [str(manifest.get("Status")), f"ShapeCompatibility: {str(bool(manifest.get('ShapeCompatibility'))).lower()}", "target-blind coordinate bridge", "authorizes P-TauCov scoring"]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_OBSERVED_INPUT_CONTRACT_INVALID")
        print(failed.to_string(index=False))
        return 1
    print(f"P_TAUCOV_EPSILON_P3_OBSERVED_INPUT_CONTRACT_VALID_{manifest.get('Status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
