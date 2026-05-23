#!/usr/bin/env python3
"""Validate the P-TauCov linear model packet schema."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_model_packet_schema.md"
CSV = ROOT / "evidence/p_taucov_linear_model_packet_schema.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_model_packet_schema_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_model_packet_schema_validation.csv"

REQUIRED_OBJECTS = {
    "L0_B",
    "R_B",
    "P_red",
    "A_Phi",
    "A_B",
    "P0",
    "coordinate_basis",
    "packet_manifest",
    "packet_sha256",
    "leakage_audit",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_MODEL_PACKET_SCHEMA_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("schema_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_MODEL_PACKET_SCHEMA_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_objects_present", REQUIRED_OBJECTS.issubset(set(df["ObjectID"])))
    add("all_required_before_metric_evaluation", df["RequiredBeforeMetricEvaluation"].astype(bool).all())
    add("no_scoring_authorized", not df["ScoringAuthorized"].astype(bool).any())
    packet_files_present = df["PresentNow"].astype(bool).all()
    add("packet_ready_matches_file_presence", bool(summary["PacketReady"].iloc[0]) == packet_files_present)
    add("metric_evaluation_matches_file_presence", bool(summary["MetricEvaluationAuthorized"].iloc[0]) == packet_files_present)
    add("linear_frozen_matches_file_presence", bool(summary["LinearCandidateFrozen"].iloc[0]) == packet_files_present)
    add("p_taucov_scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    for phrase in [
        "data/p_taucov/linear/L0_B.csv",
        "evidence/p_taucov_linear_model_packet.yaml",
        "lambda_B: 0",
        "epsilon_P: 0",
        "uses_target_residuals: false",
        "P-TauCov score",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_MODEL_PACKET_SCHEMA_INVALID")
        print(failed.to_string(index=False))
        return 1

    if packet_files_present:
        print("P_TAUCOV_LINEAR_MODEL_PACKET_SCHEMA_VALID_PACKET_PRESENT_NO_SCORING")
    else:
        print("P_TAUCOV_LINEAR_MODEL_PACKET_SCHEMA_VALID_PACKET_MISSING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
