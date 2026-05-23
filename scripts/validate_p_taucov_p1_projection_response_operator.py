#!/usr/bin/env python3
"""Validate the target-blind P1 projection-response operator packet."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT / "data/p_taucov/linear/P1_projection_response_operator.csv"
DOC = ROOT / "docs/p_taucov_p1_projection_response_operator.md"
MANIFEST = ROOT / "evidence/p_taucov_p1_projection_response_operator_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_p1_projection_response_operator.sha256"
METRICS = ROOT / "evidence/p_taucov_p1_projection_response_operator_metrics.csv"
LEAKAGE = ROOT / "evidence/p_taucov_p1_projection_response_operator_leakage_audit.csv"
ROUTE_FREEZE = ROOT / "evidence/p_taucov_minimal_nonzero_route_freeze_summary.csv"
OUT = ROOT / "evidence/p_taucov_p1_projection_response_operator_validation.csv"


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
                "AuditID": "P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required_paths = [P1, DOC, MANIFEST, SHA256, METRICS, LEAKAGE, ROUTE_FREEZE]
    for path in required_paths:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in required_paths):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    route = pd.read_csv(ROUTE_FREEZE)
    metrics = pd.read_csv(METRICS)
    leakage = pd.read_csv(LEAKAGE)
    text = DOC.read_text(encoding="utf-8")

    add("route_freeze_epsilon_p_first", route["FrozenPrimaryRoute"].iloc[0] == "EPSILON_P_PROJECTION_RESPONSE_PRIMARY")
    add("manifest_p1_frozen", manifest.get("P1OperatorFrozen") is True)
    add("manifest_model_packet_not_updated", manifest.get("LinearModelPacketUpdated") is False)
    add("manifest_metric_eval_not_authorized", manifest.get("MetricEvaluationAuthorized") is False)
    add("manifest_scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add("manifest_no_outcome", manifest.get("OutcomeInformationUsed") is False)
    add("manifest_no_residual", manifest.get("ResidualInformationUsed") is False)
    add("manifest_no_score", manifest.get("ScoreInformationUsed") is False)
    add("manifest_no_p5c", manifest.get("P5CV3OutcomeUsed") is False)

    add("all_metrics_pass", metrics["Pass"].map(bool_from_csv).all())
    expected_metrics = {
        "P1_FROBENIUS_NORM",
        "P1_COMMUTATOR_WITH_P_RED_FROBENIUS",
        "P1_DIAGONAL_ENERGY_SHARE",
        "P1_PROJECTION_AXIS_ENERGY_SHARE",
    }
    add("expected_metrics_present", expected_metrics.issubset(set(metrics["MetricID"])))
    add("leakage_audit_pass", leakage["Passed"].map(bool_from_csv).all())

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    for path in [P1, MANIFEST, METRICS]:
        rel = str(path.relative_to(ROOT))
        add(f"sha256_{rel}", hash_map.get(rel) == file_sha256(path))

    df = pd.read_csv(P1)
    add("p1_has_coordinate_id", "coordinate_id" in df.columns)
    numeric = df[[col for col in df.columns if col != "coordinate_id"]].astype(float)
    add("p1_has_two_nonzero_entries", int((numeric != 0.0).sum().sum()) == 2)
    add("p1_has_zero_diagonal", (numeric.values.diagonal() == 0.0).all())

    for phrase in [
        "parent source -> projection coordinate -> morphology coordinate",
        "1/sqrt(2)",
        "nonzero commutator with P_red",
        "derived from target residuals",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_VALID_NO_MODEL_PACKET_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
