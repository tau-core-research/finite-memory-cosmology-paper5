#!/usr/bin/env python3
"""Validate compact spectral final manifest."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence/p_taucov_compact_spectral_final_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_compact_spectral_final_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_final_manifest_summary.csv"
DOC = ROOT / "docs/p_taucov_compact_spectral_final_manifest.md"
OUT = ROOT / "evidence/p_taucov_compact_spectral_final_manifest_validation.csv"

AUDIT_ID = "P_TAUCOV_COMPACT_SPECTRAL_FINAL_MANIFEST_VALIDATION"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [MANIFEST, SHA256, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [MANIFEST, SHA256, SUMMARY, DOC]):
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        input_status = manifest.get("InputStatus", {})
        input_hash = manifest.get("InputSHA256", {})
        required_hash = manifest.get("RequiredSHA256", {})
        add("status_authorized_no_survival", str(summary["Status"]) == "P_TAUCOV_COMPACT_SPECTRAL_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM")
        add("scoring_authorized_true", bool(summary["PTauCovScoringAuthorized"]) is True)
        add("survival_false", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_false", bool(summary["MeasurementValidationAuthorized"]) is False)
        add("tau_validation_false", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("scope_primary_only", str(summary["AuthorizedScope"]) == "compact_spectral_primary_covariance_scorecard_only")
        add("source_validation_passes", bool(manifest.get("SourceValidationPasses")) is True)
        add("input_statuses_present", len(input_status) >= 7)
        add("input_hashes_present", len(input_hash) >= 8)
        add("required_hashes_present", {"source_object", "source_spectrum", "scorecard_script"}.issubset(set(required_hash)))
        add("manifest_sha_file_points_to_manifest", "p_taucov_compact_spectral_final_manifest.yaml" in SHA256.read_text(encoding="utf-8"))
        add("doc_forbids_validation_claim", "does not authorize survival language" in doc and "Tau Core validation claim" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_COMPACT_SPECTRAL_FINAL_MANIFEST_VALID" if ok else "P_TAUCOV_COMPACT_SPECTRAL_FINAL_MANIFEST_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
