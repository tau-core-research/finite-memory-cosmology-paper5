#!/usr/bin/env python3
"""Run the expanded parent-operator P-TauCov primary scorecard.

The scorecard is blocked unless the final expanded-object manifest authorizes
the primary covariance scorecard scope. It reports no survival, measurement, or
Tau Core validation claim.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "evidence/p_taucov_expanded_parent_operator_final_manifest.yaml"
CANDIDATE = ROOT / "evidence/p_taucov_expanded_parent_operator_psd_candidate.csv"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"

OUT_IN_SAMPLE = ROOT / "evidence/p_taucov_expanded_parent_operator_scorecard.csv"
OUT_OOS = ROOT / "evidence/p_taucov_expanded_parent_operator_oos_scorecard.csv"
OUT_NULLS = ROOT / "evidence/p_taucov_expanded_parent_operator_null_scorecard.csv"
OUT_GATES = ROOT / "evidence/p_taucov_expanded_parent_operator_survival_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_scorecard_summary.csv"
OUT_DOC = ROOT / "docs/p_taucov_expanded_parent_operator_scorecard.md"

AUTHORIZED_STATUS = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM"
PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PRIMARY_SCORECARD_v1"
KERNEL_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_COVARIANCE_KERNEL"
CLAIM_BOUNDARY = "expanded_parent_operator_primary_scorecard_no_survival_claim"

GENERIC_NULL_MAP = {
    "GENERIC_WRONG_CLOCK": "K_WRONG_CLOCK",
    "GENERIC_PHASE_SHIFT": "K_PHASE_SHIFTED",
    "GENERIC_FAMILY_PERMUTED": "K_FAMILY_PERMUTED",
    "GENERIC_RANDOM_SMOOTH_PSD": "K_RANDOM_SMOOTH_PSD",
    "GENERIC_DIAGONAL": "K_IDENTITY_DIAGONAL",
}


def load_authorization(path: Path) -> dict:
    if not path.exists():
        raise RuntimeError("Missing final authorization manifest; scoring is not authorized.")
    manifest = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if manifest.get("Status") != AUTHORIZED_STATUS:
        raise RuntimeError("Final manifest does not authorize expanded primary scorecard.")
    if manifest.get("PTauCovScoringAuthorized") is not True:
        raise RuntimeError("Final manifest does not authorize P-TauCov scoring.")
    if manifest.get("AuthorizedScope") != "expanded_parent_operator_primary_covariance_scorecard_only":
        raise RuntimeError("Final manifest does not authorize this scorecard scope.")
    return manifest


def matrix_from_coordinate_long(path: Path) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    ids = sorted(set(df["RowCoordinate"].astype(str)) | set(df["ColumnCoordinate"].astype(str)))
    idx = {cid: i for i, cid in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = float(row.Value)
    return ids, 0.5 * (mat + mat.T)


def load_bridge(tau_ids: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    df = pd.read_csv(BRIDGE)
    rows = (
        df[["EmpiricalIndex", "EmpiricalRowID", "FamilyID", "ClockIndex"]]
        .drop_duplicates()
        .sort_values("EmpiricalIndex")
        .reset_index(drop=True)
    )
    row_idx = {rid: i for i, rid in enumerate(rows["EmpiricalRowID"].astype(str))}
    tau_idx = {cid: i for i, cid in enumerate(tau_ids)}
    bridge = np.zeros((len(rows), len(tau_ids)), dtype=float)
    for row in df.itertuples(index=False):
        tau_coordinate = str(row.TauCoordinate)
        if tau_coordinate in tau_idx:
            bridge[row_idx[str(row.EmpiricalRowID)], tau_idx[tau_coordinate]] = float(row.BridgeValue)
    return rows, bridge


def normalize_kernel(kernel: np.ndarray) -> tuple[np.ndarray, float]:
    kernel = 0.5 * (kernel + kernel.T)
    fro = float(np.linalg.norm(kernel, ord="fro"))
    if fro == 0.0:
        return kernel, fro
    return kernel / fro, fro


def import_p5c_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("p5c_v0", P5C_V0)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load P5C v0 scorecard module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT_ID = AUDIT_ID
    module.PROTOCOL_ID = PROTOCOL_ID
    module.KERNEL_ID = KERNEL_ID
    module.CLAIM_BOUNDARY = CLAIM_BOUNDARY
    return module


def projected_kernel(tau_ids: list[str], tau_matrix: np.ndarray, bridge: np.ndarray) -> tuple[np.ndarray, float]:
    kernel = bridge @ tau_matrix @ bridge.T
    return normalize_kernel(kernel)


def coordinate_diag_kernel(tau_ids: list[str], bridge: np.ndarray, coord: str) -> tuple[np.ndarray, float]:
    if coord not in tau_ids:
        return np.zeros((bridge.shape[0], bridge.shape[0])), 0.0
    vec = bridge[:, tau_ids.index(coord)]
    return normalize_kernel(np.outer(vec, vec))


def complement_kernel(tau_ids: list[str], bridge: np.ndarray, active_ids: set[str]) -> tuple[np.ndarray, float]:
    keep = [i for i, cid in enumerate(tau_ids) if cid not in active_ids]
    mat = np.zeros((len(tau_ids), len(tau_ids)), dtype=float)
    for i in keep:
        mat[i, i] = 1.0
    return projected_kernel(tau_ids, mat, bridge)


def shuffled_support_kernel(tau_ids: list[str], tau_matrix: np.ndarray, bridge: np.ndarray) -> tuple[np.ndarray, float]:
    perm = list(range(len(tau_ids)))
    if len(perm) > 1:
        perm = perm[1:] + perm[:1]
    shuffled = tau_matrix[np.ix_(perm, perm)]
    return projected_kernel(tau_ids, shuffled, bridge)


def score_kernel(p5c, rows: pd.DataFrame, kernel: np.ndarray, kernel_id: str) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    ins, oos = p5c.score_all(rows, kernel, kernel_id)
    primary_delta = float(oos[oos["PrimaryOOS"]]["DeltaNLL_BaselineMinusKernel"].sum())
    return ins, oos, primary_delta


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
        ("SURV-G6_NOT_SINGLE_FAMILY_OR_CONTEXT_DOMINATED", max_share <= 0.60, max_share),
        ("SURV-G7_ALPHA_STABLE", alpha_stable, float(primary["Alpha"].median())),
        ("SURV-G8_AIC_BIC_POLICY_PASS", primary_delta > 0.5, primary_delta),
    ]
    df = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SURVIVAL_GATES",
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
        "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PRIMARY_SCORECARD_SURVIVAL_PATTERN_PASS_NO_CLAIM"
        if bool(df["Passed"].all())
        else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PRIMARY_SCORECARD_DOES_NOT_SURVIVE_NO_CLAIM"
    )
    return df, status


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the expanded P-TauCov primary covariance scorecard.")
    parser.add_argument("--authorization-manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = Path(args.authorization_manifest)
    if args.dry_run:
        print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORECARD_DRY_RUN_NO_SCORING")
        print(f"authorization_manifest_exists={manifest.exists()}")
        return 0

    load_authorization(manifest)
    tau_ids, tau_matrix = matrix_from_coordinate_long(CANDIDATE)
    bridge_rows, bridge = load_bridge(tau_ids)
    kernel, fro = projected_kernel(tau_ids, tau_matrix, bridge)
    if fro == 0.0:
        raise RuntimeError("Expanded parent-operator empirical kernel has zero Frobenius norm.")

    p5c = import_p5c_module()
    rows = p5c.load_rows()
    expected_ids = rows["RowID"].astype(str).tolist()
    if bridge_rows["EmpiricalRowID"].astype(str).tolist() != expected_ids:
        raise RuntimeError("Coordinate bridge empirical row order does not match P5C scorecard row order.")

    real_ins, real_oos, primary_delta_base = score_kernel(p5c, rows, kernel, KERNEL_ID)
    context_oos = context_holdout_rows(p5c, rows, kernel)
    real_oos = pd.concat([real_oos, context_oos], ignore_index=True)

    active_ids = set(tau_ids)
    null_kernels: dict[str, np.ndarray] = {}
    null_fros: dict[str, float] = {}
    for null_id, coord in {
        "MORPHOLOGY_NULL": "TEMPLATE_M_PARENT_MORPHOLOGY",
        "PROJECTION_NULL": "TEMPLATE_P_MORPH_PROJECTION",
        "SCALE_ONLY_NULL": "TEMPLATE_COORD_SCALE_UNIT",
        "CONTEXT_ONLY_NULL": "TEMPLATE_EXT_OBSERVING_CONTEXT",
    }.items():
        null_kernels[null_id], null_fros[null_id] = coordinate_diag_kernel(tau_ids, bridge, coord)
    null_kernels["OUTSIDE_EXPANDED_SUPPORT"], null_fros["OUTSIDE_EXPANDED_SUPPORT"] = complement_kernel(tau_ids, bridge, active_ids)
    null_kernels["SHUFFLED_EXPANDED_SUPPORT"], null_fros["SHUFFLED_EXPANDED_SUPPORT"] = shuffled_support_kernel(tau_ids, tau_matrix, bridge)

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
                "TauCoordinates": len(tau_ids),
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
                "# P-TauCov Expanded Parent-Operator Scorecard",
                "",
                f"Status: `{status}`",
                "",
                "This is the authorized primary covariance scorecard for the expanded",
                "parent-operator PSD object. It does not authorize survival language,",
                "measurement validation, or a Tau Core validation claim.",
                "",
                "## Key Numbers",
                "",
                f"- rows: {len(rows)}",
                f"- tau coordinates: {len(tau_ids)}",
                f"- primary OOS Delta NLL: {primary_delta}",
                f"- primary OOS Delta NLL without context blocks: {primary_delta_base}",
                f"- strongest null primary OOS Delta NLL: {float(null_summary['PrimaryOOSDeltaNLL_BaselineMinusKernel'].max())}",
                f"- gates passed: {int(gates['Passed'].sum())}/{len(gates)}",
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
