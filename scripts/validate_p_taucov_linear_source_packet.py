#!/usr/bin/env python3
"""Validate the minimal target-blind P-TauCov linear-source packet."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
P_RED = ROOT / "data/p_taucov/linear/p_red.csv"
SOURCE_DIR = ROOT / "data/p_taucov/linear/source"
MANIFEST = ROOT / "evidence/p_taucov_linear_source_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_linear_source.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_linear_source_leakage_audit.csv"
DOC = ROOT / "docs/p_taucov_linear_source_packet.md"
OUT = ROOT / "evidence/p_taucov_linear_source_packet_validation.csv"

SOURCE_FILES = {
    "K_B": SOURCE_DIR / "K_B.csv",
    "Gamma_B": SOURCE_DIR / "Gamma_B.csv",
    "D_Phi_K_B": SOURCE_DIR / "D_Phi_K_B.csv",
    "D_Phi_J_B": SOURCE_DIR / "D_Phi_J_B.csv",
    "G_Phi": SOURCE_DIR / "G_Phi.csv",
    "G_B": SOURCE_DIR / "G_B.csv",
    "P0_SOURCE": SOURCE_DIR / "P0_source.csv",
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


def matrix_equals(a: pd.DataFrame, b: pd.DataFrame, ids: list[str]) -> bool:
    return a[ids].astype(float).equals(b[ids].astype(float))


def matrix_is_zero(a: pd.DataFrame, ids: list[str]) -> bool:
    return (a[ids].astype(float) == 0.0).all().all()


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_SOURCE_PACKET_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required_paths = [BASIS, P_RED, MANIFEST, SHA256, LEAKAGE, DOC] + list(SOURCE_FILES.values())
    for path in required_paths:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if not all(path.exists() for path in required_paths):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_SOURCE_PACKET_BLOCKED_MISSING_FILES")
        return 0

    basis = pd.read_csv(BASIS)
    ids = basis["coordinate_id"].astype(str).tolist()
    p_red = read_matrix(P_RED, ids)
    matrices = {key: read_matrix(path, ids) for key, path in SOURCE_FILES.items()}

    for key in ["K_B", "D_Phi_J_B", "G_Phi", "G_B", "P0_SOURCE"]:
        add(f"{key}_equals_P_red", matrix_equals(matrices[key], p_red, ids))
    for key in ["Gamma_B", "D_Phi_K_B"]:
        add(f"{key}_is_zero", matrix_is_zero(matrices[key], ids))

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    add("manifest_sources_frozen", manifest.get("SourceObjectsFrozen") is True)
    add("manifest_linear_derivable", manifest.get("LinearObjectsDerivable") is True)
    add("manifest_no_metric_eval", manifest.get("MetricEvaluationAuthorized") is False)
    add("manifest_no_scoring", manifest.get("PTauCovScoringAuthorized") is False)
    add("manifest_no_outcome", manifest.get("OutcomeInformationUsed") is False)
    add("manifest_no_residual", manifest.get("ResidualInformationUsed") is False)
    add("manifest_no_score", manifest.get("ScoreInformationUsed") is False)
    add("manifest_no_post_scoring", manifest.get("PostScoringLocalizationUsed") is False)

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    for path in SOURCE_FILES.values():
        rel = str(path.relative_to(ROOT))
        add(f"sha256_{rel}", hash_map.get(rel) == file_sha256(path))

    leak = pd.read_csv(LEAKAGE)
    add("leakage_audit_has_passed_column", "Passed" in leak.columns)
    add("leakage_audit_required_checks_pass", "Passed" in leak.columns and leak["Passed"].map(bool_from_csv).all())

    text = DOC.read_text(encoding="utf-8")
    for phrase in [
        "K_B        = P_red",
        "Gamma_B    = 0",
        "D_Phi_K_B  = 0",
        "P0_SOURCE  = P_red",
        "not empirical evidence",
        "Derived linear objects, covariance response",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_SOURCE_PACKET_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_SOURCE_PACKET_VALID_BASELINE_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
