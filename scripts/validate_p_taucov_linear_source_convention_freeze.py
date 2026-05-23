#!/usr/bin/env python3
"""Validate the P-TauCov minimal linear-source convention freeze."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_source_convention_freeze.md"
CSV = ROOT / "evidence/p_taucov_linear_source_convention_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_source_convention_freeze_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_source_convention_freeze_validation.csv"

REQUIRED_SOURCES = {"K_B", "Gamma_B", "D_Phi_K_B", "D_Phi_J_B", "G_Phi", "G_B", "P0_SOURCE"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_SOURCE_CONVENTION_FREEZE_VALIDATION",
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
        print("P_TAUCOV_LINEAR_SOURCE_CONVENTION_FREEZE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_sources_present", REQUIRED_SOURCES.issubset(set(df["SourceObject"])))
    add("conventions_nonempty", df["Convention"].astype(str).str.strip().ne("").all())
    add("rationales_nonempty", df["Rationale"].astype(str).str.strip().ne("").all())
    add("no_concrete_sources", not df["ConcreteSourceSupplied"].astype(bool).any())
    add("linear_objects_not_derivable", not df["LinearObjectsDerivable"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_no_sources", not bool(summary["ConcreteSourcesSupplied"].iloc[0]))
    add("summary_not_derivable", not bool(summary["LinearObjectsDerivable"].iloc[0]))
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "identity on retained reduced-domain coordinates",
        "zero regularizer",
        "zero derivative",
        "identity parent-to-branch",
        "target-blind baseline source packet",
        "Minimal target-blind linear-source conventions are frozen",
        "Concrete source matrices, derived linear objects",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_SOURCE_CONVENTION_FREEZE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_SOURCE_CONVENTION_FREEZE_VALID_NO_SOURCES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
