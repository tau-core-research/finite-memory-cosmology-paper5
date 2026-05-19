#!/usr/bin/env python3
"""Build the public covariance upgrade queue after the support ladder."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SUPPORT = ROOT / "evidence" / "source_split_likelihood_native_support_ladder_summary.csv"
ROUTE = ROOT / "evidence" / "source_split_likelihood_native_covariance_route_summary.csv"
PUBLIC_PROXY = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy_summary.csv"
CV = ROOT / "evidence" / "source_split_likelihood_native_polynomial_cv_summary.csv"
READINESS = ROOT / "evidence" / "source_split_likelihood_native_covariance_source_readiness.csv"

OUT_QUEUE = ROOT / "evidence" / "public_covariance_upgrade_queue.csv"
OUT_READINESS = ROOT / "evidence" / "public_covariance_upgrade_readiness.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    support = pd.read_csv(SUPPORT).iloc[0]
    route = pd.read_csv(ROUTE).iloc[0]
    public = pd.read_csv(PUBLIC_PROXY).iloc[0]
    readiness = pd.read_csv(READINESS).iloc[0]
    cv = pd.read_csv(CV)
    comparisons = cv[cv["ModelID"].eq("CV_COMPARISON")]
    public_cv = comparisons[comparisons["SigmaRoute"].eq("public_proxy_diag")]
    public_cv_beats_poly = int(public_cv["K2BeatsBestPoly"].map(bool_text).sum())

    queue_rows = [
        {
            "TaskID": "PCOV_UPGRADE_1_FULL_TRANSFORM",
            "Priority": 1,
            "RequirementLevel": "measurement_validation_required",
            "CurrentEvidence": "public covariance proxy exists but is simplified and not full likelihood-native",
            "BlockingIssue": "full_likelihood_covariance_missing",
            "AcceptanceCriterion": "public SN+BAO covariance is propagated through the registered likelihood-native source-split transform with documented cross-covariance policy",
            "CurrentStatus": "BLOCKING",
            "NextAction": "replace simplified public proxy with full transform or explicitly registered shrinkage covariance",
            "ClaimBoundary": "public_covariance_upgrade_no_measurement_validation",
        },
        {
            "TaskID": "PCOV_UPGRADE_2_CROSS_COVARIANCE_POLICY",
            "Priority": 2,
            "RequirementLevel": "public_benchmark_required",
            "CurrentEvidence": "row-aligned cross-covariance sensitivity does not make public proxy beat polynomial controls",
            "BlockingIssue": "sn_bao_cross_covariance_not_likelihood_native",
            "AcceptanceCriterion": "SN-BAO cross-covariance is derived from public likelihood structure or predeclared shrinkage policy, not tuned to favor K2",
            "CurrentStatus": "BLOCKING",
            "NextAction": "register cross-covariance construction before rerunning scorecards",
            "ClaimBoundary": "public_covariance_upgrade_no_measurement_validation",
        },
        {
            "TaskID": "PCOV_UPGRADE_3_POLYNOMIAL_CONTROL_RULE",
            "Priority": 3,
            "RequirementLevel": "public_benchmark_required",
            "CurrentEvidence": (
                f"public in-sample polynomial controls dominate; public CV K2 beats polynomial "
                f"{public_cv_beats_poly}/{len(public_cv)} validation modes"
            ),
            "BlockingIssue": "polynomial_control_dominance_not_fully_resolved",
            "AcceptanceCriterion": "polynomial comparators are scored under the same covariance, cross-validation policy, and complexity penalty as K2",
            "CurrentStatus": "PARTIAL",
            "NextAction": "freeze public-benchmark polynomial-control policy and report both in-sample and CV results",
            "ClaimBoundary": "public_covariance_upgrade_no_measurement_validation",
        },
        {
            "TaskID": "PCOV_UPGRADE_4_BRANCH_SCATTER_REGISTRATION",
            "Priority": 4,
            "RequirementLevel": "preflight_to_supportive_bridge",
            "CurrentEvidence": (
                f"branch scatter competitive routes={int(route['BranchScatterCompetitiveRoutes'])}; "
                f"current strongest status={support['CurrentStrongestStatus']}"
            ),
            "BlockingIssue": "branch_scatter_not_independent_public_covariance",
            "AcceptanceCriterion": "branch-scatter route is justified as an independent systematic/scatter benchmark before stronger interpretation",
            "CurrentStatus": "PREFLIGHT_ALLOWED",
            "NextAction": "document whether branch scatter is a systematic floor, reconstruction-family scatter, or only a sensitivity route",
            "ClaimBoundary": "public_covariance_upgrade_no_measurement_validation",
        },
        {
            "TaskID": "PCOV_UPGRADE_5_LOCKED_RERUN_PROTOCOL",
            "Priority": 5,
            "RequirementLevel": "all_future_reruns_required",
            "CurrentEvidence": "K2 kernel is locked and current result is route-dependent",
            "BlockingIssue": "future_rerun_must_avoid_post_hoc_route_selection",
            "AcceptanceCriterion": "next scorecard declares covariance route, K1 source, nulls, x mapping, and acceptance thresholds before execution",
            "CurrentStatus": "REQUIRED_BEFORE_NEXT_STRONGER_SCORECARD",
            "NextAction": "create frozen rerun protocol before any public covariance rerun is interpreted",
            "ClaimBoundary": "public_covariance_upgrade_no_measurement_validation",
        },
    ]
    queue = pd.DataFrame(queue_rows)
    queue.to_csv(OUT_QUEUE, index=False)

    readiness_rows = [
        {
            "ReadinessID": "PUBLIC_COVARIANCE_UPGRADE_READINESS",
            "K2VsK1Supportive": support["K2VsK1Status"] == "SUPPORTIVE_PREFLIGHT",
            "K2VsPolynomialResolved": support["K2VsPolynomialStatus"] == "SUPPORTIVE_PREFLIGHT",
            "PublicCovarianceStrongEnough": bool_text(public["K2BeatsBestPoly"]),
            "PublicCovarianceProxyAvailable": bool_text(readiness["PublicCovarianceProxyAvailable"]),
            "MeasurementValidationRouteAvailable": bool_text(readiness["MeasurementValidationRouteAvailable"]),
            "BranchScatterPreflightAllowed": bool_text(readiness["BranchScatterPreflightAllowed"]),
            "BlockingTaskCount": int(queue["CurrentStatus"].isin(["BLOCKING", "REQUIRED_BEFORE_NEXT_STRONGER_SCORECARD"]).sum()),
            "PartialTaskCount": int(queue["CurrentStatus"].eq("PARTIAL").sum()),
            "PreflightAllowedTaskCount": int(queue["CurrentStatus"].eq("PREFLIGHT_ALLOWED").sum()),
            "CurrentStatus": "PUBLIC_ROUTE_NOT_READY_FOR_MEASUREMENT_VALIDATION",
            "PrimaryNextAction": "freeze full public covariance or registered shrinkage route before stronger K2 interpretation",
            "Interpretation": "support_ladder_is_positive_but_public_covariance_upgrade_remains_the_decisive_blocker",
            "ClaimBoundary": "public_covariance_upgrade_no_measurement_validation",
        }
    ]
    pd.DataFrame(readiness_rows).to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_QUEUE}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
