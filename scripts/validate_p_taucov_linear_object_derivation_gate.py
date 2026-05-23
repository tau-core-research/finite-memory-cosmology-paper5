#!/usr/bin/env python3
"""Validate the P-TauCov linear-object derivation gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_object_derivation_gate.md"
CSV = ROOT / "evidence/p_taucov_linear_object_derivation_gate.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_object_derivation_gate_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_object_derivation_gate_validation.csv"

REQUIRED_OBJECTS = {"L0_B", "R_B", "A_Phi", "A_B", "P0"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_OBJECT_DERIVATION_GATE_VALIDATION",
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
        print("P_TAUCOV_LINEAR_OBJECT_DERIVATION_GATE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_objects_present", REQUIRED_OBJECTS.issubset(set(df["Object"])))
    add("origins_nonempty", df["RequiredOrigin"].astype(str).str.strip().ne("").all())
    add("expected_files_nonempty", df["ExpectedFile"].astype(str).str.strip().ne("").all())
    add("no_concrete_objects_supplied", not df["ConcreteObjectSupplied"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_gate_declared", bool(summary["LinearObjectGateDeclared"].iloc[0]))
    add("summary_no_objects", not bool(summary["ConcreteObjectsSupplied"].iloc[0]))
    add("summary_linear_packet_not_authorized", not bool(summary["LinearPacketAuthorized"].iloc[0]))
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "P_red D_B F_B",
        "D_Phi M_parent",
        "P_morph",
        "OutcomeInformationUsed=false",
        "ResidualInformationUsed=false",
        "ScoreInformationUsed=false",
        "The Tau-side linear matrices or covariance response are frozen",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_OBJECT_DERIVATION_GATE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_OBJECT_DERIVATION_GATE_VALID_NO_MATRICES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
