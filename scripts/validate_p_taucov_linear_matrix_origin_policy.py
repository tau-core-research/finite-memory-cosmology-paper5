#!/usr/bin/env python3
"""Validate the P-TauCov linear matrix-origin policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_matrix_origin_policy.md"
CSV = ROOT / "evidence/p_taucov_linear_matrix_origin_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_matrix_origin_policy_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_matrix_origin_policy_validation.csv"

REQUIRED_OBJECTS = {"L0_B", "R_B", "P_red", "A_Phi", "A_B", "P0", "coordinate_basis"}
NON_GENERIC_OBJECTS = {"L0_B", "R_B", "P_red", "A_Phi", "A_B", "P0"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_MATRIX_ORIGIN_POLICY_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("policy_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_MATRIX_ORIGIN_POLICY_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_objects_present", REQUIRED_OBJECTS.issubset(set(df["ObjectID"])))
    add("all_required_before_packet", df["RequiredBeforePacket"].astype(bool).all())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    non_generic = df[df["ObjectID"].isin(NON_GENERIC_OBJECTS)]
    add("non_generic_objects_disallow_defaults", not non_generic["MayUseGenericDefault"].astype(bool).any())
    add("no_concrete_sources_present", int(summary["ConcreteSourcesPresent"].iloc[0]) == 0)
    add("packet_not_authorized", not bool(summary["LinearPacketAuthorized"].iloc[0]))
    add("scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    for phrase in [
        "Generic defaults",
        "allowed only as null comparators",
        "using held-out residuals",
        "using P5C v3 family gain localization",
        "post-hoc rank or entropy tuning",
        "The required linear packet matrices have already been derived",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_MATRIX_ORIGIN_POLICY_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_MATRIX_ORIGIN_POLICY_VALID_NO_PACKET")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
