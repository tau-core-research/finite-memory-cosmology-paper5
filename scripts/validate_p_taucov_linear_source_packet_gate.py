#!/usr/bin/env python3
"""Validate the P-TauCov finite-dimensional linear-source packet gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_source_packet_gate.md"
CSV = ROOT / "evidence/p_taucov_linear_source_packet_gate.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_source_packet_gate_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_source_packet_gate_validation.csv"

REQUIRED_SOURCES = {"K_B", "Gamma_B", "D_Phi_K_B", "D_Phi_J_B", "G_Phi", "G_B", "P0_SOURCE"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_SOURCE_PACKET_GATE_VALIDATION",
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
        print("P_TAUCOV_LINEAR_SOURCE_PACKET_GATE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_sources_present", REQUIRED_SOURCES.issubset(set(df["SourceObject"])))
    add("roles_nonempty", df["Role"].astype(str).str.strip().ne("").all())
    add("origins_nonempty", df["AllowedOrigin"].astype(str).str.strip().ne("").all())
    add("no_concrete_sources_supplied", not df["ConcreteSourceSupplied"].astype(bool).any())
    add("linear_objects_not_derivable", not df["LinearObjectsDerivable"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_gate_declared", bool(summary["LinearSourceGateDeclared"].iloc[0]))
    add("summary_no_sources", not bool(summary["ConcreteSourcesSupplied"].iloc[0]))
    add("summary_not_derivable", not bool(summary["LinearObjectsDerivable"].iloc[0]))
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "K_B",
        "Gamma_B",
        "D_Phi_K_B",
        "D_Phi_J_B",
        "G_Phi",
        "G_B",
        "P0_SOURCE",
        "OutcomeInformationUsed=false",
        "ResidualInformationUsed=false",
        "ScoreInformationUsed=false",
        "The finite-dimensional source objects or derived linear matrices are frozen",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_SOURCE_PACKET_GATE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_SOURCE_PACKET_GATE_VALID_NO_SOURCES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
