#!/usr/bin/env python3
"""Validate the epsilon-P3 P-TauCov freeze manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_freeze_manifest.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest_summary.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest_validation.csv"


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
                "AuditID": "P_TAUCOV_EPSILON_P3_FREEZE_MANIFEST_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [DOC, MANIFEST, SHA256, SUMMARY]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [DOC, MANIFEST, SHA256, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_FREEZE_MANIFEST_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    summary = pd.read_csv(SUMMARY)
    text = DOC.read_text(encoding="utf-8")

    add("freeze_status_frozen", manifest.get("FreezeStatus") == "FROZEN_SPECIFICITY_CANDIDATE_NO_SCORING")
    add("candidate_frozen", manifest.get("CandidateFrozen") is True)
    add("candidate_epsilon_p3", manifest.get("FrozenCandidate") == "epsilon_P3_core_mixing")
    add("specificity_passed", manifest.get("SpecificityPrescoreStatus") == "PASS_NOT_FROZEN")
    add("metrics_passed", manifest.get("SpecificityMetricsPassed") is True)
    add("no_target_residuals", manifest.get("TargetResidualsUsed") is False)
    add("no_p5c_outcome", manifest.get("P5CV3OutcomeUsed") is False)
    add("scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add("no_authorization_artifact", manifest.get("ScoringAuthorizationArtifactExists") is False)
    add("forbidden_next_step_blocks_scoring", "run_empirical_scoring" in str(manifest.get("ForbiddenNextStep", "")))

    for key, rel in manifest.get("InputFiles", {}).items():
        path = ROOT / rel
        add(f"input_exists_{key}", path.exists())
        if path.exists():
            add(f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == file_sha256(path))

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    rel_manifest = str(MANIFEST.relative_to(ROOT))
    add("manifest_sha256", hash_map.get(rel_manifest) == file_sha256(MANIFEST))
    add("summary_candidate_frozen", bool_from_csv(summary["CandidateFrozen"].iloc[0]))
    add("summary_no_scoring", not bool_from_csv(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "FROZEN_SPECIFICITY_CANDIDATE_NO_SCORING",
        "P3 core-mixing",
        "MetricsPassed: 6/6",
        "Forbidden statement",
        "separate scoring-authorization protocol",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_FREEZE_MANIFEST_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_FREEZE_MANIFEST_VALID_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
