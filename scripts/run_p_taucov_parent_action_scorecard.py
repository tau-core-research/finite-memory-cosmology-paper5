#!/usr/bin/env python3
"""Run the parent-action P-TauCov primary covariance scorecard."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "evidence/p_taucov_parent_action_final_manifest.yaml"
COV_MAP = ROOT / "evidence/p_taucov_covariance_map_matrix.csv"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
OUT = ROOT / "evidence/p_taucov_parent_action_scorecard.csv"
OOS = ROOT / "evidence/p_taucov_parent_action_oos_scorecard.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_scorecard_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_PARENT_ACTION_PRIMARY_SCORECARD_v1"
KERNEL_ID = "P_TAUCOV_PARENT_ACTION_PSD_COVARIANCE_KERNEL"
CLAIM_BOUNDARY = "parent_action_primary_scorecard_no_survival_claim"

COORDINATE_ALIASES = {
    "Phi_source": "TEMPLATE_PHI_PARENT_SOURCE",
    "P_projection": "TEMPLATE_P_MORPH_PROJECTION",
}


def load_authorization(path: Path) -> dict:
    if not path.exists():
        raise RuntimeError("Missing final authorization manifest; scoring is not authorized.")
    manifest = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if manifest.get("PTauCovScoringAuthorized") is not True:
        raise RuntimeError("Final manifest does not authorize P-TauCov scoring.")
    if manifest.get("AuthorizedScope") != "parent_action_primary_covariance_scorecard_only":
        raise RuntimeError("Final manifest does not authorize this scorecard scope.")
    return manifest


def matrix_from_long(path: Path) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    ids = sorted(set(df["RowCoordinate"].astype(str)) | set(df["ColumnCoordinate"].astype(str)))
    idx = {cid: i for i, cid in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = float(row.Value)
    return ids, 0.5 * (mat + mat.T)


def load_bridge(tau_ids: list[str]) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(BRIDGE)
    row_ids = (
        df[["EmpiricalIndex", "EmpiricalRowID"]]
        .drop_duplicates()
        .sort_values("EmpiricalIndex")["EmpiricalRowID"]
        .astype(str)
        .tolist()
    )
    row_idx = {rid: i for i, rid in enumerate(row_ids)}
    tau_idx = {COORDINATE_ALIASES.get(cid, cid): i for i, cid in enumerate(tau_ids)}
    bridge = np.zeros((len(row_ids), len(tau_ids)), dtype=float)
    for row in df.itertuples(index=False):
        tau_coordinate = str(row.TauCoordinate)
        if tau_coordinate in tau_idx:
            bridge[row_idx[str(row.EmpiricalRowID)], tau_idx[tau_coordinate]] = float(row.BridgeValue)
    return row_ids, bridge


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the parent-action P-TauCov scorecard only after final authorization.")
    parser.add_argument("--authorization-manifest", default=str(DEFAULT_MANIFEST), help="Final authorization manifest path.")
    parser.add_argument("--dry-run", action="store_true", help="Report authorization state without scoring.")
    args = parser.parse_args()

    manifest = Path(args.authorization_manifest)
    if args.dry_run:
        print("P_TAUCOV_PARENT_ACTION_SCORECARD_DRY_RUN_NO_SCORING")
        print(f"authorization_manifest_exists={manifest.exists()}")
        return 0
    load_authorization(manifest)
    tau_ids, delta_tau = matrix_from_long(COV_MAP)
    empirical_ids, bridge = load_bridge(tau_ids)
    kernel = bridge @ delta_tau @ bridge.T
    fro = float(np.linalg.norm(kernel, ord="fro"))
    if fro == 0.0:
        raise RuntimeError("Bridge-projected parent-action kernel has zero Frobenius norm.")
    kernel = kernel / fro

    import importlib.util

    spec = importlib.util.spec_from_file_location("p5c_v0", P5C_V0)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load P5C v0 scorecard module.")
    p5c_v0 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p5c_v0)
    p5c_v0.AUDIT_ID = AUDIT_ID
    p5c_v0.PROTOCOL_ID = PROTOCOL_ID
    p5c_v0.KERNEL_ID = KERNEL_ID
    p5c_v0.CLAIM_BOUNDARY = CLAIM_BOUNDARY
    rows = p5c_v0.load_rows()
    expected_ids = rows["RowID"].astype(str).tolist()
    if empirical_ids != expected_ids:
        raise RuntimeError("Coordinate bridge empirical row order does not match P5C scorecard row order.")

    in_sample, oos = p5c_v0.score_all(rows, kernel, KERNEL_ID)
    in_sample.to_csv(OUT, index=False)
    oos.to_csv(OOS, index=False)
    primary = oos[oos["PrimaryOOS"]]
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "KernelID": KERNEL_ID,
                "Rows": len(rows),
                "TauCoordinates": len(tau_ids),
                "BridgeRows": len(empirical_ids),
                "KernelFrobeniusNormBeforeNormalization": fro,
                "InSampleDeltaNLL_BaselineMinusKernel": float(in_sample["DeltaNLL_BaselineMinusKernel"].iloc[0]),
                "PrimaryOOSDeltaNLL_BaselineMinusKernel": float(primary["DeltaNLL_BaselineMinusKernel"].sum()),
                "PTauCovScoringAuthorized": True,
                "SurvivalClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    print("P_TAUCOV_PARENT_ACTION_PRIMARY_SCORECARD_COMPLETE_NO_SURVIVAL_CLAIM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
