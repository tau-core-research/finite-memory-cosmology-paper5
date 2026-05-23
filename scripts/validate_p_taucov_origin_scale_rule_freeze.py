#!/usr/bin/env python3
"""Validate the P-TauCov origin/scale rule freeze."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_origin_scale_rule_freeze.md"
CSV = ROOT / "evidence/p_taucov_origin_scale_rule_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_origin_scale_rule_freeze_summary.csv"
OUT = ROOT / "evidence/p_taucov_origin_scale_rule_freeze_validation.csv"

REQUIRED_AXIS_KINDS = {
    "parent",
    "branch",
    "morphology",
    "projection",
    "reference",
    "scale",
    "family",
    "context",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_ORIGIN_SCALE_RULE_FREEZE_VALIDATION",
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
        print("P_TAUCOV_ORIGIN_SCALE_RULE_FREEZE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_axis_kinds_present", REQUIRED_AXIS_KINDS.issubset(set(df["AxisKind"])))
    add("origin_rules_nonempty", df["OriginRule"].astype(str).str.strip().ne("").all())
    add("scale_rules_nonempty", df["ScaleRule"].astype(str).str.strip().ne("").all())
    add("no_concrete_origin_values", not df["ConcreteOriginValueSupplied"].astype(bool).any())
    add("no_concrete_scale_values", not df["ConcreteScaleValueSupplied"].astype(bool).any())
    add("no_outcome_information", not df["UsesOutcomeInformation"].astype(bool).any())
    add("no_residual_information", not df["UsesResidualInformation"].astype(bool).any())
    add("no_score_information", not df["UsesScoreInformation"].astype(bool).any())
    add("basis_packet_not_authorized", not df["CoordinateBasisPacketAuthorized"].astype(bool).any())
    add("reference_domain_not_selectable", not df["ReferenceDomainSelectable"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_rules_frozen", bool(summary["RulesFrozen"].iloc[0]))
    add("summary_no_concrete_values", int(summary["ConcreteOriginValuesSupplied"].iloc[0]) == 0 and int(summary["ConcreteScaleValuesSupplied"].iloc[0]) == 0)
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "The origin/scale selection rules are frozen",
        "Concrete origin/scale values or a coordinate-basis packet are frozen",
        "held-out residuals",
        "P5C v3 gains",
        "post-hoc support localization",
        "identity-projection reference",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_ORIGIN_SCALE_RULE_FREEZE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_ORIGIN_SCALE_RULE_FREEZE_VALID_NO_VALUES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
