#!/usr/bin/env python3
"""Validate the target-blind P-TauCov linear model packet."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_model_packet.md"
MANIFEST = ROOT / "evidence/p_taucov_linear_model_packet.yaml"
SHA256 = ROOT / "evidence/p_taucov_linear_model_packet.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_linear_model_packet_leakage_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_model_packet_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_model_packet_validation.csv"

REQUIRED_KEYS = {
    "coordinate_basis",
    "phi_0",
    "p_red",
    "K_B",
    "Gamma_B",
    "D_Phi_J_B",
    "L0_B",
    "R_B",
    "A_Phi",
    "A_B",
    "P0",
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
                "AuditID": "P_TAUCOV_LINEAR_MODEL_PACKET_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required_paths = [DOC, MANIFEST, SHA256, LEAKAGE, SUMMARY]
    for path in required_paths:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if not all(path.exists() for path in required_paths):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_MODEL_PACKET_BLOCKED_MISSING_FILES")
        return 0

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    input_files = manifest.get("InputFiles", {})
    input_hashes = manifest.get("InputSHA256", {})

    add("required_input_keys_present", REQUIRED_KEYS.issubset(set(input_files)))
    for key, rel in input_files.items():
        path = ROOT / rel
        add(f"input_exists_{key}", path.exists())
        if path.exists():
            add(f"input_hash_{key}", input_hashes.get(key) == file_sha256(path))

    add("lambda_B_zero", manifest.get("lambda_B") == 0)
    add("epsilon_P_zero", manifest.get("epsilon_P") == 0)
    add("linear_model_packet_frozen", manifest.get("LinearModelPacketFrozen") is True)
    add("specificity_audit_authorized", manifest.get("LinearSpecificityAuditAuthorized") is True)
    add("metric_evaluation_authorized", manifest.get("MetricEvaluationAuthorized") is True)
    add("p_taucov_scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add("no_outcome", manifest.get("OutcomeInformationUsed") is False)
    add("no_residual", manifest.get("ResidualInformationUsed") is False)
    add("no_score", manifest.get("ScoreInformationUsed") is False)
    add("no_p5c_v3_outcome", manifest.get("P5CV3OutcomeUsed") is False)
    add("no_post_scoring", manifest.get("PostScoringLocalizationUsed") is False)

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    rel_manifest = str(MANIFEST.relative_to(ROOT))
    add("manifest_sha256", hash_map.get(rel_manifest) == file_sha256(MANIFEST))

    leak = pd.read_csv(LEAKAGE)
    add("leakage_audit_has_passed_column", "Passed" in leak.columns)
    add("leakage_audit_required_checks_pass", "Passed" in leak.columns and leak["Passed"].map(bool_from_csv).all())

    summary = pd.read_csv(SUMMARY)
    add("summary_linear_model_packet_frozen", bool_from_csv(summary["LinearModelPacketFrozen"].iloc[0]))
    add("summary_specificity_audit_authorized", bool_from_csv(summary["LinearSpecificityAuditAuthorized"].iloc[0]))
    add("summary_no_scoring", not bool_from_csv(summary["PTauCovScoringAuthorized"].iloc[0]))

    text = DOC.read_text(encoding="utf-8")
    for phrase in [
        "lambda_B = 0",
        "epsilon_P = 0",
        "specificity",
        "does not authorize P-TauCov scoring",
        "empirical Tau-signal claims",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_MODEL_PACKET_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_MODEL_PACKET_VALID_SPECIFICITY_ONLY_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
