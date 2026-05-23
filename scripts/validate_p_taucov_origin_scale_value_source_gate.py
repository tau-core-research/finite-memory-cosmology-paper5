#!/usr/bin/env python3
"""Validate the P-TauCov origin/scale value-source packet gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_origin_scale_value_source_gate.md"
CSV = ROOT / "evidence/p_taucov_origin_scale_value_source_gate.csv"
SUMMARY = ROOT / "evidence/p_taucov_origin_scale_value_source_gate_summary.csv"
OUT = ROOT / "evidence/p_taucov_origin_scale_value_source_gate_validation.csv"

REQUIRED_FILES = {
    "data/p_taucov/linear/origin_scale_values.csv",
    "evidence/p_taucov_origin_scale_values_manifest.yaml",
    "evidence/p_taucov_origin_scale_values.sha256",
    "evidence/p_taucov_origin_scale_values_leakage_audit.csv",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_ORIGIN_SCALE_VALUE_SOURCE_GATE_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_ORIGIN_SCALE_VALUE_SOURCE_GATE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_files_declared", REQUIRED_FILES.issubset(set(df["Path"])))
    add("all_files_marked_required", df["Required"].astype(bool).all())
    add("no_concrete_values_supplied", not df["ConcreteValuesSupplied"].astype(bool).any())
    add("basis_packet_not_authorized", not df["CoordinateBasisPacketAuthorized"].astype(bool).any())
    add("reference_domain_not_selectable", not df["ReferenceDomainSelectable"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_gate_declared", bool(summary["ValueSourceGateDeclared"].iloc[0]))
    add("summary_no_values", not bool(summary["ConcreteValuesSupplied"].iloc[0]))
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "basis_axis",
        "origin_value",
        "scale_value",
        "OutcomeInformationUsed=false",
        "ResidualInformationUsed=false",
        "ScoreInformationUsed=false",
        "PostScoringLocalizationUsed=false",
        "Concrete origin/scale values or a coordinate-basis packet are available",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_ORIGIN_SCALE_VALUE_SOURCE_GATE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_ORIGIN_SCALE_VALUE_SOURCE_GATE_VALID_VALUES_NOT_SUPPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
