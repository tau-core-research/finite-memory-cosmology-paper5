#!/usr/bin/env python3
"""Validate the P-TauCov coordinate/source basis schema."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_coordinate_basis_schema.md"
CSV = ROOT / "evidence/p_taucov_coordinate_basis_schema.csv"
SUMMARY = ROOT / "evidence/p_taucov_coordinate_basis_schema_summary.csv"
OUT = ROOT / "evidence/p_taucov_coordinate_basis_schema_validation.csv"

REQUIRED_FIELDS = {
    "coordinate_id",
    "coordinate_family",
    "coordinate_kind",
    "basis_axis",
    "origin_value",
    "scale_value",
    "is_null_candidate",
    "is_gauge_candidate",
    "is_forbidden_candidate",
    "provenance",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_SCHEMA_VALIDATION",
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
        print("P_TAUCOV_COORDINATE_BASIS_SCHEMA_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_fields_present", REQUIRED_FIELDS.issubset(set(df["Field"])))
    add("all_rows_marked_required", df["Required"].astype(bool).all())
    add("no_concrete_basis_supplied", not df["ConcreteBasisSupplied"].astype(bool).any())
    add("reference_domain_not_selectable", not df["ReferenceDomainSelectable"].astype(bool).any())
    add("linear_packet_not_authorized", not df["LinearPacketAuthorized"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_schema_declared", bool(summary["SchemaDeclared"].iloc[0]))
    add("summary_no_basis", not bool(summary["ConcreteBasisSupplied"].iloc[0]))
    add("summary_reference_domain_not_selectable", not bool(summary["ReferenceDomainSelectable"].iloc[0]))
    add("summary_domain_not_frozen", not bool(summary["ReducedDomainFrozen"].iloc[0]))
    add("summary_no_linear_packet_authorization", not bool(summary["LinearPacketAuthorized"].iloc[0]))
    add("summary_no_metric_authorization", not bool(summary["MetricEvaluationAuthorized"].iloc[0]))
    add("summary_no_scoring_authorization", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "data/p_taucov/linear/coordinate_basis.csv",
        "evidence/p_taucov_coordinate_basis_manifest.yaml",
        "evidence/p_taucov_coordinate_basis.sha256",
        "evidence/p_taucov_coordinate_basis_leakage_audit.csv",
        "no forbidden target, score, residual, or post-scoring source is used",
        "A concrete P-TauCov coordinate basis or reference domain is frozen",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_COORDINATE_BASIS_SCHEMA_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_COORDINATE_BASIS_SCHEMA_VALID_NO_BASIS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
