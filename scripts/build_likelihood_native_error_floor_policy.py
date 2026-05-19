#!/usr/bin/env python3
"""Build an error-floor justification policy for the likelihood-native branch."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "evidence" / "source_split_likelihood_native_error_floor_sweep_summary.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
FAMILY_EXPORT = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
POLICY_OUT = ROOT / "evidence" / "source_split_likelihood_native_error_floor_policy.csv"
SUMMARY_OUT = ROOT / "evidence" / "source_split_likelihood_native_error_floor_policy_summary.csv"


def read_threshold() -> float:
    sweep = pd.read_csv(SWEEP)
    values = sweep["FirstFloorWhereK2Best"].dropna().unique()
    if len(values) == 0:
        return float("nan")
    return float(values[0])


def cross_branch_scatter_fraction() -> tuple[float, int, str]:
    if not FAMILY_EXPORT.exists() or not TARGET.exists():
        return float("nan"), 0, "missing_candidate_export_or_target"

    families = pd.read_csv(FAMILY_EXPORT)
    target = pd.read_csv(TARGET)[["GridIndex", "SourceSplitResponse"]]
    grouped = (
        families.groupby("GridIndex")["ResponseValue"]
        .agg(["count", "std"])
        .reset_index()
        .rename(columns={"std": "BranchScatter"})
    )
    data = grouped.merge(target, on="GridIndex", how="inner")
    data = data[data["count"] >= 2].copy()
    if data.empty:
        return float("nan"), 0, "not_enough_branch_rows"

    denom = np.maximum(np.abs(data["SourceSplitResponse"].to_numpy(float)), 1e-12)
    ratio = data["BranchScatter"].fillna(0.0).to_numpy(float) / denom
    return float(np.median(ratio)), int(len(ratio)), "candidate_export_preflight_only"


def main() -> None:
    threshold = read_threshold()
    scatter_fraction, scatter_rows, scatter_status = cross_branch_scatter_fraction()
    scatter_meets = bool(np.isfinite(scatter_fraction) and np.isfinite(threshold) and scatter_fraction >= threshold)

    rows = [
        {
            "RouteID": "PUBLIC_FULL_COVARIANCE",
            "RouteClass": "independent_required",
            "Definition": "Use a public full covariance matrix propagated into the source-split diagnostic vector.",
            "CurrentValue": "",
            "RequiredFloor": threshold,
            "MeetsRequiredFloor": False,
            "EligibleForBenchmark": False,
            "Status": "required_not_available",
            "BlockingIssue": "no_public_likelihood_native_source_split_covariance",
            "NextAction": "ingest or construct a public covariance for the same diagnostic vector before stronger K2 interpretation",
            "ClaimBoundary": "policy_only_no_measurement_validation",
        },
        {
            "RouteID": "PUBLIC_SYSTEMATIC_FLOOR",
            "RouteClass": "independent_required",
            "Definition": "Use an independently published systematic uncertainty floor for the transformed source-split response.",
            "CurrentValue": "",
            "RequiredFloor": threshold,
            "MeetsRequiredFloor": False,
            "EligibleForBenchmark": False,
            "Status": "required_not_available",
            "BlockingIssue": "no_independent_systematic_floor_registered",
            "NextAction": "register an external systematic-floor source before using any target-fraction floor",
            "ClaimBoundary": "policy_only_no_measurement_validation",
        },
        {
            "RouteID": "CROSS_BRANCH_SCATTER_PREFLIGHT",
            "RouteClass": "preflight_control",
            "Definition": "Estimate row-level scale from public SN/BAO branch scatter; current export is a preflight control.",
            "CurrentValue": scatter_fraction,
            "RequiredFloor": threshold,
            "MeetsRequiredFloor": scatter_meets,
            "EligibleForBenchmark": False,
            "Status": scatter_status,
            "BlockingIssue": "branch_scatter_is_candidate_preflight_not_public_full_covariance",
            "NextAction": "upgrade branch scatter into a declared covariance or systematic model before benchmark use",
            "ClaimBoundary": "policy_only_no_measurement_validation",
        },
        {
            "RouteID": "POST_HOC_ERROR_FLOOR_0P14",
            "RouteClass": "forbidden_post_hoc",
            "Definition": "Select the 0.14 target-fraction floor because it makes K2 AIC-competitive.",
            "CurrentValue": threshold,
            "RequiredFloor": threshold,
            "MeetsRequiredFloor": True,
            "EligibleForBenchmark": False,
            "Status": "forbidden_as_post_hoc_selection",
            "BlockingIssue": "selected_from_current_scorecard",
            "NextAction": "do not use as a benchmark covariance unless independently justified by another route",
            "ClaimBoundary": "policy_only_no_measurement_validation",
        },
        {
            "RouteID": "NATIVE_DIAGONAL_PROXY",
            "RouteClass": "weakening_baseline",
            "Definition": "Use the native diagonal proxy already carried by the K1 export.",
            "CurrentValue": 0.0,
            "RequiredFloor": threshold,
            "MeetsRequiredFloor": False,
            "EligibleForBenchmark": True,
            "Status": "available_but_weakening_for_k2",
            "BlockingIssue": "flexible_controls_dominate_under_native_proxy",
            "NextAction": "retain as weakening baseline while testing independent covariance routes",
            "ClaimBoundary": "policy_only_no_measurement_validation",
        },
    ]
    policy = pd.DataFrame(rows)
    policy.to_csv(POLICY_OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "RequiredFloorForK2AICCompetitiveness": threshold,
                "CrossBranchScatterMedianFraction": scatter_fraction,
                "CrossBranchScatterRows": scatter_rows,
                "CrossBranchScatterMeetsRequiredFloor": scatter_meets,
                "EligibleBenchmarkRoutesAvailable": int(policy["EligibleForBenchmark"].eq(True).sum()),
                "EligibleBenchmarkRoutesMeetingRequiredFloor": int(
                    (policy["EligibleForBenchmark"].eq(True) & policy["MeetsRequiredFloor"].eq(True)).sum()
                ),
                "IndependentRequiredRoutesAvailable": int(
                    (
                        policy["RouteClass"].eq("independent_required")
                        & policy["EligibleForBenchmark"].eq(True)
                    ).sum()
                ),
                "IndependentRequiredRoutesMeetingFloor": int(
                    (
                        policy["RouteClass"].eq("independent_required")
                        & policy["EligibleForBenchmark"].eq(True)
                        & policy["MeetsRequiredFloor"].eq(True)
                    ).sum()
                ),
                "PolicyStatus": "error_floor_not_independently_justified",
                "Interpretation": "k2_competitiveness_threshold_identified_but_not_promoted",
                "ClaimBoundary": "policy_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    print(f"Wrote {POLICY_OUT}")
    print(f"Wrote {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
