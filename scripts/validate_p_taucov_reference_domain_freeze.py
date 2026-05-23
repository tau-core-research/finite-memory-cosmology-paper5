#!/usr/bin/env python3
"""Validate the P-TauCov reference-state/reduced-domain freeze policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_reference_domain_freeze.md"
CSV = ROOT / "evidence/p_taucov_reference_domain_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_reference_domain_freeze_summary.csv"
OUT = ROOT / "evidence/p_taucov_reference_domain_freeze_validation.csv"

REQUIRED_ITEMS = {"Phi_0", "B_star_at_Phi_0", "P_null", "P_gauge", "P_forbidden", "P_red", "InvertibilityAudit"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_REFERENCE_DOMAIN_FREEZE_VALIDATION",
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
        print("P_TAUCOV_REFERENCE_DOMAIN_FREEZE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_items_present", REQUIRED_ITEMS.issubset(set(df["Item"])))
    add("no_concrete_values_present", not df["ConcreteValuePresent"].astype(bool).any())
    add("linear_packet_not_authorized", not df["LinearPacketAuthorized"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["ScoringAuthorized"].astype(bool).any())
    add("reference_not_frozen", not bool(summary["ReferenceStateFrozen"].iloc[0]))
    add("domain_not_frozen", not bool(summary["ReducedDomainFrozen"].iloc[0]))
    for phrase in [
        "Phi_0",
        "B_star(Phi_0)",
        "P_red = I - P_null - P_gauge - P_forbidden",
        "held-out residuals",
        "linear specificity metric pass/fail result",
        "The reference state or reduced branch domain is already frozen",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_REFERENCE_DOMAIN_FREEZE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_REFERENCE_DOMAIN_FREEZE_VALID_NOT_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
