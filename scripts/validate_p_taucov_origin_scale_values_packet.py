#!/usr/bin/env python3
"""Validate a concrete P-TauCov origin/scale values packet if it exists."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "data/p_taucov/linear/origin_scale_values.csv"
MANIFEST = ROOT / "evidence/p_taucov_origin_scale_values_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_origin_scale_values.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_origin_scale_values_leakage_audit.csv"
OUT = ROOT / "evidence/p_taucov_origin_scale_values_packet_validation.csv"

REQUIRED_COLUMNS = {
    "basis_axis",
    "origin_value",
    "scale_value",
    "origin_rule",
    "scale_rule",
    "value_source",
    "provenance",
}

FORBIDDEN_MANIFEST_FLAGS = {
    "OutcomeInformationUsed": False,
    "ResidualInformationUsed": False,
    "ScoreInformationUsed": False,
    "PostScoringLocalizationUsed": False,
}


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
                "AuditID": "P_TAUCOV_ORIGIN_SCALE_VALUES_PACKET_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required_paths = [VALUES, MANIFEST, SHA256, LEAKAGE]
    for path in required_paths:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if not all(path.exists() for path in required_paths):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_ORIGIN_SCALE_VALUES_PACKET_BLOCKED_MISSING_FILES")
        return 0

    df = pd.read_csv(VALUES)
    add("required_columns_present", REQUIRED_COLUMNS.issubset(set(df.columns)))
    if REQUIRED_COLUMNS.issubset(set(df.columns)):
        add("basis_axis_unique", df["basis_axis"].is_unique)
        add("value_source_nonempty", df["value_source"].astype(str).str.strip().ne("").all())
        add("provenance_nonempty", df["provenance"].astype(str).str.strip().ne("").all())
        origin = pd.to_numeric(df["origin_value"], errors="coerce")
        scale = pd.to_numeric(df["scale_value"], errors="coerce")
        add("origin_value_finite", origin.map(math.isfinite).all())
        add("scale_value_finite", scale.map(math.isfinite).all())
        add("scale_value_nonzero", scale.ne(0).all())

    expected_hash = SHA256.read_text(encoding="utf-8").strip().split()[0]
    actual_hash = file_sha256(VALUES)
    add("sha256_matches_origin_scale_values", expected_hash == actual_hash)

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    for key, expected in FORBIDDEN_MANIFEST_FLAGS.items():
        add(f"manifest_{key}_is_false", manifest.get(key) is expected)

    leak = pd.read_csv(LEAKAGE)
    add("leakage_audit_has_passed_column", "Passed" in leak.columns)
    add("leakage_audit_required_checks_pass", "Passed" in leak.columns and leak["Passed"].map(bool_from_csv).all())

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_ORIGIN_SCALE_VALUES_PACKET_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_ORIGIN_SCALE_VALUES_PACKET_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
