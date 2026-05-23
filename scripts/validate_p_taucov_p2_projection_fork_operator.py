#!/usr/bin/env python3
"""Validate the target-blind P2 projection-fork operator packet."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
P2 = ROOT / "data/p_taucov/linear/P2_projection_fork_operator.csv"
DOC = ROOT / "docs/p_taucov_p2_projection_fork_operator.md"
MANIFEST = ROOT / "evidence/p_taucov_p2_projection_fork_operator_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_p2_projection_fork_operator.sha256"
METRICS = ROOT / "evidence/p_taucov_p2_projection_fork_operator_metrics.csv"
LEAKAGE = ROOT / "evidence/p_taucov_p2_projection_fork_operator_leakage_audit.csv"
P1_SUMMARY = ROOT / "evidence/p_taucov_epsilon_p_specificity_prescore_summary.csv"
OUT = ROOT / "evidence/p_taucov_p2_projection_fork_operator_validation.csv"


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
                "AuditID": "P_TAUCOV_P2_PROJECTION_FORK_OPERATOR_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required = [P2, DOC, MANIFEST, SHA256, METRICS, LEAKAGE, P1_SUMMARY]
    for path in required:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in required):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_P2_PROJECTION_FORK_OPERATOR_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    metrics = pd.read_csv(METRICS)
    leakage = pd.read_csv(LEAKAGE)
    p1_summary = pd.read_csv(P1_SUMMARY)
    text = DOC.read_text(encoding="utf-8")

    add("p1_failed_not_specific", p1_summary["Status"].iloc[0] == "FAIL_EPSILON_P_NOT_SPECIFIC")
    add("manifest_p2_frozen", manifest.get("P2OperatorFrozen") is True)
    add("manifest_no_metric_eval", manifest.get("MetricEvaluationAuthorized") is False)
    add("manifest_no_scoring", manifest.get("PTauCovScoringAuthorized") is False)
    add("manifest_no_outcome", manifest.get("OutcomeInformationUsed") is False)
    add("manifest_no_residual", manifest.get("ResidualInformationUsed") is False)
    add("manifest_no_score", manifest.get("ScoreInformationUsed") is False)
    add("manifest_no_p5c", manifest.get("P5CV3OutcomeUsed") is False)
    metric_pass = dict(zip(metrics["MetricID"].astype(str), metrics["Pass"].map(bool_from_csv)))
    for metric_id in [
        "P2_FROBENIUS_NORM",
        "P2_COMMUTATOR_WITH_P_RED_FROBENIUS",
        "P2_DELTA_OFFDIAGONAL_SHARE",
        "P2_LABEL_PROXY_OVERLAP",
        "P2_STRUCTURAL_NULL_MARGIN",
    ]:
        add(f"critical_metric_pass_{metric_id}", metric_pass.get(metric_id, False))
    add("support_entropy_recorded_as_caveat", "P2_SUPPORT_ENTROPY" in metric_pass)
    add("leakage_pass", leakage["Passed"].map(bool_from_csv).all())

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    for path in [P2, MANIFEST, METRICS]:
        rel = str(path.relative_to(ROOT))
        add(f"sha256_{rel}", hash_map.get(rel) == file_sha256(path))

    p2 = pd.read_csv(P2)
    numeric = p2[[col for col in p2.columns if col != "coordinate_id"]].astype(float)
    add("p2_has_three_nonzero_entries", int((numeric != 0.0).sum().sum()) == 3)
    add("p2_has_zero_diagonal", (numeric.values.diagonal() == 0.0).all())

    for phrase in [
        "parent source -> projection coordinate",
        "parent source -> morphology coordinate",
        "projection coordinate -> morphology coordinate",
        "1/sqrt(3)",
        "off-diagonal covariance component",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_P2_PROJECTION_FORK_OPERATOR_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_P2_PROJECTION_FORK_OPERATOR_VALID_NO_MODEL_PACKET_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
