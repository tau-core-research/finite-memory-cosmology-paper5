#!/usr/bin/env python3
"""Validate the P-TauCov Tau matrix-origin route."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_tau_matrix_origin_route.md"
CSV = ROOT / "evidence/p_taucov_tau_matrix_origin_route.csv"
SUMMARY = ROOT / "evidence/p_taucov_tau_matrix_origin_route_summary.csv"
OUT = ROOT / "evidence/p_taucov_tau_matrix_origin_route_validation.csv"

REQUIRED_OBJECTS = {"L0_B", "R_B", "P_red", "A_Phi", "A_B", "P0"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_TAU_MATRIX_ORIGIN_ROUTE_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("route_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_TAU_MATRIX_ORIGIN_ROUTE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_objects_routed", REQUIRED_OBJECTS.issubset(set(df["ObjectID"])))
    add("no_concrete_matrices_present", not df["ConcreteMatrixPresent"].astype(bool).any())
    add("no_matrix_can_enter_packet_yet", not df["CanEnterLinearPacket"].astype(bool).any())
    add("no_scoring_authorized", not df["ScoringAuthorized"].astype(bool).any())
    add("linear_packet_not_authorized", not bool(summary["LinearPacketAuthorized"].iloc[0]))
    add("metric_eval_not_authorized", not bool(summary["MetricEvaluationAuthorized"].iloc[0]))
    add("p_taucov_scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    for phrase in [
        "L0_B = P_red D_B F_B",
        "R_B = - P_red D_Phi F_B",
        "A_Phi = D_Phi M_parent",
        "A_B = D_B M_parent",
        "F_B",
        "M_parent",
        "P_morph",
        "The linear packet matrices have been derived or frozen",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_TAU_MATRIX_ORIGIN_ROUTE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_TAU_MATRIX_ORIGIN_ROUTE_VALID_NO_PACKET")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
