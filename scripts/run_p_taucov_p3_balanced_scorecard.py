#!/usr/bin/env python3
"""Run the P3 balanced P-TauCov signed alignment scorecard.

This script is inert unless a final authorization manifest explicitly enables
P3BalancedScoringAuthorized=true.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "evidence/p_taucov_p3_balanced_final_authorization.yaml"
KERNEL = ROOT / "evidence/p_taucov_p3_balanced_preflight_matrix.csv"
POLICY = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy.yaml"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
OUT_OOS = ROOT / "evidence/p_taucov_p3_balanced_oos_scorecard.csv"
OUT_NULLS = ROOT / "evidence/p_taucov_p3_balanced_null_scorecard.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_scorecard_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_P3_BALANCED_ALIGNMENT_SCORECARD_v1"
KERNEL_ID = "P_TAUCOV_P3_BALANCED_SIGNED_KERNEL"
CLAIM_BOUNDARY = "p3_balanced_alignment_scorecard_no_survival_claim"


def load_authorization() -> None:
    if not AUTH.exists():
        raise RuntimeError("Missing final authorization manifest.")
    auth = yaml.safe_load(AUTH.read_text(encoding="utf-8")) or {}
    if auth.get("P3BalancedScoringAuthorized") is not True:
        raise RuntimeError("P3 balanced scoring is not authorized.")
    if auth.get("AuthorizedScope") != "p3_balanced_signed_alignment_scorecard_only":
        raise RuntimeError("Authorization scope mismatch.")


def load_policy() -> None:
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8")) or {}
    if policy.get("Status") != "P_TAUCOV_P3_BALANCED_SCORING_POLICY_FROZEN_NO_SCORING":
        raise RuntimeError("P3 balanced scoring policy is not frozen.")
    if policy.get("ScoringAuthorized") is not False:
        raise RuntimeError("Policy freeze must not itself authorize scoring.")


def read_kernel(path: Path, row_ids: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    ids = sorted(set(df["RowID"].astype(str)) | set(df["ColumnID"].astype(str)))
    if ids != row_ids:
        raise RuntimeError("Kernel row IDs do not match empirical row order.")
    idx = {rid: i for i, rid in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowID)], idx[str(row.ColumnID)]] = float(row.Value)
    return normalize_kernel(mat)


def normalize_kernel(kernel: np.ndarray) -> np.ndarray:
    kernel = 0.5 * (kernel + kernel.T)
    fro = float(np.linalg.norm(kernel, ord="fro"))
    if fro == 0.0:
        raise RuntimeError("Zero kernel.")
    return kernel / fro


def signed_statistic(resid: np.ndarray, sigma2: float, kernel: np.ndarray) -> float:
    return float((resid @ kernel @ resid) / sigma2 - np.trace(kernel))


def evaluate_fold(p5c, rows: pd.DataFrame, kernel: np.ndarray, fold: pd.Series) -> dict | None:
    test = p5c.fold_mask(rows, fold)
    train = ~test
    if int(train.sum()) <= 4 or int(test.sum()) == 0:
        return None
    coeff = p5c.fit_mean(rows, train)
    resid_train = p5c.residuals(rows, coeff, train)
    resid_test = p5c.residuals(rows, coeff, test)
    sigma2 = p5c.fit_sigma2(resid_train)
    test_idx = np.where(test)[0]
    k_test = kernel[np.ix_(test_idx, test_idx)]
    return {
        "SignedS": signed_statistic(resid_test, sigma2, k_test),
        "Sigma2": sigma2,
        "MeanCoefficients": ";".join(f"{v:.17g}" for v in coeff),
    }


def null_kernels(kernel: np.ndarray, rows: pd.DataFrame) -> dict[str, np.ndarray]:
    n = kernel.shape[0]
    rng = np.random.default_rng(20260523)
    perm = rng.permutation(n)
    clock_shift = np.roll(np.arange(n), 1)
    family_labels = rows["FamilyID"].astype(str).tolist()
    families = sorted(set(family_labels))
    family_map = {family: families[(i + 1) % len(families)] for i, family in enumerate(families)}
    family_order = []
    used: set[int] = set()
    for family in family_labels:
        target = family_map[family]
        candidates = [i for i, value in enumerate(family_labels) if value == target and i not in used]
        choice = candidates[0] if candidates else [i for i, value in enumerate(family_labels) if value == target][0]
        used.add(choice)
        family_order.append(choice)
    random_signed = rng.normal(size=(n, n))
    random_signed = normalize_kernel(0.5 * (random_signed + random_signed.T))
    return {
        "SIGN_FLIP_ORIENTATION_CONTROL": -kernel,
        "SUPPORT_SHUFFLE": normalize_kernel(kernel[np.ix_(perm, perm)]),
        "CLOCK_PHASE_SHIFT": normalize_kernel(kernel[np.ix_(clock_shift, clock_shift)]),
        "FAMILY_CYCLE": normalize_kernel(kernel[np.ix_(family_order, family_order)]),
        "SIGNED_RANDOM_ORTHOGONAL": random_signed,
    }


def main() -> int:
    load_authorization()
    load_policy()
    spec = importlib.util.spec_from_file_location("p5c_v0", P5C_V0)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load P5C module.")
    p5c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p5c)
    rows = p5c.load_rows()
    row_ids = rows["RowID"].astype(str).tolist()
    kernel = read_kernel(KERNEL, row_ids)
    folds = pd.read_csv(p5c.FOLDS)

    oos_rows = []
    for _, fold in folds.iterrows():
        result = evaluate_fold(p5c, rows, kernel, fold)
        if result is None:
            continue
        oos_rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "KernelID": KERNEL_ID,
                "FoldID": fold["FoldID"],
                "FoldClass": fold["FoldClass"],
                "PrimaryOOS": bool(fold["PrimaryOOS"]),
                "TestFamilies": fold["TestFamilies"],
                "TestClockBlocks": fold["TestClockBlocks"],
                **result,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    oos = pd.DataFrame(oos_rows)
    oos.to_csv(OUT_OOS, index=False)

    null_rows = []
    for null_id, null_kernel in null_kernels(kernel, rows).items():
        null_scores = []
        for _, fold in folds.iterrows():
            result = evaluate_fold(p5c, rows, null_kernel, fold)
            if result is not None and bool(fold["PrimaryOOS"]):
                null_scores.append(float(result["SignedS"]))
        null_rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "NullID": null_id,
                "PrimarySignedS": float(np.sum(null_scores)),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    nulls = pd.DataFrame(null_rows)
    nulls.to_csv(OUT_NULLS, index=False)

    primary = oos[oos["PrimaryOOS"]]
    family = primary[primary["FoldClass"].eq("primary_leave_one_family_out")]
    clock = primary[primary["FoldClass"].eq("primary_contiguous_clock_block")]
    primary_s = float(primary["SignedS"].sum())
    family_s = float(family["SignedS"].sum())
    clock_s = float(clock["SignedS"].sum())
    required_null_max = float(nulls["PrimarySignedS"].max())
    positive_family = family[family["SignedS"] > 0.0]
    positive_family_count = int(len(positive_family))
    max_family_share = (
        float(positive_family["SignedS"].max() / positive_family["SignedS"].sum())
        if float(positive_family["SignedS"].sum()) > 0.0
        else 1.0
    )
    status = (
        "P_TAUCOV_P3_BALANCED_ALIGNMENT_POSITIVE_NO_SURVIVAL_CLAIM"
        if primary_s > required_null_max
        and family_s > 0.0
        and clock_s > 0.0
        and positive_family_count >= 2
        and max_family_share <= 0.5
        else "P_TAUCOV_P3_BALANCED_ALIGNMENT_FAIL_NO_SURVIVAL_CLAIM"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "Status": status,
                "PrimarySignedS": primary_s,
                "FamilySignedS": family_s,
                "ClockSignedS": clock_s,
                "RequiredNullMaxSignedS": required_null_max,
                "PositiveFamilyCount": positive_family_count,
                "MaxPositiveFamilyShare": max_family_share,
                "P3BalancedScoringAuthorized": True,
                "CovarianceSurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
