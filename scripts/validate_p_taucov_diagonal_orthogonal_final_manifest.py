#!/usr/bin/env python3
"""Validate diagonal-orthogonal P-TauCov final manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence/p_taucov_diagonal_orthogonal_final_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_diagonal_orthogonal_final_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_diagonal_orthogonal_final_manifest_summary.csv"
DOC = ROOT / "docs/p_taucov_diagonal_orthogonal_final_manifest.md"
OUT = ROOT / "evidence/p_taucov_diagonal_orthogonal_final_manifest_validation.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_DIAGONAL_ORTHOGONAL_FINAL_MANIFEST_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [MANIFEST, SHA256, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [MANIFEST, SHA256, SUMMARY, DOC]):
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        recorded = SHA256.read_text(encoding="utf-8").split()[0]
        add("status_authorized", manifest.get("Status") == "P_TAUCOV_DIAGONAL_ORTHOGONAL_ALIGNMENT_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM")
        add("summary_authorized", bool(summary["DiagonalOrthogonalScoringAuthorized"]) is True)
        add("covariance_survival_not_authorized", manifest.get("CovarianceSurvivalClaimAuthorized") is False)
        add("tau_validation_not_authorized", manifest.get("TauCoreValidationClaimAuthorized") is False)
        add("measurement_not_authorized", manifest.get("MeasurementValidationAuthorized") is False)
        add("scope_correct", manifest.get("AuthorizedScope") == "diagonal_orthogonal_signed_alignment_scorecard_only")
        add("manifest_sha_valid", recorded == sha256(MANIFEST))
        for key, rel in manifest.get("InputFiles", {}).items():
            path = ROOT / rel
            add(f"input_exists_{key}", path.exists())
            if path.exists():
                add(f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == sha256(path))
        add("doc_boundary", "does not authorize covariance-survival" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_DIAGONAL_ORTHOGONAL_FINAL_MANIFEST_VALID" if ok else "P_TAUCOV_DIAGONAL_ORTHOGONAL_FINAL_MANIFEST_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
