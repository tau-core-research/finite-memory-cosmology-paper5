#!/usr/bin/env python3
"""Validate a concrete P-TauCov coordinate-basis packet if it exists."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
MANIFEST = ROOT / "evidence/p_taucov_coordinate_basis_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_coordinate_basis.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_coordinate_basis_leakage_audit.csv"
OUT = ROOT / "evidence/p_taucov_coordinate_basis_packet_validation.csv"

REQUIRED_FIELDS = {
    "coordinate_id",
    "coordinate_family",
    "coordinate_kind",
    "basis_axis",
    "origin_value",
    "scale_value",
    "is_null_candidate",
    "is_gauge_candidate",
    "is_forbidden_candidate",
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
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_PACKET_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required_paths = [BASIS, MANIFEST, SHA256, LEAKAGE]
    for path in required_paths:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if not all(path.exists() for path in required_paths):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_COORDINATE_BASIS_PACKET_BLOCKED_MISSING_FILES")
        return 0

    df = pd.read_csv(BASIS)
    add("required_fields_present", REQUIRED_FIELDS.issubset(set(df.columns)))

    if REQUIRED_FIELDS.issubset(set(df.columns)):
        add("coordinate_id_unique", df["coordinate_id"].is_unique)
        add("provenance_nonempty", df["provenance"].astype(str).str.strip().ne("").all())

        origin = pd.to_numeric(df["origin_value"], errors="coerce")
        scale = pd.to_numeric(df["scale_value"], errors="coerce")
        add("origin_value_finite", origin.map(math.isfinite).all())
        add("scale_value_finite", scale.map(math.isfinite).all())
        add("scale_value_nonzero", scale.ne(0).all())

    expected_hash = SHA256.read_text(encoding="utf-8").strip().split()[0]
    actual_hash = file_sha256(BASIS)
    add("sha256_matches_coordinate_basis", expected_hash == actual_hash)

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
        print("P_TAUCOV_COORDINATE_BASIS_PACKET_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_COORDINATE_BASIS_PACKET_VALID_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
