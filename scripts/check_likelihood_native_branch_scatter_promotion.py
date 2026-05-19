#!/usr/bin/env python3
"""Check whether branch-scatter covariance can be promoted beyond preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCATTER = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_covariance.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_summary.csv"
POLICY = ROOT / "evidence" / "source_split_likelihood_native_error_floor_policy_summary.csv"
GATE = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_promotion_gate.csv"
GATE_SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_promotion_summary.csv"


def bool_row(check_id: str, passed: bool, blocking_issue: str, next_action: str) -> dict[str, object]:
    return {
        "CheckID": check_id,
        "Passed": bool(passed),
        "BlockingIssue": "" if passed else blocking_issue,
        "NextAction": next_action,
        "ClaimBoundary": "promotion_gate_only_no_measurement_validation",
    }


def main() -> None:
    scatter_exists = SCATTER.exists()
    summary_exists = SUMMARY.exists()
    policy_exists = POLICY.exists()

    scatter = pd.read_csv(SCATTER) if scatter_exists else pd.DataFrame()
    summary = pd.read_csv(SUMMARY) if summary_exists else pd.DataFrame()
    policy = pd.read_csv(POLICY) if policy_exists else pd.DataFrame()

    rows = []
    rows.append(
        bool_row(
            "SCATTER_ROWS_AVAILABLE",
            scatter_exists and not scatter.empty,
            "branch_scatter_covariance_missing",
            "run scripts/run_likelihood_native_branch_scatter_benchmark.py",
        )
    )
    rows.append(
        bool_row(
            "ALL_ROWS_HAVE_TWO_BRANCHES",
            scatter_exists and not scatter.empty and scatter["BranchCount"].min() >= 2,
            "not_all_rows_have_two_public_branches",
            "complete the SN and BAO branch export for every scoring row",
        )
    )
    rows.append(
        bool_row(
            "SCATTER_EXCEEDS_K2_THRESHOLD",
            policy_exists
            and not policy.empty
            and bool(policy["CrossBranchScatterMeetsRequiredFloor"].iloc[0]),
            "branch_scatter_below_error_floor_threshold",
            "retain weakening status unless an independent scale route is available",
        )
    )
    rows.append(
        bool_row(
            "K2_BEST_UNDER_SCATTER_VARIANTS",
            summary_exists
            and not summary.empty
            and summary["BestModel"].eq("K2_LOCKED_RHO4").all()
            and summary["K2BeatsBestPoly"].astype(str).str.lower().eq("true").all(),
            "k2_not_best_under_all_branch_scatter_variants",
            "keep branch-scatter result as mixed preflight evidence",
        )
    )
    rows.append(
        bool_row(
            "NOT_PUBLIC_FULL_COVARIANCE",
            False,
            "branch_scatter_is_not_public_full_covariance",
            "do not use measurement-validation language; treat as declared preflight benchmark only",
        )
    )
    rows.append(
        bool_row(
            "INDEPENDENT_SYSTEMATIC_OR_COVARIANCE_SOURCE",
            False,
            "no_independent_systematic_or_full_covariance_source_registered",
            "register an independent covariance, systematic floor, or reconstruction-family scatter rule",
        )
    )

    gate = pd.DataFrame(rows)
    gate["CanPromoteToPreflightBenchmark"] = (
        gate["CheckID"]
        .isin(
            [
                "SCATTER_ROWS_AVAILABLE",
                "ALL_ROWS_HAVE_TWO_BRANCHES",
                "SCATTER_EXCEEDS_K2_THRESHOLD",
                "K2_BEST_UNDER_SCATTER_VARIANTS",
            ]
        )
        & gate["Passed"].astype(bool)
    )
    gate.to_csv(GATE, index=False)

    core_preflight_checks = gate[gate["CheckID"].isin(
        [
            "SCATTER_ROWS_AVAILABLE",
            "ALL_ROWS_HAVE_TWO_BRANCHES",
            "SCATTER_EXCEEDS_K2_THRESHOLD",
            "K2_BEST_UNDER_SCATTER_VARIANTS",
        ]
    )]
    measurement_checks = gate[gate["CheckID"].isin(
        [
            "NOT_PUBLIC_FULL_COVARIANCE",
            "INDEPENDENT_SYSTEMATIC_OR_COVARIANCE_SOURCE",
        ]
    )]
    preflight_promotable = bool(core_preflight_checks["Passed"].all())
    measurement_promotable = bool(gate["Passed"].all())

    summary_out = pd.DataFrame(
        [
            {
                "Checks": len(gate),
                "PassedChecks": int(gate["Passed"].sum()),
                "BlockingChecks": int((~gate["Passed"]).sum()),
                "PreflightBenchmarkPromotionAllowed": preflight_promotable,
                "MeasurementValidationPromotionAllowed": measurement_promotable,
                "MeasurementBlockingChecks": int((~measurement_checks["Passed"]).sum()),
                "PromotionStatus": (
                    "preflight_benchmark_allowed_measurement_validation_blocked"
                    if preflight_promotable and not measurement_promotable
                    else "promotion_blocked"
                ),
                "Interpretation": (
                    "branch_scatter_can_be_declared_preflight_benchmark_but_not_measurement_validation"
                    if preflight_promotable and not measurement_promotable
                    else "branch_scatter_remains_preflight_only_without_promotion"
                ),
                "ClaimBoundary": "promotion_gate_only_no_measurement_validation",
            }
        ]
    )
    summary_out.to_csv(GATE_SUMMARY, index=False)
    print(f"Wrote {GATE}")
    print(f"Wrote {GATE_SUMMARY}")


if __name__ == "__main__":
    main()
