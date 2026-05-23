#!/usr/bin/env python3
"""Validate the non-authorizing P-TauCov coordinate-basis skeleton."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_coordinate_basis_skeleton.md"
TEMPLATE = ROOT / "data/p_taucov/templates/coordinate_basis_skeleton.csv"
SUMMARY = ROOT / "evidence/p_taucov_coordinate_basis_skeleton_summary.csv"
OUT = ROOT / "evidence/p_taucov_coordinate_basis_skeleton_validation.csv"

REQUIRED_COLUMNS = {
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
    "TemplateOnly",
    "NumericValueSupplied",
    "CoordinateBasisPacketAuthorized",
    "ReferenceDomainSelectable",
    "MetricEvaluationAuthorized",
    "PTauCovScoringAuthorized",
}

PLACEHOLDER = "TO_BE_FILLED_BY_TARGET_BLIND_PACKET"


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_SKELETON_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("template_exists", TEMPLATE.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, TEMPLATE, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_COORDINATE_BASIS_SKELETON_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    template = pd.read_csv(TEMPLATE)
    summary = pd.read_csv(SUMMARY)

    add("required_columns_present", REQUIRED_COLUMNS.issubset(set(template.columns)))
    add("coordinate_ids_unique", template["coordinate_id"].is_unique)
    add("template_only_all_rows", template["TemplateOnly"].astype(bool).all())
    add("origin_placeholders_present", template["origin_value"].astype(str).eq(PLACEHOLDER).all())
    add("scale_placeholders_present", template["scale_value"].astype(str).eq(PLACEHOLDER).all())
    add("no_numeric_values", not template["NumericValueSupplied"].astype(bool).any())
    add("basis_packet_not_authorized", not template["CoordinateBasisPacketAuthorized"].astype(bool).any())
    add("reference_domain_not_selectable", not template["ReferenceDomainSelectable"].astype(bool).any())
    add("metric_eval_not_authorized", not template["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not template["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_template_only", bool(summary["TemplateOnly"].iloc[0]))
    add("summary_no_numeric_values", int(summary["NumericValuesSupplied"].iloc[0]) == 0)
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "data/p_taucov/templates/coordinate_basis_skeleton.csv",
        "not at the packet path",
        "TO_BE_FILLED_BY_TARGET_BLIND_PACKET",
        "must not be accepted",
        "coordinate-basis packet",
        "The concrete coordinate basis has been supplied, accepted, or frozen",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_COORDINATE_BASIS_SKELETON_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_COORDINATE_BASIS_SKELETON_VALID_TEMPLATE_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
