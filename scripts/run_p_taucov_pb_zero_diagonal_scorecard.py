#!/usr/bin/env python3
"""Run the PB zero-diagonal P-TauCov primary covariance scorecard."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "evidence/p_taucov_pb_zero_diagonal_final_manifest.yaml"
OBJECT = ROOT / "evidence/p_taucov_pb_zero_diagonal_object_matrix.csv"
COORD = ROOT / "evidence/p_taucov_pb_interaction_coordinate.csv"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"

OUT_IN_SAMPLE = ROOT / "evidence/p_taucov_pb_zero_diagonal_scorecard.csv"
OUT_OOS = ROOT / "evidence/p_taucov_pb_zero_diagonal_oos_scorecard.csv"
OUT_NULLS = ROOT / "evidence/p_taucov_pb_zero_diagonal_null_scorecard.csv"
OUT_GATES = ROOT / "evidence/p_taucov_pb_zero_diagonal_survival_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_pb_zero_diagonal_scorecard_summary.csv"
OUT_DOC = ROOT / "docs/p_taucov_pb_zero_diagonal_scorecard.md"

AUTHORIZED_STATUS = "P_TAUCOV_PB_ZERO_DIAGONAL_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM"
PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_PRIMARY_SCORECARD_v1"
KERNEL_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_COVARIANCE_KERNEL"
CLAIM_BOUNDARY = "pb_zero_diagonal_primary_scorecard_no_survival_claim"

GENERIC_NULL_MAP = {
    "GENERIC_RANDOM_SMOOTH_PSD": "K_RANDOM_SMOOTH_PSD",
    "PROJECTION_NULL": "K_PHASE_SHIFTED",
    "GENERIC_WRONG_CLOCK": "K_WRONG_CLOCK",
    "GENERIC_PHASE_SHIFT": "K_PHASE_SHIFTED",
    "GENERIC_FAMILY_PERMUTED": "K_FAMILY_PERMUTED",
    "GENERIC_DIAGONAL": "K_IDENTITY_DIAGONAL",
}


def load_authorization(path: Path) -> None:
    if not path.exists():
        raise RuntimeError("Missing final authorization manifest; scoring is not authorized.")
    manifest = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if manifest.get("Status") != AUTHORIZED_STATUS:
        raise RuntimeError("Final manifest does not authorize PB zero-diagonal scorecard.")
    if manifest.get("PTauCovScoringAuthorized") is not True:
        raise RuntimeError("Final manifest does not authorize P-TauCov scoring.")
    if manifest.get("AuthorizedScope") != "pb_zero_diagonal_primary_covariance_scorecard_only":
        raise RuntimeError("Final manifest does not authorize this scorecard scope.")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_kernel(kernel: np.ndarray) -> tuple[np.ndarray, float]:
    kernel = 0.5 * (kernel + kernel.T)
    fro = float(np.linalg.norm(kernel, ord="fro"))
    if fro == 0.0:
        return kernel, fro
    return kernel / fro, fro


def matrix_from_row_long(path: Path, object_id: str | None = None) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    if object_id is not None and "ObjectCandidateID" in df.columns:
        df = df[df["ObjectCandidateID"].astype(str).eq(object_id)]
    labels = list(dict.fromkeys(df["RowID"].astype(str)))
    idx = {label: i for i, label in enumerate(labels)}
    mat = np.zeros((len(labels), len(labels)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowID)], idx[str(row.ColumnID)]] = float(row.Value)
    return labels, 0.5 * (mat + mat.T)


def import_p5c_module():
    p5c = load_module(P5C_V0, "p5c_v0_pb_zero_diag")
    p5c.AUDIT_ID = AUDIT_ID
    p5c.PROTOCOL_ID = PROTOCOL_ID
    p5c.KERNEL_ID = KERNEL_ID
    p5c.CLAIM_BOUNDARY = CLAIM_BOUNDARY
    p5c.fit_alpha = signed_fit_alpha
    p5c.evaluate = signed_evaluate
    return p5c


def signed_fit_alpha(resid_train: np.ndarray, sigma2: float, kernel_train: np.ndarray) -> tuple[float, float]:
    # Frozen signed one-scalar alpha grid. Invalid non-SPD covariance points are
    # skipped rather than treated as evidence. This is required because the PB
    # zero-diagonal object is an off-diagonal covariance-response deformation,
    # not a PSD kernel.
    grid = np.concatenate([-np.geomspace(1e-6, 10.0, 160)[::-1], [0.0], np.geomspace(1e-6, 10.0, 160)])
    best_alpha = 0.0
    best_nll = nll_gaussian_safe(resid_train, sigma2 * np.eye(len(resid_train)))
    for alpha in grid:
        cov = sigma2 * np.eye(len(resid_train)) + float(alpha) * kernel_train
        score = nll_gaussian_safe(resid_train, cov)
        if np.isfinite(score) and score < best_nll:
            best_nll = score
            best_alpha = float(alpha)
    return best_alpha, best_nll


def signed_fit_alpha_validated(
    resid_train: np.ndarray,
    sigma2: float,
    kernel_train: np.ndarray,
    kernel_test: np.ndarray,
    test_size: int,
) -> tuple[float, float]:
    # Same frozen grid as signed_fit_alpha, but restricted to alpha values that
    # keep both train and declared test covariance SPD. This uses only the
    # kernel/domain structure and fold membership, not test residual outcomes.
    grid = np.concatenate([-np.geomspace(1e-6, 10.0, 160)[::-1], [0.0], np.geomspace(1e-6, 10.0, 160)])
    best_alpha = 0.0
    best_nll = nll_gaussian_safe(resid_train, sigma2 * np.eye(len(resid_train)))
    for alpha in grid:
        train_cov = sigma2 * np.eye(len(resid_train)) + float(alpha) * kernel_train
        test_cov = sigma2 * np.eye(test_size) + float(alpha) * kernel_test
        if not np.isfinite(nll_gaussian_safe(np.zeros(test_size), test_cov)):
            continue
        score = nll_gaussian_safe(resid_train, train_cov)
        if np.isfinite(score) and score < best_nll:
            best_nll = score
            best_alpha = float(alpha)
    return best_alpha, best_nll


def nll_gaussian_safe(resid: np.ndarray, cov: np.ndarray) -> float:
    cov = 0.5 * (cov + cov.T)
    jitter = 1e-9
    for _ in range(7):
        try:
            chol = np.linalg.cholesky(cov + jitter * np.eye(len(cov)))
            sol = np.linalg.solve(chol, resid)
            quad = float(sol @ sol)
            logdet = float(2.0 * np.sum(np.log(np.diag(chol))))
            return 0.5 * (quad + logdet + len(resid) * np.log(2.0 * np.pi))
        except np.linalg.LinAlgError:
            jitter *= 10.0
    return float("inf")


def signed_evaluate(rows: pd.DataFrame, kernel: np.ndarray, train_mask: np.ndarray, test_mask: np.ndarray) -> dict:
    p5c = load_module(P5C_V0, "p5c_v0_pb_zero_diag_eval")
    coeff = p5c.fit_mean(rows, train_mask)
    resid_train = p5c.residuals(rows, coeff, train_mask)
    resid_test = p5c.residuals(rows, coeff, test_mask)
    train_idx = np.where(train_mask)[0]
    test_idx = np.where(test_mask)[0]
    k_train = kernel[np.ix_(train_idx, train_idx)]
    k_test = kernel[np.ix_(test_idx, test_idx)]
    sigma2 = p5c.fit_sigma2(resid_train)
    alpha, train_nll_kernel = signed_fit_alpha_validated(resid_train, sigma2, k_train, k_test, len(resid_test))
    baseline_test = nll_gaussian_safe(resid_test, sigma2 * np.eye(len(resid_test)))
    kernel_test = nll_gaussian_safe(resid_test, sigma2 * np.eye(len(resid_test)) + alpha * k_test)
    return {
        "Alpha": alpha,
        "Sigma2": sigma2,
        "TrainNLL_Kernel": train_nll_kernel,
        "TestNLL_Baseline": baseline_test,
        "TestNLL_Kernel": kernel_test,
        "DeltaNLL_BaselineMinusKernel": baseline_test - kernel_test,
        "MeanCoefficients": ";".join(f"{v:.17g}" for v in coeff),
    }


def context_holdout_rows(p5c, rows: pd.DataFrame, kernel: np.ndarray) -> pd.DataFrame:
    median_z = float(rows["z"].median())
    blocks = [
        ("context_low_z", rows["z"].to_numpy(float) <= median_z),
        ("context_high_z", rows["z"].to_numpy(float) > median_z),
    ]
    out = []
    for fold_id, test in blocks:
        train = ~test
        result = p5c.evaluate(rows, kernel, train, test)
        out.append(
            {
                "AuditID": AUDIT_ID,
                "ProtocolID": PROTOCOL_ID,
                "KernelID": KERNEL_ID,
                "FoldID": fold_id,
                "FoldClass": "primary_observing_context_block",
                "PrimaryOOS": True,
                "TrainRows": int(train.sum()),
                "TestRows": int(test.sum()),
                "TestFamilies": "ALL",
                "TestClockBlocks": fold_id,
                **result,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    return pd.DataFrame(out)


def score_kernel(p5c, rows: pd.DataFrame, kernel: np.ndarray, kernel_id: str) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    ins, oos = p5c.score_all(rows, kernel, kernel_id)
    primary_delta = float(oos[oos["PrimaryOOS"]]["DeltaNLL_BaselineMinusKernel"].sum())
    return ins, oos, primary_delta


def pb_diagnostic_nulls(rows: pd.DataFrame) -> dict[str, tuple[np.ndarray, float]]:
    labels, full_outer = matrix_from_row_long(ROOT / "evidence/p_taucov_pb_interaction_object_preflight_matrix.csv", "PB_OUTER_PRODUCT_PSD")
    if labels != rows["RowID"].astype(str).tolist():
        raise RuntimeError("PB diagnostic row order does not match P5C row order.")
    coord = pd.read_csv(COORD)
    if coord["EmpiricalRowID"].astype(str).tolist() != labels:
        raise RuntimeError("PB coordinate row order does not match object row order.")
    vector = coord["FrozenCoordinateValue"].astype(float).to_numpy()
    diag_only = np.diag(np.diag(full_outer))
    family_ids = coord["FamilyID"].astype(str).to_numpy()
    family_mask = np.array(
        [[family_ids[i] == family_ids[j] for j in range(len(family_ids))] for i in range(len(family_ids))],
        dtype=float,
    )
    family_masked = np.outer(vector, vector) * family_mask
    return {
        "PB_DIAGONAL_ONLY": normalize_kernel(diag_only),
        "PB_FAMILY_MASKED": normalize_kernel(family_masked),
    }


def survival_gates(real_oos: pd.DataFrame, null_summary: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    primary = real_oos[real_oos["PrimaryOOS"]]
    lofo = primary[primary["FoldClass"].eq("primary_leave_one_family_out")]
    clock = primary[primary["FoldClass"].eq("primary_contiguous_clock_block")]
    context = primary[primary["FoldClass"].eq("primary_observing_context_block")]
    primary_delta = float(primary["DeltaNLL_BaselineMinusKernel"].sum())
    family_delta = float(lofo["DeltaNLL_BaselineMinusKernel"].sum())
    clock_delta = float(clock["DeltaNLL_BaselineMinusKernel"].sum())
    context_delta = float(context["DeltaNLL_BaselineMinusKernel"].sum()) if len(context) else 0.0
    null_max = float(null_summary["PrimaryOOSDeltaNLL_BaselineMinusKernel"].max())
    alpha_stable = bool((primary["Alpha"] > 0.0).all())
    positive = primary[primary["DeltaNLL_BaselineMinusKernel"] > 0.0]
    max_share = 1.0
    if float(positive["DeltaNLL_BaselineMinusKernel"].sum()) > 0.0:
        max_share = float(positive["DeltaNLL_BaselineMinusKernel"].max() / positive["DeltaNLL_BaselineMinusKernel"].sum())
    gates = [
        ("SURV-G1_PRIMARY_OOS_POSITIVE", primary_delta > 0.0, primary_delta),
        ("SURV-G2_FAMILY_AGGREGATE_POSITIVE", family_delta > 0.0, family_delta),
        ("SURV-G3_CLOCK_AGGREGATE_POSITIVE", clock_delta > 0.0, clock_delta),
        ("SURV-G4_CONTEXT_AGGREGATE_POSITIVE", context_delta > 0.0, context_delta),
        ("SURV-G5_BEATS_ALL_REQUIRED_NULLS", primary_delta > null_max, primary_delta - null_max),
        ("SURV-G6_NOT_SINGLE_FAMILY_CLOCK_OR_CONTEXT_DOMINATED", max_share <= 0.60, max_share),
        ("SURV-G7_ALPHA_STABLE", alpha_stable, float(primary["Alpha"].median())),
        ("SURV-G8_AIC_BIC_POLICY_PASS", primary_delta > 0.5, primary_delta),
    ]
    df = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_PB_ZERO_DIAGONAL_SURVIVAL_GATES",
                "ProtocolID": PROTOCOL_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "SurvivalClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value in gates
        ]
    )
    status = (
        "P_TAUCOV_PB_ZERO_DIAGONAL_PRIMARY_SCORECARD_SURVIVAL_PATTERN_PASS_NO_CLAIM"
        if bool(df["Passed"].all())
        else "P_TAUCOV_PB_ZERO_DIAGONAL_PRIMARY_SCORECARD_DOES_NOT_SURVIVE_NO_CLAIM"
    )
    return df, status


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the PB zero-diagonal P-TauCov primary scorecard.")
    parser.add_argument("--authorization-manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    manifest = Path(args.authorization_manifest)
    if args.dry_run:
        print("P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_DRY_RUN_NO_SCORING")
        print(f"authorization_manifest_exists={manifest.exists()}")
        return 0

    load_authorization(manifest)
    labels, kernel_raw = matrix_from_row_long(OBJECT)
    kernel, fro = normalize_kernel(kernel_raw)
    if fro == 0.0:
        raise RuntimeError("PB zero-diagonal object has zero Frobenius norm.")

    p5c = import_p5c_module()
    rows = p5c.load_rows()
    if labels != rows["RowID"].astype(str).tolist():
        raise RuntimeError("PB zero-diagonal object row order does not match P5C row order.")

    real_ins, real_oos, primary_delta_base = score_kernel(p5c, rows, kernel, KERNEL_ID)
    context_oos = context_holdout_rows(p5c, rows, kernel)
    real_oos = pd.concat([real_oos, context_oos], ignore_index=True)

    null_kernels: dict[str, tuple[np.ndarray, float]] = pb_diagnostic_nulls(rows)
    for null_id, generic_id in GENERIC_NULL_MAP.items():
        null_kernels[null_id] = normalize_kernel(p5c.matrix_from_long(p5c.NULLS, generic_id, len(rows)))

    null_rows = []
    for null_id, (mat, raw_fro) in null_kernels.items():
        if float(np.linalg.norm(mat, ord="fro")) == 0.0:
            delta = 0.0
            median_alpha = 0.0
        else:
            _, oos, delta = score_kernel(p5c, rows, mat, null_id)
            median_alpha = float(oos[oos["PrimaryOOS"]]["Alpha"].median())
        null_rows.append(
            {
                "AuditID": AUDIT_ID,
                "ProtocolID": PROTOCOL_ID,
                "KernelID": null_id,
                "PrimaryOOSDeltaNLL_BaselineMinusKernel": float(delta),
                "MedianAlpha": median_alpha,
                "KernelFrobeniusNormBeforeNormalization": float(raw_fro),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    null_summary = pd.DataFrame(null_rows)
    gates, status = survival_gates(real_oos, null_summary)
    primary_delta = float(real_oos[real_oos["PrimaryOOS"]]["DeltaNLL_BaselineMinusKernel"].sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": AUDIT_ID,
                "ProtocolID": PROTOCOL_ID,
                "KernelID": KERNEL_ID,
                "Rows": len(rows),
                "Families": rows["FamilyID"].nunique(),
                "ClockPositions": rows["z"].nunique(),
                "KernelFrobeniusNormBeforeNormalization": fro,
                "InSampleDeltaNLL_BaselineMinusKernel": float(real_ins.iloc[0]["DeltaNLL_BaselineMinusKernel"]),
                "PrimaryOOSDeltaNLL_BaselineMinusKernel": primary_delta,
                "PrimaryOOSDeltaNLLWithoutContextBlocks": primary_delta_base,
                "StrongestNullPrimaryOOSDeltaNLL": float(null_summary["PrimaryOOSDeltaNLL_BaselineMinusKernel"].max()),
                "GatesPassed": int(gates["Passed"].sum()),
                "GatesTotal": len(gates),
                "CurrentStatus": status,
                "PTauCovScoringAuthorized": True,
                "SurvivalClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    real_ins.to_csv(OUT_IN_SAMPLE, index=False)
    real_oos.to_csv(OUT_OOS, index=False)
    null_summary.to_csv(OUT_NULLS, index=False)
    gates.to_csv(OUT_GATES, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov PB Zero-Diagonal Scorecard",
                "",
                f"Status: `{status}`",
                "",
                "This is the authorized primary covariance scorecard for the frozen",
                "PB zero-diagonal covariance-response object. It does not authorize",
                "survival language, measurement validation, or a Tau Core validation claim.",
                "",
                "## Key Numbers",
                "",
                f"- rows: {len(rows)}",
                f"- families: {rows['FamilyID'].nunique()}",
                f"- clock positions: {rows['z'].nunique()}",
                f"- primary OOS Delta NLL: {primary_delta}",
                f"- primary OOS Delta NLL without context blocks: {primary_delta_base}",
                f"- strongest null primary OOS Delta NLL: {float(null_summary['PrimaryOOSDeltaNLL_BaselineMinusKernel'].max())}",
                f"- gates passed: {int(gates['Passed'].sum())}/{len(gates)}",
                "",
                "## Interpretation",
                "",
                "The object does not survive the frozen global P-TauCov scorecard. The",
                "family aggregate is positive, but clock/context aggregates are strongly",
                "negative and the object does not defeat the strongest required null.",
                "This is therefore a branch-local diagnostic anomaly at most, not a",
                "global covariance survivor.",
                "",
                "Positive Delta NLL means the declared covariance deformation beats the",
                "diagonal covariance baseline on that score. A failed survival gate remains",
                "a failed survival gate even if individual folds or diagnostics look",
                "interesting.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
