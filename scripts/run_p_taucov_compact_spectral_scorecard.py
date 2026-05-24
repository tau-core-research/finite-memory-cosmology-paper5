#!/usr/bin/env python3
"""Run the compact spectral P-TauCov primary scorecard.

The scorecard is blocked unless the final compact spectral manifest authorizes
the primary covariance-deformation scope. The compact source is an oriented
spectral residue; the primary covariance test therefore uses its frozen PSD
projection and reports no survival, measurement, or Tau Core validation claim.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "evidence/p_taucov_compact_spectral_final_manifest.yaml"
SOURCE = ROOT / "evidence/p_taucov_compact_spectral_residue_source.csv"
SPECTRUM = ROOT / "evidence/p_taucov_compact_spectral_residue_source_spectrum.csv"
Q_RANGE = ROOT / "evidence/p_taucov_q_range_projector_matrix.csv"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
SOURCE_BUILDER = ROOT / "scripts/build_p_taucov_compact_spectral_residue_source.py"

OUT_IN_SAMPLE = ROOT / "evidence/p_taucov_compact_spectral_scorecard.csv"
OUT_OOS = ROOT / "evidence/p_taucov_compact_spectral_oos_scorecard.csv"
OUT_NULLS = ROOT / "evidence/p_taucov_compact_spectral_null_scorecard.csv"
OUT_GATES = ROOT / "evidence/p_taucov_compact_spectral_survival_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_scorecard_summary.csv"
OUT_DOC = ROOT / "docs/p_taucov_compact_spectral_scorecard.md"

AUTHORIZED_STATUS = "P_TAUCOV_COMPACT_SPECTRAL_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM"
PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_COMPACT_SPECTRAL_PRIMARY_SCORECARD_v1"
KERNEL_ID = "P_TAUCOV_COMPACT_SPECTRAL_PSD_COVARIANCE_KERNEL"
CLAIM_BOUNDARY = "compact_spectral_primary_scorecard_no_survival_claim"

GENERIC_NULL_MAP = {
    "GENERIC_RANDOM_SMOOTH_PSD": "K_RANDOM_SMOOTH_PSD",
    "PROJECTION_NULL": "K_PHASE_SHIFTED",
    "GENERIC_WRONG_CLOCK": "K_WRONG_CLOCK",
    "GENERIC_PHASE_SHIFT": "K_PHASE_SHIFTED",
    "GENERIC_FAMILY_PERMUTED": "K_FAMILY_PERMUTED",
    "GENERIC_DIAGONAL": "K_IDENTITY_DIAGONAL",
}


def load_authorization(path: Path) -> dict:
    if not path.exists():
        raise RuntimeError("Missing final authorization manifest; scoring is not authorized.")
    manifest = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if manifest.get("Status") != AUTHORIZED_STATUS:
        raise RuntimeError("Final manifest does not authorize compact spectral scorecard.")
    if manifest.get("PTauCovScoringAuthorized") is not True:
        raise RuntimeError("Final manifest does not authorize P-TauCov scoring.")
    if manifest.get("AuthorizedScope") != "compact_spectral_primary_covariance_scorecard_only":
        raise RuntimeError("Final manifest does not authorize this scorecard scope.")
    return manifest


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


def psd_projection(kernel: np.ndarray) -> tuple[np.ndarray, float, float, int]:
    kernel = 0.5 * (kernel + kernel.T)
    eigvals, eigvecs = np.linalg.eigh(kernel)
    positive = eigvals > 1e-12
    psd_raw = eigvecs[:, positive] @ np.diag(eigvals[positive]) @ eigvecs[:, positive].T
    psd, _ = normalize_kernel(psd_raw)
    signed_norm = float(np.linalg.norm(kernel, ord="fro"))
    retention = 0.0 if signed_norm == 0.0 else float(np.linalg.norm(psd_raw, ord="fro") / signed_norm)
    return psd, signed_norm, retention, int(positive.sum())


def matrix_from_row_long(path: Path) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    labels = list(dict.fromkeys(df["RowID"].astype(str)))
    idx = {label: i for i, label in enumerate(labels)}
    mat = np.zeros((len(labels), len(labels)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowID)], idx[str(row.ColumnID)]] = float(row.Value)
    return labels, 0.5 * (mat + mat.T)


def import_p5c_module():
    p5c = load_module(P5C_V0, "p5c_v0")
    p5c.AUDIT_ID = AUDIT_ID
    p5c.PROTOCOL_ID = PROTOCOL_ID
    p5c.KERNEL_ID = KERNEL_ID
    p5c.CLAIM_BOUNDARY = CLAIM_BOUNDARY
    return p5c


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


def spectral_shuffle(kernel: np.ndarray) -> np.ndarray:
    eigvals, eigvecs = np.linalg.eigh(0.5 * (kernel + kernel.T))
    perm = np.arange(len(eigvals))
    if len(perm) > 1:
        perm = np.roll(perm, 1)
    shuffled = eigvecs[:, perm] @ np.diag(eigvals) @ eigvecs[:, perm].T
    psd, *_ = psd_projection(shuffled)
    return psd


def spectral_low_pass_complement(p5c, rows: pd.DataFrame) -> np.ndarray:
    builder = load_module(SOURCE_BUILDER, "compact_source_builder")
    labels, q_range = builder.load_square_matrix(Q_RANGE, ("RowID", "ColumnID"))
    if labels != rows["RowID"].astype(str).tolist():
        raise RuntimeError("Q-range labels do not match P5C row order.")
    lap = builder.clock_laplacian(rows)
    compact_operator = 0.5 * (q_range @ lap @ q_range + (q_range @ lap @ q_range).T)
    evals, evecs = np.linalg.eigh(compact_operator)
    spectrum = pd.read_csv(SPECTRUM)
    selected = set(spectrum.loc[spectrum["SelectedForResidue"].astype(bool), "EigenIndex"].astype(int))
    low_active = [
        int(i)
        for i, value in enumerate(evals)
        if value > builder.EIGEN_THRESHOLD and int(i) not in selected
    ]
    if not low_active:
        return np.zeros((len(rows), len(rows)))
    complement = np.zeros_like(compact_operator)
    for idx in low_active:
        vec = evecs[:, idx]
        complement += float(evals[idx]) * np.outer(vec, vec)
    smooth, _ = normalize_kernel(p5c.matrix_from_long(p5c.NULLS, "K_RANDOM_SMOOTH_PSD", len(rows)))
    projection, _ = normalize_kernel(p5c.matrix_from_long(p5c.NULLS, "K_PHASE_SHIFTED", len(rows)))
    diagonal, _ = normalize_kernel(np.eye(len(rows)))
    complement = builder.remove_direction(complement, smooth)
    complement = builder.remove_direction(complement, projection)
    complement = builder.remove_direction(complement, diagonal)
    complement = q_range @ complement @ q_range
    psd, *_ = psd_projection(complement)
    return psd


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
                "AuditID": "P_TAUCOV_COMPACT_SPECTRAL_SURVIVAL_GATES",
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
        "P_TAUCOV_COMPACT_SPECTRAL_PRIMARY_SCORECARD_SURVIVAL_PATTERN_PASS_NO_CLAIM"
        if bool(df["Passed"].all())
        else "P_TAUCOV_COMPACT_SPECTRAL_PRIMARY_SCORECARD_DOES_NOT_SURVIVE_NO_CLAIM"
    )
    return df, status


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the compact spectral P-TauCov primary scorecard.")
    parser.add_argument("--authorization-manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = Path(args.authorization_manifest)
    if args.dry_run:
        print("P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_DRY_RUN_NO_SCORING")
        print(f"authorization_manifest_exists={manifest.exists()}")
        return 0

    load_authorization(manifest)
    labels, signed_source = matrix_from_row_long(SOURCE)
    kernel, signed_norm, psd_retention, psd_rank = psd_projection(signed_source)
    if float(np.linalg.norm(kernel, ord="fro")) == 0.0:
        raise RuntimeError("Compact spectral PSD projection has zero Frobenius norm.")

    p5c = import_p5c_module()
    rows = p5c.load_rows()
    if labels != rows["RowID"].astype(str).tolist():
        raise RuntimeError("Compact spectral source row order does not match P5C scorecard row order.")

    real_ins, real_oos, primary_delta_base = score_kernel(p5c, rows, kernel, KERNEL_ID)
    real_oos = pd.concat([real_oos, context_holdout_rows(p5c, rows, kernel)], ignore_index=True)

    null_kernels: dict[str, np.ndarray] = {
        "SPECTRAL_MODE_SHUFFLE": spectral_shuffle(signed_source),
        "SPECTRAL_LOW_PASS_COMPLEMENT": spectral_low_pass_complement(p5c, rows),
    }
    null_fros: dict[str, float] = {
        key: float(np.linalg.norm(value, ord="fro")) for key, value in null_kernels.items()
    }
    for null_id, generic_id in GENERIC_NULL_MAP.items():
        mat = p5c.matrix_from_long(p5c.NULLS, generic_id, len(rows))
        null_kernels[null_id], null_fros[null_id] = normalize_kernel(mat)

    null_rows = []
    for null_id, mat in null_kernels.items():
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
                "KernelFrobeniusNormBeforeNormalization": float(null_fros[null_id]),
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
                "SignedSourceFrobeniusNorm": signed_norm,
                "PSDProjectionRank": psd_rank,
                "PSDProjectionFrobeniusNorm": float(np.linalg.norm(kernel, ord="fro")),
                "PSDProjectionRetainedAsPrimaryCovarianceObject": psd_retention,
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
                "# P-TauCov Compact Spectral Scorecard",
                "",
                f"Status: `{status}`",
                "",
                "This is the authorized primary covariance scorecard for the compact",
                "spectral residue route. The signed residue source is projected to its",
                "PSD covariance object before scoring. This does not authorize survival",
                "language, measurement validation, or a Tau Core validation claim.",
                "",
                "## Key Numbers",
                "",
                f"- rows: `{len(rows)}`",
                f"- PSD projection rank: `{psd_rank}`",
                f"- primary OOS Delta NLL: `{primary_delta}`",
                f"- primary OOS Delta NLL without context blocks: `{primary_delta_base}`",
                f"- strongest null primary OOS Delta NLL: `{float(null_summary['PrimaryOOSDeltaNLL_BaselineMinusKernel'].max())}`",
                f"- gates passed: `{int(gates['Passed'].sum())}/{len(gates)}`",
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
