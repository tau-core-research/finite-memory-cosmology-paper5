#!/usr/bin/env python3
"""Validate the P-TauCov finite-dimensional symbolic axis map."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_symbolic_axis_map.md"
CSV = ROOT / "evidence/p_taucov_symbolic_axis_map.csv"
SUMMARY = ROOT / "evidence/p_taucov_symbolic_axis_map_summary.csv"
OUT = ROOT / "evidence/p_taucov_symbolic_axis_map_validation.csv"

REQUIRED_AXES = {
    "PHI_PARENT_SOURCE",
    "B_BRANCH_RESPONSE",
    "M_PARENT_MORPHOLOGY",
    "P_MORPH_PROJECTION",
    "COORD_ORIGIN_CENTER",
    "COORD_SCALE_UNIT",
    "EXT_SOURCE_FAMILY",
    "EXT_OBSERVING_CONTEXT",
}

ALLOWED_SOURCE_CLASSES = {
    "TauSideSymbolicDefinition",
    "CoordinateConventionOnly",
    "PublishedExternalMetadata",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_SYMBOLIC_AXIS_MAP_VALIDATION",
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
        print("P_TAUCOV_SYMBOLIC_AXIS_MAP_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_axes_present", REQUIRED_AXES.issubset(set(df["AxisID"])))
    add("axis_ids_unique", df["AxisID"].is_unique)
    add("source_classes_allowed", set(df["AllowedSourceClass"]).issubset(ALLOWED_SOURCE_CLASSES))
    add("all_axes_may_enter_basis", df["MayEnterCoordinateBasis"].astype(bool).all())
    add("no_numeric_values", not df["NumericValueSupplied"].astype(bool).any())
    add("no_matrix_elements", not df["MatrixElementSupplied"].astype(bool).any())
    add("no_residual_or_score_use", not df["UsesResidualOrScore"].astype(bool).any())
    add("basis_packet_not_authorized", not df["CoordinateBasisPacketAuthorized"].astype(bool).any())
    add("reference_domain_not_selectable", not df["ReferenceDomainSelectable"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_no_numeric_values", int(summary["NumericValuesSupplied"].iloc[0]) == 0)
    add("summary_no_matrix_elements", int(summary["MatrixElementsSupplied"].iloc[0]) == 0)
    add("summary_no_residual_or_score", not bool(summary["ResidualOrScoreUse"].iloc[0]))
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "finite-dimensional symbolic axis map",
        "PHI_PARENT_SOURCE",
        "B_BRANCH_RESPONSE",
        "P5C v3 gains",
        "held-out residuals",
        "The concrete coordinate basis, matrices, or P-TauCov covariance response are",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_SYMBOLIC_AXIS_MAP_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_SYMBOLIC_AXIS_MAP_VALID_NO_NUMERIC_BASIS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
