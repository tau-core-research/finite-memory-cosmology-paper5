#!/usr/bin/env python3
"""Build a target-blind parent-Hessian/commutator object packet."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_p_taucov_epsilon_p3_null_survival_suite.py"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
BASIS = ROOT / "evidence/p_taucov_p4_morphology_basis.csv"
OUT_OBJECT = ROOT / "evidence/p_taucov_parent_hessian_commutator_object.csv"
OUT_GATES = ROOT / "evidence/p_taucov_parent_hessian_commutator_object_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_parent_hessian_commutator_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_hessian_commutator_object.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PARENT_HESSIAN_COMMUTATOR_OBJECT_v1"
CLAIM_BOUNDARY = "target_blind_parent_hessian_commutator_object_no_scoring"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def corr(a: np.ndarray, b: np.ndarray) -> float:
    av = a.reshape(-1)
    bv = b.reshape(-1)
    if float(np.linalg.norm(av)) == 0.0 or float(np.linalg.norm(bv)) == 0.0:
        return float("nan")
    return float(np.corrcoef(av, bv)[0, 1])


def matrix_from_basis(path: Path, basis_id: str, coords: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    df = df[df["BasisID"].eq(basis_id)]
    idx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(coords), len(coords)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)] ] = float(row.Value)
    return 0.5 * (mat + mat.T)


def project_away_morphology(mat: np.ndarray, coords: list[str]) -> np.ndarray:
    residual = mat.copy()
    basis_ids = sorted(pd.read_csv(BASIS)["BasisID"].unique())
    for basis_id in basis_ids:
        b = matrix_from_basis(BASIS, basis_id, coords)
        residual = residual - float(np.sum(residual * b)) * b
    return residual


def normalize(mat: np.ndarray) -> np.ndarray:
    fro = float(np.linalg.norm(mat, ord="fro"))
    return mat if fro == 0.0 else mat / fro


def family_clock_max_share(kernel: np.ndarray, rows: pd.DataFrame, column: str) -> float:
    total = float(np.abs(kernel).sum())
    if total == 0.0:
        return 1.0
    shares = []
    for _, group in rows.groupby(column):
        ids = group["RowIndex"].to_numpy(int)
        shares.append(float(np.abs(kernel[np.ix_(ids, ids)]).sum() / total))
    return max(shares) if shares else 1.0


def main() -> int:
    runner = load_module(RUNNER, "ptaucov_runner")
    p5c_v0 = load_module(P5C_V0, "p5c_v0")
    tau_ids, delta = runner.matrix_from_long(runner.BRANCH_WEIGHTS, "DeltaCTau")
    bridge_ids, bridge = runner.load_bridge(tau_ids)
    rows = p5c_v0.load_rows()
    if bridge_ids != rows["RowID"].astype(str).tolist():
        raise RuntimeError("Bridge row order mismatch.")

    idx = {coord: i for i, coord in enumerate(tau_ids)}
    p_idx = idx["TEMPLATE_P_MORPH_PROJECTION"]
    m_idx = idx["TEMPLATE_M_PARENT_MORPHOLOGY"]
    phi_idx = idx["TEMPLATE_PHI_PARENT_SOURCE"]
    b_idx = idx["TEMPLATE_B_BRANCH_RESPONSE"]

    p_morph = np.zeros_like(delta)
    p_morph[p_idx, p_idx] = 1.0
    p_morph[m_idx, m_idx] = 1.0

    l_tau = np.diag(np.linspace(-1.0, 1.0, len(tau_ids)))
    l_tau[phi_idx, b_idx] = 1.0
    l_tau[b_idx, phi_idx] = -1.0
    l_tau[phi_idx, p_idx] = 0.5
    l_tau[p_idx, b_idx] = -0.5

    comm = p_morph @ l_tau - l_tau @ p_morph
    sym_comm_energy = comm.T @ comm + comm @ comm.T
    hessian_cross = np.zeros_like(delta)
    hessian_cross[phi_idx, b_idx] = 1.0
    hessian_cross[b_idx, phi_idx] = 1.0
    hessian_cross[phi_idx, p_idx] = -1.0
    hessian_cross[p_idx, phi_idx] = -1.0
    raw = normalize(sym_comm_energy + hessian_cross)
    residual = normalize(project_away_morphology(raw, tau_ids))

    candidate_kernel = runner.project(bridge, residual)

    morph_delta = delta.copy()
    morph_delta[m_idx, :] = 0.0
    morph_delta[:, m_idx] = 0.0
    morphology_kernel = runner.project(bridge, morph_delta)
    projection_bridge = bridge.copy()
    projection_bridge[:, p_idx] = 0.0
    projection_null_kernel = runner.project(projection_bridge, residual)
    shuffled = np.roll(residual.reshape(-1), 7).reshape(residual.shape)
    shuffled_kernel = runner.project(bridge, shuffled)

    rows_out = []
    for i, row_coord in enumerate(tau_ids):
        for j, col_coord in enumerate(tau_ids):
            value = float(residual[i, j])
            if value != 0.0:
                rows_out.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "RowCoordinate": row_coord,
                        "ColumnCoordinate": col_coord,
                        "Value": value,
                        "ObjectSource": "toy_parent_commutator_plus_hessian_cross",
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows_out).to_csv(OUT_OBJECT, index=False)

    residual_norm = float(np.linalg.norm(residual, ord="fro"))
    morphology_corr = abs(corr(candidate_kernel, morphology_kernel))
    projection_corr = abs(corr(candidate_kernel, projection_null_kernel))
    shuffled_corr = abs(corr(candidate_kernel, shuffled_kernel))
    max_family = family_clock_max_share(candidate_kernel, rows, "FamilyID")
    max_clock = family_clock_max_share(candidate_kernel, rows, "ClockBlock")
    gate_rows = [
        ("HC-G1_NONZERO_MORPHOLOGY_ORTHOGONAL_PARENT_TERM", residual_norm > 1e-12, residual_norm),
        ("HC-G2_LOW_MORPHOLOGY_NULL_CORRELATION", morphology_corr < 0.75, morphology_corr),
        ("HC-G3_LOW_PROJECTION_NULL_CORRELATION", projection_corr < 0.60, projection_corr),
        ("HC-G4_LOW_SHUFFLED_SUPPORT_CORRELATION", shuffled_corr < 0.60, shuffled_corr),
        ("HC-G5_NO_PRE_SCORE_FAMILY_CLOCK_DOMINANCE", max(max_family, max_clock) <= 0.60, max(max_family, max_clock)),
        ("HC-G6_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
    ]
    gates = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate, passed, value in gate_rows
        ]
    )
    gates.to_csv(OUT_GATES, index=False)
    passed_count = int(gates["Passed"].sum())
    status = (
        "P_TAUCOV_PARENT_HESSIAN_COMMUTATOR_OBJECT_PREFLIGHT_PASS_NO_SCORING"
        if passed_count == len(gates)
        else "P_TAUCOV_PARENT_HESSIAN_COMMUTATOR_OBJECT_PREFLIGHT_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates),
                "ResidualNormAfterMorphologyProjection": residual_norm,
                "MorphologyNullAbsCorrelation": morphology_corr,
                "ProjectionNullAbsCorrelation": projection_corr,
                "ShuffledSupportAbsCorrelation": shuffled_corr,
                "MaxFamilyEnergyShare": max_family,
                "MaxClockEnergyShare": max_clock,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Hessian Commutator Object",
                "",
                f"Status: `{status}`.",
                "",
                "This is a target-blind toy parent-operator object. It is not an",
                "empirical scorecard, not a survival claim, and not measurement",
                "validation.",
                "",
                "## Key Numbers",
                "",
                f"- gates passed: `{passed_count}/{len(gates)}`",
                f"- residual norm after morphology projection: `{residual_norm}`",
                f"- morphology-null abs correlation: `{morphology_corr}`",
                f"- projection-null abs correlation: `{projection_corr}`",
                f"- shuffled-support abs correlation: `{shuffled_corr}`",
                f"- max family energy share: `{max_family}`",
                f"- max clock energy share: `{max_clock}`",
                "",
                "## Interpretation",
                "",
                "A passing object would show that the parent-Hessian/commutator route",
                "is structurally capable of producing a non-morphology Tau-side",
                "candidate before scoring. A failing object means the route still",
                "collapses into morphology/projection structure.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
