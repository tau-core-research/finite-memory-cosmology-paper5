#!/usr/bin/env python3
"""Validate the target-blind epsilon_P/P3 model packet."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_model_packet.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_model_packet.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_model_packet.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_epsilon_p3_model_packet_leakage_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_model_packet_summary.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_model_packet_validation.csv"


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
                "AuditID": "P_TAUCOV_EPSILON_P3_MODEL_PACKET_VALIDATION",
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
        print("P_TAUCOV_EPSILON_P3_MODEL_PACKET_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    for key, rel in manifest.get("InputFiles", {}).items():
        path = ROOT / rel
        add(f"input_exists_{key}", path.exists())
        if path.exists():
            add(f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == file_sha256(path))

    add("model_family_p3", manifest.get("ModelFamily") == "epsilon_P_core_mixing_response")
    add("lambda_B_zero", manifest.get("lambda_B") == 0)
    add("epsilon_P_one", manifest.get("epsilon_P") == 1)
    add("p2_failed", manifest.get("ParentP2Status") == "FAIL_EPSILON_P2_NOT_SPECIFIC")
    add("p3_packet_frozen", manifest.get("EpsilonP3ModelPacketFrozen") is True)
    add("specificity_authorized", manifest.get("LinearSpecificityAuditAuthorized") is True)
    add("metric_eval_authorized", manifest.get("MetricEvaluationAuthorized") is True)
    add("scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add("no_outcome", manifest.get("OutcomeInformationUsed") is False)
    add("no_residual", manifest.get("ResidualInformationUsed") is False)
    add("no_score", manifest.get("ScoreInformationUsed") is False)
    add("no_p5c", manifest.get("P5CV3OutcomeUsed") is False)

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    rel_manifest = str(MANIFEST.relative_to(ROOT))
    add("manifest_sha256", hash_map.get(rel_manifest) == file_sha256(MANIFEST))
    add("leakage_pass", pd.read_csv(LEAKAGE)["Passed"].map(bool_from_csv).all())
    summary = pd.read_csv(SUMMARY)
    add("summary_packet_frozen", bool_from_csv(summary["EpsilonP3ModelPacketFrozen"].iloc[0]))
    add("summary_no_scoring", not bool_from_csv(summary["PTauCovScoringAuthorized"].iloc[0]))

    text = DOC.read_text(encoding="utf-8")
    for phrase in [
        "epsilon_P = 1",
        "P_epsilon = P0 + epsilon_P * P3",
        "not a fitted",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_MODEL_PACKET_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_MODEL_PACKET_VALID_SPECIFICITY_ONLY_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
