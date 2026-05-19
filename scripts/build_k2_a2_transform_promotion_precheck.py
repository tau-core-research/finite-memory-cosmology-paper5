#!/usr/bin/env python3
"""Build the SN/BAO transform promotion precheck for the locked A2 gate.

This precheck freezes the mathematical policy needed for a scorecard rerun.
It does not authorize measurement validation and does not alter K2, rho, p,
A_tau, or K1.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PANTHEON_TABLE = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
PANTHEON_COV = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
DESI_MEAN = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_COV = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
L_SN = DATA / "transforms" / "k2_a2_l_sn_transform_v1.csv"
L_BAO = DATA / "transforms" / "k2_a2_l_bao_transform_v1.csv"
K1 = DATA / "k1" / "source_split_external_k1_response.csv"
K2 = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"
COV_VERIFY = EVIDENCE / "k2_a2_transform_covariance_verification_v1.csv"
CROSS_COV = EVIDENCE / "k2_a2_cross_covariance_policy_readiness_v1.csv"
NULL_POLICY = EVIDENCE / "k2_a2_full_gate_null_policy_readiness_v1.csv"

OUT = EVIDENCE / "k2_a2_transform_promotion_precheck.csv"
SUMMARY = EVIDENCE / "k2_a2_transform_promotion_precheck_summary.csv"
DOC = DOCS / "k2_a2_transform_promotion_precheck.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def pantheon_size() -> tuple[int, bool]:
    if not PANTHEON_TABLE.exists() or not PANTHEON_COV.exists():
        return 0, False
    table_rows = len(pd.read_csv(PANTHEON_TABLE, sep=r"\s+", engine="python"))
    values = np.loadtxt(PANTHEON_COV)
    declared = int(values[0])
    cov_ok = len(values) - 1 == declared * declared
    return table_rows, cov_ok and table_rows == declared


def desi_size() -> tuple[int, bool]:
    if not DESI_MEAN.exists() or not DESI_COV.exists():
        return 0, False
    rows = pd.read_csv(DESI_MEAN, sep=r"\s+", comment="#", names=["z", "value", "quantity"], engine="python")
    cov = np.loadtxt(DESI_COV)
    return len(rows), cov.shape == (len(rows), len(rows))


def matrix_shape(path: Path) -> tuple[int, int, bool]:
    if not path.exists():
        return 0, 0, False
    df = pd.read_csv(path)
    value_cols = [col for col in df.columns if col != "GridIndex"]
    return len(df), len(value_cols), True


def file_bool(path: Path, column: str) -> bool:
    if not path.exists():
        return False
    df = pd.read_csv(path)
    if df.empty or column not in df.columns:
        return False
    return bool(df[column].map(truthy).all())


def main() -> None:
    sn_rows, sn_input_ok = pantheon_size()
    bao_rows, bao_input_ok = desi_size()
    lsn_rows, lsn_cols, lsn_ok = matrix_shape(L_SN)
    lbao_rows, lbao_cols, lbao_ok = matrix_shape(L_BAO)
    cov_verified = file_bool(COV_VERIFY, "MatchesReferenceWithinTolerance")
    cross_cov_frozen = file_bool(CROSS_COV, "PolicyFrozenForPreflight")
    nulls_frozen = file_bool(NULL_POLICY, "FullGateNullPolicyFrozen")

    k1_ok = False
    if K1.exists():
        k1_df = pd.read_csv(K1)
        k1_ok = (
            not k1_df.empty
            and bool(k1_df.get("AllowedAsPrimaryK1Candidate", pd.Series([False])).map(truthy).all())
            and bool(k1_df.get("LikelihoodNative", pd.Series([False])).map(truthy).all())
            and bool(k1_df.get("FittedInThisNote", pd.Series([True])).map(lambda x: not truthy(x)).all())
        )

    k2_ok = False
    if K2.exists():
        pred = pd.read_csv(K2)
        k2_ok = (
            not pred.empty
            and set(pred["P"]) == {3}
            and set(pred["Rho"]) == {4.0}
            and set(pred["A_tau"]) == {2.0}
        )

    rows = [
        {
            "ComponentID": "SN_RESIDUAL_POLICY",
            "ProductID": "PANTHEON_PLUS_SH0ES_SN",
            "Status": "PASS" if sn_input_ok and lsn_ok and lsn_rows == 8 and lsn_cols == sn_rows else "BLOCKED",
            "FrozenDefinition": "r_SN = D_SN * B_SN * (I - 1*w_SN^T) * (mu_obs - mu_CMB_baseline)",
            "Observed": f"sn_rows={sn_rows}; L_SN_shape=({lsn_rows},{lsn_cols})",
            "BlockingIssue": "" if sn_input_ok and lsn_ok and lsn_rows == 8 and lsn_cols == sn_rows else "sn_input_or_L_SN_shape_not_ready",
            "AllowedForScorecardRerun": sn_input_ok and lsn_ok and lsn_rows == 8 and lsn_cols == sn_rows,
            "AllowedForMeasurementValidation": False,
            "ClaimBoundary": "transform_promotion_precheck_no_measurement_validation",
        },
        {
            "ComponentID": "BAO_RESIDUAL_POLICY",
            "ProductID": "DESI_DR2_BAO_ALL_GAUSSIAN",
            "Status": "PASS" if bao_input_ok and lbao_ok and lbao_rows == 8 and lbao_cols == bao_rows else "BLOCKED",
            "FrozenDefinition": "r_BAO = log(q_obs / q_CMB_baseline); y_BAO = D_BAO * A_BAO * r_BAO",
            "Observed": f"bao_rows={bao_rows}; L_BAO_shape=({lbao_rows},{lbao_cols})",
            "BlockingIssue": "" if bao_input_ok and lbao_ok and lbao_rows == 8 and lbao_cols == bao_rows else "bao_input_or_L_BAO_shape_not_ready",
            "AllowedForScorecardRerun": bao_input_ok and lbao_ok and lbao_rows == 8 and lbao_cols == bao_rows,
            "AllowedForMeasurementValidation": False,
            "ClaimBoundary": "transform_promotion_precheck_no_measurement_validation",
        },
        {
            "ComponentID": "JOINT_SOURCE_SPLIT_POLICY",
            "ProductID": "PANTHEON_PLUS_SH0ES_SN;DESI_DR2_BAO_ALL_GAUSSIAN",
            "Status": "PASS" if cov_verified and cross_cov_frozen else "BLOCKED",
            "FrozenDefinition": "y_split = L_SN*r_SN - L_BAO*r_BAO; C_split from propagated SN/BAO covariance with frozen cross-covariance policy",
            "Observed": f"covariance_verified={cov_verified}; cross_covariance_policy_frozen={cross_cov_frozen}",
            "BlockingIssue": "" if cov_verified and cross_cov_frozen else "joint_covariance_or_cross_covariance_policy_not_ready",
            "AllowedForScorecardRerun": cov_verified and cross_cov_frozen,
            "AllowedForMeasurementValidation": False,
            "ClaimBoundary": "transform_promotion_precheck_no_measurement_validation",
        },
        {
            "ComponentID": "K1_AND_NULL_POLICY",
            "ProductID": "K1_BASELINE;NULL_COMPARATORS",
            "Status": "PASS" if k1_ok and nulls_frozen else "BLOCKED",
            "FrozenDefinition": "score K1/no-memory and registered null comparators in the same y_split space before A2 interpretation",
            "Observed": f"k1_likelihood_native={k1_ok}; null_policy_frozen={nulls_frozen}",
            "BlockingIssue": "" if k1_ok and nulls_frozen else "k1_or_null_policy_not_ready",
            "AllowedForScorecardRerun": k1_ok and nulls_frozen,
            "AllowedForMeasurementValidation": False,
            "ClaimBoundary": "transform_promotion_precheck_no_measurement_validation",
        },
        {
            "ComponentID": "LOCKED_A2_UNCHANGED",
            "ProductID": "K2_SOURCE_SPLIT_A2_PRIOR_V1",
            "Status": "PASS" if k2_ok else "BLOCKED",
            "FrozenDefinition": "K2_A2 = 2 * K1 * (1 + 4*x^3); p=3; rho=4; A_tau=2; no K1 refit",
            "Observed": f"k2_lock_ok={k2_ok}",
            "BlockingIssue": "" if k2_ok else "locked_A2_prediction_missing_or_mutated",
            "AllowedForScorecardRerun": k2_ok,
            "AllowedForMeasurementValidation": False,
            "ClaimBoundary": "transform_promotion_precheck_no_measurement_validation",
        },
    ]
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)

    scorecard_ready = bool(df["AllowedForScorecardRerun"].map(truthy).all())
    summary = pd.DataFrame(
        [
            {
                "ReadinessID": "K2_A2_TRANSFORM_PROMOTION_PREFLIGHT_V1",
                "Rows": len(df),
                "PassedRows": int(df["Status"].eq("PASS").sum()),
                "ScorecardRerunReady": scorecard_ready,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SCORECARD_RERUN_READY_NO_MEASUREMENT_VALIDATION" if scorecard_ready else "TRANSFORM_PROMOTION_BLOCKED",
                "BlockingComponents": ";".join(df.loc[~df["AllowedForScorecardRerun"].map(truthy), "ComponentID"]),
                "NextAction": "rerun locked A2 scorecard under frozen transform policy; keep measurement-validation language closed",
                "ClaimBoundary": "transform_promotion_precheck_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    DOC.write_text(
        "\n".join(
            [
                "# K2 A2 Transform Promotion Precheck",
                "",
                "Status: scorecard-rerun precheck; no measurement-validation claim.",
                "",
                "This file freezes the SN/BAO transform policy needed to rerun the locked A2 scorecard.",
                "It does not change the K2 kernel, does not allow rho>4, and does not refit K1.",
                "",
                "## Frozen Vector Policy",
                "",
                "```text",
                "r_SN  = D_SN * B_SN * (I - 1*w_SN^T) * (mu_obs - mu_CMB_baseline)",
                "r_BAO = log(q_obs / q_CMB_baseline)",
                "y_split = L_SN*r_SN - L_BAO*r_BAO",
                "```",
                "",
                "## Boundary",
                "",
                "The transform can support a scorecard rerun if all rows pass. It still cannot be used as a measurement-validation claim until the rerun and public benchmark interpretation are completed.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
