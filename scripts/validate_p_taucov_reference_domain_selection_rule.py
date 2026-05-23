#!/usr/bin/env python3
"""Validate the P-TauCov target-blind reference-domain selection rule."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_reference_domain_selection_rule.md"
CSV = ROOT / "evidence/p_taucov_reference_domain_selection_rule.csv"
SUMMARY = ROOT / "evidence/p_taucov_reference_domain_selection_rule_summary.csv"
OUT = ROOT / "evidence/p_taucov_reference_domain_selection_rule_validation.csv"

REQUIRED_OBJECTS = {
    "Phi_0",
    "B_star_at_Phi_0",
    "P_null",
    "P_gauge",
    "P_forbidden",
    "P_red",
}

FORBIDDEN_PHRASES = [
    "held-out residuals",
    "P5C v3 gains",
    "OOS DeltaNLL",
    "linear specificity metric result",
    "post-hoc support localization",
]


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_REFERENCE_DOMAIN_SELECTION_RULE_VALIDATION",
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
        print("P_TAUCOV_REFERENCE_DOMAIN_SELECTION_RULE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_objects_present", REQUIRED_OBJECTS.issubset(set(df["Object"])))
    add("no_concrete_values_set", not df["ConcreteValueSet"].astype(bool).any())
    add("no_outcome_information_allowed", not df["OutcomeInformationAllowed"].astype(bool).any())
    add("linear_packet_not_authorized", not df["LinearPacketAuthorized"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("selection_rule_declared", bool(summary["SelectionRuleDeclared"].iloc[0]))
    add("phi0_not_set", not bool(summary["ConcretePhi0Set"].iloc[0]))
    add("basis_not_set", not bool(summary["ConcreteBasisSet"].iloc[0]))
    add("domain_not_frozen", not bool(summary["ReducedDomainFrozen"].iloc[0]))
    add("summary_no_linear_packet_authorization", not bool(summary["LinearPacketAuthorized"].iloc[0]))
    add("summary_no_metric_authorization", not bool(summary["MetricEvaluationAuthorized"].iloc[0]))
    add("summary_no_scoring_authorization", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "Choose the frozen coordinate-basis origin",
        "otherwise choose the frozen coordinate-basis center",
        "P_red = I - P_null - P_gauge - P_forbidden",
        "input-provenance leakage certificate",
        "The P-TauCov reference state or reduced domain has been frozen",
    ]:
        add(f"doc_contains_{phrase[:36]}", phrase in text)

    for phrase in FORBIDDEN_PHRASES:
        add(f"doc_declares_forbidden_{phrase[:36]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_REFERENCE_DOMAIN_SELECTION_RULE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_REFERENCE_DOMAIN_SELECTION_RULE_VALID_NOT_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
