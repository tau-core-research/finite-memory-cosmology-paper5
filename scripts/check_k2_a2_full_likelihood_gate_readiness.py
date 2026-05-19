#!/usr/bin/env python3
"""Check readiness for the next A2 full likelihood-native measurement gate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PANTHEON_TABLE = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
PANTHEON_COV = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
DESI_DR2_MEAN = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR2_COV = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
A2_LOCK = ROOT / "frozen" / "k2_source_split_a2_prior_v1.yaml"
A2_PRED = ROOT / "data" / "predictions" / "k2_source_split_a2_prior_v1.csv"
K1_READINESS = ROOT / "evidence" / "source_split_likelihood_native_k1_readiness.csv"
K1_PROMOTION = ROOT / "evidence" / "source_split_likelihood_native_k1_promotion_summary.csv"
NULL_POLICY = ROOT / "evidence" / "k2_a2_full_gate_null_policy_readiness_v1.csv"
CROSS_COV_POLICY = ROOT / "evidence" / "k2_a2_cross_covariance_policy_readiness_v1.csv"
TRANSFORM_PROMOTION = ROOT / "evidence" / "k2_a2_transform_promotion_precheck_summary.csv"
TRANSFORM_PROMOTION_ROWS = ROOT / "evidence" / "k2_a2_transform_promotion_precheck.csv"

OUT = ROOT / "evidence" / "k2_a2_full_likelihood_gate_readiness.csv"


def pass_fail(ok: bool) -> str:
    return "PASS" if ok else "BLOCKED"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def k1_promoted() -> tuple[bool, str]:
    observed_parts: list[str] = []
    readiness_ok = False
    promotion_ok = False
    if K1_READINESS.exists():
        readiness = pd.read_csv(K1_READINESS)
        if not readiness.empty:
            readiness_ok = bool(readiness.get("LikelihoodNativeK1ExportAllowed", pd.Series([False])).map(truthy).all())
            decision = str(readiness.get("CurrentDecision", pd.Series([""])).iloc[0])
            observed_parts.append(f"readiness_allowed={readiness_ok}; decision={decision}")
    else:
        observed_parts.append("readiness_file_missing")
    if K1_PROMOTION.exists():
        promotion = pd.read_csv(K1_PROMOTION)
        if not promotion.empty:
            promotion_ok = bool(promotion.get("PrimaryK1PromotionAllowed", pd.Series([False])).map(truthy).all())
            checks = str(promotion.get("PromotableChecks", pd.Series([""])).iloc[0])
            observed_parts.append(f"promotion_allowed={promotion_ok}; promotable_checks={checks}")
    else:
        observed_parts.append("promotion_file_missing")
    return readiness_ok and promotion_ok, "; ".join(observed_parts)


def null_policy_frozen() -> tuple[bool, str]:
    if not NULL_POLICY.exists():
        return False, "null_policy_readiness_file_missing"
    readiness = pd.read_csv(NULL_POLICY)
    if readiness.empty:
        return False, "null_policy_readiness_empty"
    frozen = bool(readiness.get("FullGateNullPolicyFrozen", pd.Series([False])).map(truthy).all())
    registered = str(readiness.get("RegisteredRequiredNulls", pd.Series([""])).iloc[0])
    required = str(readiness.get("RequiredNulls", pd.Series([""])).iloc[0])
    guard = str(readiness.get("ScorecardGuardAllowed", pd.Series([""])).iloc[0])
    return frozen, f"registered_required_nulls={registered}/{required}; scorecard_guard_allowed={guard}"


def cross_covariance_policy_frozen() -> tuple[bool, str]:
    if not CROSS_COV_POLICY.exists():
        return False, "cross_covariance_policy_readiness_file_missing"
    readiness = pd.read_csv(CROSS_COV_POLICY)
    if readiness.empty:
        return False, "cross_covariance_policy_readiness_empty"
    frozen = bool(readiness.get("PolicyFrozenForPreflight", pd.Series([False])).map(truthy).all())
    sens = str(readiness.get("SensitivityReady", pd.Series([""])).iloc[0])
    transform = str(readiness.get("TransformCovarianceReady", pd.Series([""])).iloc[0])
    return frozen, f"policy_frozen_for_preflight={frozen}; sensitivity_ready={sens}; transform_covariance_ready={transform}"


def transform_promotion_ready(component_id: str) -> tuple[bool, str]:
    if not TRANSFORM_PROMOTION.exists() or not TRANSFORM_PROMOTION_ROWS.exists():
        return False, "transform_promotion_precheck_missing"
    summary = pd.read_csv(TRANSFORM_PROMOTION)
    rows = pd.read_csv(TRANSFORM_PROMOTION_ROWS)
    if summary.empty or rows.empty:
        return False, "transform_promotion_precheck_empty"
    ready = bool(summary.get("ScorecardRerunReady", pd.Series([False])).map(truthy).all())
    measurement = bool(summary.get("MeasurementValidationAllowed", pd.Series([True])).map(truthy).any())
    match = rows[rows["ComponentID"].astype(str).eq(component_id)]
    component_ready = bool(not match.empty and match["AllowedForScorecardRerun"].map(truthy).all())
    status = str(summary.get("CurrentStatus", pd.Series([""])).iloc[0])
    return (
        ready and component_ready and not measurement,
        f"promotion_status={status}; component={component_id}; scorecard_rerun_ready={ready}; measurement_validation_allowed={measurement}",
    )


def pantheon_cov_shape() -> tuple[int | None, int | None, bool]:
    if not PANTHEON_COV.exists():
        return None, None, False
    values = np.loadtxt(PANTHEON_COV)
    declared = int(values[0])
    flat = len(values) - 1
    return declared, flat, flat == declared * declared


def main() -> None:
    rows: list[dict[str, object]] = []

    def add(
        gate_id: str,
        requirement: str,
        ok: bool,
        observed: object,
        blocking: str,
        next_action: str,
        gate_class: str = "required",
    ) -> None:
        rows.append(
            {
                "GateID": gate_id,
                "GateClass": gate_class,
                "Status": pass_fail(ok),
                "Requirement": requirement,
                "Observed": observed,
                "BlockingIssue": "" if ok else blocking,
                "NextAction": next_action,
                "ClaimBoundary": "a2_full_likelihood_gate_no_measurement_validation",
            }
        )

    sn_rows = len(pd.read_csv(PANTHEON_TABLE, sep=r"\s+", engine="python")) if PANTHEON_TABLE.exists() else 0
    sn_declared, sn_flat, sn_cov_ok = pantheon_cov_shape()
    add(
        "A2_FULL_GATE_SN_PUBLIC_INPUT",
        "Pantheon+ table and 1701x1701 covariance available",
        PANTHEON_TABLE.exists() and sn_cov_ok and sn_rows == sn_declared,
        f"rows={sn_rows}; cov_declared={sn_declared}; flat_values={sn_flat}",
        "pantheon_public_input_missing_or_shape_invalid",
        "repair Pantheon+ local ingest before full gate",
    )

    bao_rows = pd.read_csv(DESI_DR2_MEAN, sep=r"\s+", comment="#", names=["z", "value", "quantity"], engine="python")
    bao_cov = np.loadtxt(DESI_DR2_COV)
    add(
        "A2_FULL_GATE_BAO_PUBLIC_INPUT",
        "DESI DR2 BAO mean vector and square covariance available",
        DESI_DR2_MEAN.exists() and DESI_DR2_COV.exists() and bao_cov.shape == (len(bao_rows), len(bao_rows)),
        f"rows={len(bao_rows)}; cov_shape={bao_cov.shape}; quantities={dict(bao_rows.quantity.value_counts())}",
        "desi_dr2_public_input_missing_or_shape_invalid",
        "repair DESI DR2 local ingest before full gate",
    )

    lock_text = A2_LOCK.read_text() if A2_LOCK.exists() else ""
    pred = pd.read_csv(A2_PRED) if A2_PRED.exists() else pd.DataFrame()
    add(
        "A2_FULL_GATE_LOCKED_PREDICTION",
        "A2 locked prediction exists with p=3, rho=4, A_tau=2",
        A2_LOCK.exists()
        and A2_PRED.exists()
        and "A_tau: 2.0" in lock_text
        and not pred.empty
        and set(pred["Rho"]) == {4.0}
        and set(pred["P"]) == {3}
        and set(pred["A_tau"]) == {2.0},
        f"lock={A2_LOCK.exists()}; pred_rows={len(pred)}",
        "a2_locked_prediction_missing_or_mutated",
        "regenerate locked A2 export from frozen contract only",
    )

    sn_transform_ok, sn_transform_observed = transform_promotion_ready("SN_RESIDUAL_POLICY")
    add(
        "A2_FULL_GATE_SN_TRANSFORM",
        "SN residual transform must be likelihood-native and frozen before scoring",
        sn_transform_ok,
        sn_transform_observed,
        "sn_likelihood_native_transform_not_frozen",
        "define exact SN residual vector, nuisance handling, centering rule, and transform matrix before rerun",
    )
    bao_transform_ok, bao_transform_observed = transform_promotion_ready("BAO_RESIDUAL_POLICY")
    add(
        "A2_FULL_GATE_BAO_TRANSFORM",
        "BAO residual transform must be likelihood-native and frozen before scoring",
        bao_transform_ok,
        bao_transform_observed,
        "bao_likelihood_native_transform_not_frozen",
        "define BAO observable prediction vector and transform matrix for DESI DR2 quantities before rerun",
    )
    cross_ok, cross_observed = cross_covariance_policy_frozen()
    add(
        "A2_FULL_GATE_SN_BAO_CROSS_COVARIANCE",
        "SN-BAO cross-covariance policy must be declared before scoring",
        cross_ok,
        cross_observed,
        "sn_bao_cross_covariance_policy_missing",
        "derive public cross-covariance rule or preregister zero/shrinkage policy with sensitivity report",
    )
    k1_ok, k1_observed = k1_promoted()
    add(
        "A2_FULL_GATE_LIKELIHOOD_NATIVE_K1",
        "K1/no-memory baseline must be likelihood-native and frozen independently",
        k1_ok,
        k1_observed,
        "likelihood_native_k1_not_promoted",
        "promote K1 baseline with frozen parameters, nuisance policy, and covariance route",
    )
    null_ok, null_observed = null_policy_frozen()
    add(
        "A2_FULL_GATE_NULLS_FROZEN",
        "Null comparators and validation modes must be frozen before rerun",
        null_ok,
        null_observed,
        "null_policy_not_frozen_for_full_gate",
        "freeze K1, polynomial, sign-randomized, coordinate-remap, optical/backreaction null policies",
    )

    df = pd.DataFrame(rows)
    required = df[df["GateClass"].eq("required")]
    overall_ok = bool((required["Status"] == "PASS").all())
    df = pd.concat(
        [
            df,
            pd.DataFrame(
                [
                    {
                        "GateID": "A2_FULL_LIKELIHOOD_GATE_OVERALL",
                        "GateClass": "overall",
                        "Status": "PASS" if overall_ok else "BLOCKED",
                        "Requirement": "all required full likelihood-native gates pass",
                        "Observed": f"{int((required['Status'] == 'PASS').sum())}/{len(required)} required gates pass",
                        "BlockingIssue": "" if overall_ok else "full_likelihood_native_gate_incomplete",
                        "NextAction": "complete blocked transform/covariance/K1/null gates before any measurement-validation interpretation",
                        "ClaimBoundary": "a2_full_likelihood_gate_no_measurement_validation",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
