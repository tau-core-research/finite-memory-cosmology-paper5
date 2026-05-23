#!/usr/bin/env python3
"""Validate the derived target-blind P-TauCov linear-object packet."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
P_RED = ROOT / "data/p_taucov/linear/p_red.csv"
DOC = ROOT / "docs/p_taucov_linear_object_packet.md"
MANIFEST = ROOT / "evidence/p_taucov_linear_object_derivation_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_linear_object_derivation.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_linear_object_derivation_leakage_audit.csv"
OUT = ROOT / "evidence/p_taucov_linear_object_packet_validation.csv"

OBJECT_FILES = {
    "L0_B": ROOT / "data/p_taucov/linear/L0_B.csv",
    "R_B": ROOT / "data/p_taucov/linear/R_B.csv",
    "A_Phi": ROOT / "data/p_taucov/linear/A_Phi.csv",
    "A_B": ROOT / "data/p_taucov/linear/A_B.csv",
    "P0": ROOT / "data/p_taucov/linear/P0.csv",
}

EXPECTED_SIGNS = {
    "L0_B": 1.0,
    "R_B": -1.0,
    "A_Phi": 1.0,
    "A_B": 1.0,
    "P0": 1.0,
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


def read_matrix(path: Path, ids: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected = ["coordinate_id"] + ids
    if list(df.columns) != expected:
        raise ValueError(f"Unexpected columns in {path}")
    return df


def signed_matrix_equals(a: pd.DataFrame, p_red: pd.DataFrame, ids: list[str], sign: float) -> bool:
    left = a[ids].astype(float).round(12)
    right = (sign * p_red[ids].astype(float)).round(12)
    return left.equals(right)


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_OBJECT_PACKET_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required_paths = [P_RED, DOC, MANIFEST, SHA256, LEAKAGE] + list(OBJECT_FILES.values())
    for path in required_paths:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if not all(path.exists() for path in required_paths):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_OBJECT_PACKET_BLOCKED_MISSING_FILES")
        return 0

    p_red_raw = pd.read_csv(P_RED)
    ids = [col for col in p_red_raw.columns if col != "coordinate_id"]
    p_red = read_matrix(P_RED, ids)
    matrices = {key: read_matrix(path, ids) for key, path in OBJECT_FILES.items()}

    for key, sign in EXPECTED_SIGNS.items():
        add(f"{key}_equals_{sign:g}_P_red", signed_matrix_equals(matrices[key], p_red, ids, sign))

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    add("manifest_linear_objects_frozen", manifest.get("LinearObjectsFrozen") is True)
    add("manifest_model_packet_ready", manifest.get("LinearModelPacketReady") is True)
    add("manifest_no_metric_eval", manifest.get("MetricEvaluationAuthorized") is False)
    add("manifest_no_scoring", manifest.get("PTauCovScoringAuthorized") is False)
    add("manifest_no_outcome", manifest.get("OutcomeInformationUsed") is False)
    add("manifest_no_residual", manifest.get("ResidualInformationUsed") is False)
    add("manifest_no_score", manifest.get("ScoreInformationUsed") is False)
    add("manifest_no_post_scoring", manifest.get("PostScoringLocalizationUsed") is False)

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    for path in OBJECT_FILES.values():
        rel = str(path.relative_to(ROOT))
        add(f"sha256_{rel}", hash_map.get(rel) == file_sha256(path))

    leak = pd.read_csv(LEAKAGE)
    add("leakage_audit_has_passed_column", "Passed" in leak.columns)
    add("leakage_audit_required_checks_pass", "Passed" in leak.columns and leak["Passed"].map(bool_from_csv).all())

    text = DOC.read_text(encoding="utf-8")
    for phrase in [
        "L0_B  = P_red",
        "R_B   = -P_red",
        "not empirical evidence",
        "positive P-TauCov result",
        "Metric evaluation, covariance response, or P-TauCov scoring is authorized.",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_OBJECT_PACKET_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_OBJECT_PACKET_VALID_BASELINE_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
