#!/usr/bin/env python3
"""Run the epsilon-P3 P-TauCov null/survival suite."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization.yaml"
BRANCH_WEIGHTS = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_weights.csv"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
OUT_NULLS = ROOT / "evidence/p_taucov_epsilon_p3_null_suite_scorecard.csv"
OUT_GATES = ROOT / "evidence/p_taucov_epsilon_p3_survival_gate_results.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_null_survival_summary.csv"
DOC = ROOT / "docs/p_taucov_epsilon_p3_null_survival_suite.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_EPSILON_P3_NULL_SURVIVAL_SUITE_v1"
CLAIM_BOUNDARY = "epsilon_p3_null_survival_suite_no_measurement_validation"


def matrix_from_long(path: Path, value_col: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    ids = sorted(set(df["RowCoordinate"].astype(str)) | set(df["ColumnCoordinate"].astype(str)))
    idx = {cid: i for i, cid in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = float(getattr(row, value_col))
    return ids, mat


def load_bridge(tau_ids: list[str]) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(BRIDGE)
    row_ids = df[["EmpiricalIndex", "EmpiricalRowID"]].drop_duplicates().sort_values("EmpiricalIndex")["EmpiricalRowID"].astype(str).tolist()
    row_idx = {rid: i for i, rid in enumerate(row_ids)}
    tau_idx = {cid: i for i, cid in enumerate(tau_ids)}
    bridge = np.zeros((len(row_ids), len(tau_ids)), dtype=float)
    for row in df.itertuples(index=False):
        if str(row.TauCoordinate) in tau_idx:
            bridge[row_idx[str(row.EmpiricalRowID)], tau_idx[str(row.TauCoordinate)]] = float(row.BridgeValue)
    return row_ids, bridge


def normalize_kernel(kernel: np.ndarray) -> np.ndarray:
    kernel = 0.5 * (kernel + kernel.T)
    eigvals, eigvecs = np.linalg.eigh(kernel)
    eigvals = np.clip(eigvals, 0.0, None)
    kernel = eigvecs @ np.diag(eigvals) @ eigvecs.T
    kernel = 0.5 * (kernel + kernel.T)
    fro = float(np.linalg.norm(kernel, ord="fro"))
    if fro == 0.0:
        return kernel
    return kernel / fro


def project(bridge: np.ndarray, delta: np.ndarray) -> np.ndarray:
    return normalize_kernel(bridge @ delta @ bridge.T)


def score_kernel(rows: pd.DataFrame, p5c_v0, kernel: np.ndarray, kernel_id: str) -> dict:
    _, oos = p5c_v0.score_all(rows, kernel, kernel_id)
    primary = oos[oos["PrimaryOOS"]]
    lofo = primary[primary["FoldClass"].eq("primary_leave_one_family_out")]
    clock = primary[primary["FoldClass"].eq("primary_contiguous_clock_block")]
    positive = lofo[lofo["DeltaNLL_BaselineMinusKernel"] > 0.0]
    if float(positive["DeltaNLL_BaselineMinusKernel"].sum()) > 0.0:
        max_family_share = float(positive["DeltaNLL_BaselineMinusKernel"].max() / positive["DeltaNLL_BaselineMinusKernel"].sum())
    else:
        max_family_share = 1.0
    return {
        "KernelID": kernel_id,
        "PrimaryOOSDeltaNLL": float(primary["DeltaNLL_BaselineMinusKernel"].sum()),
        "LOFODeltaNLL": float(lofo["DeltaNLL_BaselineMinusKernel"].sum()),
        "ClockBlockDeltaNLL": float(clock["DeltaNLL_BaselineMinusKernel"].sum()),
        "MedianAlpha": float(primary["Alpha"].median()),
        "MaxPositiveFamilyShare": max_family_share,
    }


def main() -> int:
    auth = yaml.safe_load(AUTH.read_text(encoding="utf-8")) or {}
    if auth.get("PTauCovScoringAuthorized") is not True:
        raise RuntimeError("Primary scoring authorization is missing.")

    tau_ids, delta = matrix_from_long(BRANCH_WEIGHTS, "DeltaCTau")
    _, weights = matrix_from_long(BRANCH_WEIGHTS, "WBranch")
    bridge_ids, bridge = load_bridge(tau_ids)
    spec = importlib.util.spec_from_file_location("p5c_v0", P5C_V0)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load P5C v0 scorecard module.")
    p5c_v0 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p5c_v0)
    p5c_v0.AUDIT_ID = AUDIT_ID
    p5c_v0.PROTOCOL_ID = PROTOCOL_ID
    p5c_v0.CLAIM_BOUNDARY = CLAIM_BOUNDARY
    rows = p5c_v0.load_rows()
    if bridge_ids != rows["RowID"].astype(str).tolist():
        raise RuntimeError("Bridge row order mismatch.")

    omega = pd.read_csv(BRANCH_WEIGHTS).pivot(index="RowCoordinate", columns="ColumnCoordinate", values="OmegaBranch")
    omega = omega.reindex(index=tau_ids, columns=tau_ids).fillna(False).astype(bool).to_numpy()
    outside = ~omega
    shift_mask = np.roll(omega.reshape(-1), 7).reshape(omega.shape)
    tau_index = {cid: i for i, cid in enumerate(tau_ids)}
    p_idx = tau_index.get("TEMPLATE_P_MORPH_PROJECTION")
    m_idx = tau_index.get("TEMPLATE_M_PARENT_MORPHOLOGY")

    kernels = {
        "TAU_EPSILON_P3_PRIMARY": project(bridge, delta),
        "OUTSIDE_BRANCH": project(bridge, delta * outside),
        "SHUFFLED_SUPPORT": project(bridge, delta * shift_mask),
        "GENERIC_DIAGONAL": normalize_kernel(np.diag(np.diag(project(bridge, delta)))),
    }
    morph_delta = delta.copy()
    if m_idx is not None:
        morph_delta[m_idx, :] = 0.0
        morph_delta[:, m_idx] = 0.0
    kernels["MORPHOLOGY_NULL"] = project(bridge, morph_delta)
    bridge_proj_null = bridge.copy()
    if p_idx is not None:
        bridge_proj_null[:, p_idx] = 0.0
    kernels["PROJECTION_NULL"] = project(bridge_proj_null, delta)

    results = [score_kernel(rows, p5c_v0, kernel, kernel_id) for kernel_id, kernel in kernels.items()]
    results_df = pd.DataFrame(results)
    results_df.insert(0, "AuditID", AUDIT_ID)
    results_df.insert(0, "ProtocolID", PROTOCOL_ID)
    results_df["ClaimBoundary"] = CLAIM_BOUNDARY
    results_df.to_csv(OUT_NULLS, index=False)

    primary_delta = float(results_df.loc[results_df["KernelID"].eq("TAU_EPSILON_P3_PRIMARY"), "PrimaryOOSDeltaNLL"].iloc[0])
    nulls = results_df[~results_df["KernelID"].eq("TAU_EPSILON_P3_PRIMARY")]
    strongest_null = nulls.sort_values(["PrimaryOOSDeltaNLL", "KernelID"], ascending=[False, True]).iloc[0]
    gates = [
        ("G1_PRIMARY_POSITIVE", primary_delta > 0.0, primary_delta),
        ("G2_BEATS_OUTSIDE_BRANCH", primary_delta > float(results_df.loc[results_df["KernelID"].eq("OUTSIDE_BRANCH"), "PrimaryOOSDeltaNLL"].iloc[0]), primary_delta - float(results_df.loc[results_df["KernelID"].eq("OUTSIDE_BRANCH"), "PrimaryOOSDeltaNLL"].iloc[0])),
        ("G3_BEATS_SHUFFLED_SUPPORT", primary_delta > float(results_df.loc[results_df["KernelID"].eq("SHUFFLED_SUPPORT"), "PrimaryOOSDeltaNLL"].iloc[0]), primary_delta - float(results_df.loc[results_df["KernelID"].eq("SHUFFLED_SUPPORT"), "PrimaryOOSDeltaNLL"].iloc[0])),
        ("G4_BEATS_MORPHOLOGY_NULL", primary_delta > float(results_df.loc[results_df["KernelID"].eq("MORPHOLOGY_NULL"), "PrimaryOOSDeltaNLL"].iloc[0]), primary_delta - float(results_df.loc[results_df["KernelID"].eq("MORPHOLOGY_NULL"), "PrimaryOOSDeltaNLL"].iloc[0])),
        ("G5_BEATS_PROJECTION_NULL", primary_delta > float(results_df.loc[results_df["KernelID"].eq("PROJECTION_NULL"), "PrimaryOOSDeltaNLL"].iloc[0]), primary_delta - float(results_df.loc[results_df["KernelID"].eq("PROJECTION_NULL"), "PrimaryOOSDeltaNLL"].iloc[0])),
        ("G6_BEATS_STRONGEST_DECLARED_NULL", primary_delta > float(strongest_null["PrimaryOOSDeltaNLL"]), primary_delta - float(strongest_null["PrimaryOOSDeltaNLL"])),
        ("G7_NO_SINGLE_FAMILY_DOMINANCE", float(results_df.loc[results_df["KernelID"].eq("TAU_EPSILON_P3_PRIMARY"), "MaxPositiveFamilyShare"].iloc[0]) <= 0.60, float(results_df.loc[results_df["KernelID"].eq("TAU_EPSILON_P3_PRIMARY"), "MaxPositiveFamilyShare"].iloc[0])),
    ]
    gates_df = pd.DataFrame(
        [{"ProtocolID": PROTOCOL_ID, "AuditID": AUDIT_ID, "GateID": gate, "Passed": bool(passed), "DiagnosticValue": value, "ClaimBoundary": CLAIM_BOUNDARY} for gate, passed, value in gates]
    )
    gates_df.to_csv(OUT_GATES, index=False)
    passed = int(gates_df["Passed"].sum())
    status = "P_TAUCOV_EPSILON_P3_SURVIVES_DECLARED_NULL_SUITE" if passed == len(gates_df) else "P_TAUCOV_EPSILON_P3_PRIMARY_POSITIVE_BUT_NO_SURVIVAL"
    pd.DataFrame(
        [{
            "ProtocolID": PROTOCOL_ID,
            "AuditID": AUDIT_ID,
            "Status": status,
            "GatesPassed": passed,
            "GatesTotal": len(gates_df),
            "PrimaryOOSDeltaNLL": primary_delta,
            "StrongestNullID": strongest_null["KernelID"],
            "StrongestNullPrimaryOOSDeltaNLL": float(strongest_null["PrimaryOOSDeltaNLL"]),
            "SurvivalClaimAllowed": status.endswith("SURVIVES_DECLARED_NULL_SUITE"),
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }]
    ).to_csv(OUT_SUMMARY, index=False)
    DOC.write_text(f"""# P-TauCov Epsilon-P3 Null Survival Suite

Status: `{status}`.

Primary OOS DeltaNLL: `{primary_delta}`.

Strongest declared null: `{strongest_null['KernelID']}` with OOS DeltaNLL
`{float(strongest_null['PrimaryOOSDeltaNLL'])}`.

Gates passed: `{passed}/{len(gates_df)}`.

Measurement validation remains forbidden.
""", encoding="utf-8")
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
