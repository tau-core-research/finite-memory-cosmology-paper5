#!/usr/bin/env python3
"""Validate the P-TauCov Tau-side definition spec."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_tau_side_definition_spec.md"
CSV = ROOT / "evidence/p_taucov_tau_side_definition_spec.csv"
SUMMARY = ROOT / "evidence/p_taucov_tau_side_definition_spec_summary.csv"
OUT = ROOT / "evidence/p_taucov_tau_side_definition_spec_validation.csv"

REQUIRED_OBJECTS = {"F_B", "U_branch", "M_parent", "P_morph", "Phi_0", "NullGaugeBasis"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_TAU_SIDE_DEFINITION_SPEC_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("spec_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_TAU_SIDE_DEFINITION_SPEC_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_objects_present", REQUIRED_OBJECTS.issubset(set(df["ObjectID"])))
    add("no_concrete_matrices_produced", not df["ConcreteMatrixProduced"].astype(bool).any())
    add("no_packet_entry_authorized", not df["CanEnterLinearPacket"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["ScoringAuthorized"].astype(bool).any())
    add("reference_state_not_set", not bool(summary["ReferenceStateSet"].iloc[0]))
    add("null_gauge_basis_not_set", not bool(summary["NullGaugeBasisSet"].iloc[0]))
    add("linear_packet_not_authorized", not bool(summary["LinearPacketAuthorized"].iloc[0]))
    for phrase in [
        "F_B(\\Phi,B)",
        "U_{\\rm branch}",
        "D_B F_B = K_B",
        "M_{\\rm parent}(\\Phi,B)",
        "P_{\\rm morph}(\\Phi,B)=P_0",
        "epsilon_P=0",
        "The Tau-side definitions have produced a valid linear packet",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_TAU_SIDE_DEFINITION_SPEC_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_TAU_SIDE_DEFINITION_SPEC_VALID_NOT_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
