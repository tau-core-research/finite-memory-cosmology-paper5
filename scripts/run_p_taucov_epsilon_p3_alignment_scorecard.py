#!/usr/bin/env python3
"""Run epsilon-P3 P-TauCov bridge-projected covariance scorecard after final authorization.

This script is intentionally inert until a final authorization manifest exists
and explicitly sets `PTauCovScoringAuthorized: true`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization.yaml"
BRANCH_WEIGHTS = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_weights.csv"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_alignment_scorecard.csv"
OOS = ROOT / "evidence/p_taucov_epsilon_p3_alignment_oos_scorecard.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_alignment_scorecard_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_EPSILON_P3_ALIGNMENT_SCORECARD_v1"
CLAIM_BOUNDARY = "epsilon_p3_alignment_scorecard_requires_final_authorization"


def load_authorization() -> dict:
    if not AUTH.exists():
        raise RuntimeError("Missing final authorization manifest; scoring is not authorized.")
    auth = yaml.safe_load(AUTH.read_text(encoding="utf-8")) or {}
    if auth.get("PTauCovScoringAuthorized") is not True:
        raise RuntimeError("Final authorization does not permit P-TauCov scoring.")
    return auth


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


def main() -> int:
    load_authorization()
    tau_ids, delta_tau = matrix_from_long(BRANCH_WEIGHTS, "DeltaCTau")
    empirical_ids, bridge = load_bridge(tau_ids)
    kernel = bridge @ delta_tau @ bridge.T
    fro = float(np.linalg.norm(kernel, ord="fro"))
    if fro == 0.0:
        raise RuntimeError("Bridge-projected epsilon-P3 kernel has zero Frobenius norm.")
    kernel = kernel / fro

    import importlib.util

    spec = importlib.util.spec_from_file_location("p5c_v0", P5C_V0)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load P5C v0 scorecard module.")
    p5c_v0 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p5c_v0)
    p5c_v0.AUDIT_ID = AUDIT_ID
    p5c_v0.PROTOCOL_ID = PROTOCOL_ID
    p5c_v0.KERNEL_ID = "P_TAUCOV_EPSILON_P3_BRIDGE_PROJECTED_KERNEL"
    p5c_v0.CLAIM_BOUNDARY = CLAIM_BOUNDARY
    data_rows = p5c_v0.load_rows()
    expected_ids = data_rows["RowID"].astype(str).tolist()
    if empirical_ids != expected_ids:
        raise RuntimeError("Coordinate bridge empirical row order does not match P5C scorecard row order.")

    in_sample, oos = p5c_v0.score_all(data_rows, kernel, p5c_v0.KERNEL_ID)
    in_sample.to_csv(OUT, index=False)
    oos.to_csv(OOS, index=False)
    primary = oos[oos["PrimaryOOS"]]
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "KernelID": p5c_v0.KERNEL_ID,
                "Rows": len(data_rows),
                "TauCoordinates": len(tau_ids),
                "BridgeRows": len(empirical_ids),
                "KernelFrobeniusNormBeforeNormalization": fro,
                "InSampleDeltaNLL_BaselineMinusKernel": float(in_sample["DeltaNLL_BaselineMinusKernel"].iloc[0]),
                "PrimaryOOSDeltaNLL_BaselineMinusKernel": float(primary["DeltaNLL_BaselineMinusKernel"].sum()),
                "PTauCovScoringAuthorized": True,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    ).to_csv(SUMMARY, index=False)
    print("P_TAUCOV_EPSILON_P3_BRIDGE_PROJECTED_SCORECARD_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
