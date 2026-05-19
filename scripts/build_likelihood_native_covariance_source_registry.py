#!/usr/bin/env python3
"""Register independent covariance/systematic routes for likelihood-native K2."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "evidence" / "source_split_likelihood_native_covariance_source_registry.csv"
READINESS = ROOT / "evidence" / "source_split_likelihood_native_covariance_source_readiness.csv"
TASKS = ROOT / "evidence" / "source_split_likelihood_native_covariance_source_task_queue.csv"

DESI_COV = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
PANTHEON_COV = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BRANCH_SCATTER = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_covariance.csv"
BRANCH_PROMO = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_promotion_summary.csv"
PUBLIC_PROXY = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy_summary.csv"


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def main() -> None:
    desi_available = exists(DESI_COV)
    pantheon_available = exists(PANTHEON_COV)
    branch_available = exists(BRANCH_SCATTER)
    public_proxy_available = exists(PUBLIC_PROXY)
    branch_promo = pd.read_csv(BRANCH_PROMO) if exists(BRANCH_PROMO) else pd.DataFrame()
    branch_preflight_allowed = bool(
        not branch_promo.empty
        and branch_promo["PreflightBenchmarkPromotionAllowed"].astype(str).str.lower().eq("true").all()
    )

    rows = [
        {
            "SourceID": "PUBLIC_SN_BAO_FULL_PROPAGATED_COVARIANCE",
            "RouteClass": "independent_required",
            "Description": "Propagate Pantheon+ and DESI covariance into the same likelihood-native source-split vector.",
            "RawInputsAvailable": desi_available and pantheon_available,
            "TransformedCovarianceAvailable": False,
            "EligibleForPreflightBenchmark": False,
            "EligibleForMeasurementValidation": False,
            "CurrentStatus": "raw_public_covariances_available_transform_missing",
            "BlockingIssue": "joint_source_split_covariance_not_propagated",
            "NextAction": "define Jacobian/bootstrap propagation from SN and BAO observables into the source-split vector",
            "ClaimBoundary": "covariance_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "PUBLIC_SN_BAO_PROPAGATED_PROXY",
            "RouteClass": "public_proxy_preflight",
            "Description": "First propagated public SN+BAO covariance proxy on the likelihood-native source-split vector.",
            "RawInputsAvailable": desi_available and pantheon_available,
            "TransformedCovarianceAvailable": public_proxy_available,
            "EligibleForPreflightBenchmark": public_proxy_available,
            "EligibleForMeasurementValidation": False,
            "CurrentStatus": (
                "public_covariance_proxy_available"
                if public_proxy_available
                else "public_covariance_proxy_missing"
            ),
            "BlockingIssue": "proxy_not_full_likelihood;sn_bao_cross_covariance_zero_assumption",
            "NextAction": "compare against branch-scatter preflight and upgrade to full propagated likelihood covariance",
            "ClaimBoundary": "covariance_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "PUBLIC_SYSTEMATIC_FLOOR",
            "RouteClass": "independent_required",
            "Description": "Externally declared systematic floor for the transformed source-split diagnostic.",
            "RawInputsAvailable": False,
            "TransformedCovarianceAvailable": False,
            "EligibleForPreflightBenchmark": False,
            "EligibleForMeasurementValidation": False,
            "CurrentStatus": "not_registered",
            "BlockingIssue": "no_external_systematic_floor_source",
            "NextAction": "identify and cite a systematic-floor source before benchmark use",
            "ClaimBoundary": "covariance_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "BRANCH_SCATTER_DECLARED_PREFLIGHT",
            "RouteClass": "preflight_benchmark",
            "Description": "SN/BAO branch scatter on the source-split vector, promoted only to declared preflight benchmark.",
            "RawInputsAvailable": branch_available,
            "TransformedCovarianceAvailable": branch_available,
            "EligibleForPreflightBenchmark": branch_preflight_allowed,
            "EligibleForMeasurementValidation": False,
            "CurrentStatus": (
                "preflight_benchmark_allowed"
                if branch_preflight_allowed
                else "preflight_benchmark_not_allowed"
            ),
            "BlockingIssue": "not_public_full_covariance",
            "NextAction": "use as declared preflight benchmark; replace or validate with independent covariance route",
            "ClaimBoundary": "covariance_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "RECONSTRUCTION_FAMILY_SCATTER",
            "RouteClass": "candidate_future",
            "Description": "Scatter across a registered public reconstruction-family response export.",
            "RawInputsAvailable": False,
            "TransformedCovarianceAvailable": False,
            "EligibleForPreflightBenchmark": False,
            "EligibleForMeasurementValidation": False,
            "CurrentStatus": "not_registered",
            "BlockingIssue": "no_public_reconstruction_family_scatter_rule",
            "NextAction": "register reconstruction families and freeze scatter rule before scoring",
            "ClaimBoundary": "covariance_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "NATIVE_DIAGONAL_PROXY",
            "RouteClass": "weakening_baseline",
            "Description": "Native K1Sigma diagonal proxy carried by the likelihood-native K1 export.",
            "RawInputsAvailable": True,
            "TransformedCovarianceAvailable": True,
            "EligibleForPreflightBenchmark": True,
            "EligibleForMeasurementValidation": False,
            "CurrentStatus": "available_weakening_baseline",
            "BlockingIssue": "too_narrow_for_branch_scale_and_not_public_full_covariance",
            "NextAction": "retain as baseline control when comparing covariance routes",
            "ClaimBoundary": "covariance_source_registry_no_measurement_validation",
        },
    ]
    registry = pd.DataFrame(rows)
    registry.to_csv(REGISTRY, index=False)

    readiness = pd.DataFrame(
        [
            {
                "ArtifactID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_COVARIANCE_SOURCE_READINESS",
                "RawPublicCovariancesAvailable": desi_available and pantheon_available,
                "PublicCovarianceProxyAvailable": public_proxy_available,
                "PreflightBenchmarkRouteAvailable": bool(registry["EligibleForPreflightBenchmark"].any()),
                "MeasurementValidationRouteAvailable": bool(registry["EligibleForMeasurementValidation"].any()),
                "BranchScatterPreflightAllowed": branch_preflight_allowed,
                "PrimaryBlockingIssue": (
                    "full_likelihood_covariance_missing"
                    if public_proxy_available
                    else "public_covariance_transform_missing"
                ),
                "NextAction": (
                    "upgrade public covariance proxy to full likelihood covariance and compare with branch-scatter benchmark"
                    if public_proxy_available
                    else "build propagated public SN+BAO source-split covariance or register an independent systematic/scatter source"
                ),
                "ClaimBoundary": "covariance_source_registry_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(READINESS, index=False)

    tasks = pd.DataFrame(
        [
            {
                "TaskID": "COVSRC_1_PROPAGATE_PUBLIC_COVARIANCE",
                "Priority": 1,
                "DependsOn": "",
                "Task": "Propagate Pantheon+ and DESI covariance into the likelihood-native source-split vector.",
                "BlocksMeasurementValidation": True,
                "Status": "PROXY_AVAILABLE_FULL_LIKELIHOOD_PENDING" if public_proxy_available else "PENDING",
            },
            {
                "TaskID": "COVSRC_2_REGISTER_SYSTEMATIC_FLOOR",
                "Priority": 2,
                "DependsOn": "",
                "Task": "Find or declare an independent systematic-floor source for the transformed diagnostic.",
                "BlocksMeasurementValidation": True,
                "Status": "PENDING",
            },
            {
                "TaskID": "COVSRC_3_FREEZE_RECONSTRUCTION_FAMILY_SCATTER",
                "Priority": 3,
                "DependsOn": "",
                "Task": "Register reconstruction-family scatter rule before any scoring use.",
                "BlocksMeasurementValidation": False,
                "Status": "PENDING",
            },
            {
                "TaskID": "COVSRC_4_KEEP_BRANCH_SCATTER_PREFLIGHT",
                "Priority": 4,
                "DependsOn": "",
                "Task": "Use branch scatter only as declared preflight benchmark until an independent route exists.",
                "BlocksMeasurementValidation": False,
                "Status": "ACTIVE_BOUNDARY",
            },
        ]
    )
    tasks.to_csv(TASKS, index=False)

    print(f"Wrote {REGISTRY}")
    print(f"Wrote {READINESS}")
    print(f"Wrote {TASKS}")


if __name__ == "__main__":
    main()
