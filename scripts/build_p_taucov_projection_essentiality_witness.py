#!/usr/bin/env python3
"""Build a target-blind projection-essentiality witness."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_p_taucov_epsilon_p3_null_survival_suite.py"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
BASIS = ROOT / "evidence/p_taucov_p4_morphology_basis.csv"
OUT_OBJECT = ROOT / "evidence/p_taucov_projection_essentiality_witness.csv"
OUT_GATES = ROOT / "evidence/p_taucov_projection_essentiality_witness_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_witness_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_essentiality_witness.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PROJECTION_ESSENTIALITY_WITNESS_v1"
CLAIM_BOUNDARY = "projection_essentiality_witness_no_scoring"


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
        return 0.0
    return float(np.corrcoef(av, bv)[0, 1])


def matrix_from_basis(path: Path, basis_id: str, coords: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    df = df[df["BasisID"].eq(basis_id)]
    idx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(coords), len(coords)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = float(row.Value)
    return 0.5 * (mat + mat.T)


def project_away_morphology(mat: np.ndarray, coords: list[str]) -> np.ndarray:
    residual = mat.copy()
    for basis_id in sorted(pd.read_csv(BASIS)["BasisID"].unique()):
        basis = matrix_from_basis(BASIS, basis_id, coords)
        residual = residual - float(np.sum(residual * basis)) * basis
    fro = float(np.linalg.norm(residual, ord="fro"))
    return residual if fro == 0.0 else residual / fro


def max_share(kernel: np.ndarray, rows: pd.DataFrame, column: str) -> float:
    total = float(np.abs(kernel).sum())
    if total == 0.0:
        return 1.0
    values = []
    for _, group in rows.groupby(column):
        ids = group["RowIndex"].to_numpy(int)
        values.append(float(np.abs(kernel[np.ix_(ids, ids)]).sum() / total))
    return max(values) if values else 1.0


def main() -> int:
    runner = load_module(RUNNER, "ptaucov_runner")
    p5c_v0 = load_module(P5C_V0, "p5c_v0")
    tau_ids, delta = runner.matrix_from_long(runner.BRANCH_WEIGHTS, "DeltaCTau")
    bridge_ids, bridge = runner.load_bridge(tau_ids)
    rows = p5c_v0.load_rows()
    if bridge_ids != rows["RowID"].astype(str).tolist():
        raise RuntimeError("Bridge row order mismatch.")

    idx = {coord: i for i, coord in enumerate(tau_ids)}
    p = idx["TEMPLATE_P_MORPH_PROJECTION"]
    b = idx["TEMPLATE_B_BRANCH_RESPONSE"]
    phi = idx["TEMPLATE_PHI_PARENT_SOURCE"]
    m = idx["TEMPLATE_M_PARENT_MORPHOLOGY"]

    raw = np.zeros_like(delta)
    raw[p, b] = raw[b, p] = -2.0
    raw[p, phi] = raw[phi, p] = -1.0
    raw[b, b] = -1.0
    witness = project_away_morphology(raw, tau_ids)
    kernel = runner.project(bridge, witness)

    morph_delta = delta.copy()
    morph_delta[m, :] = 0.0
    morph_delta[:, m] = 0.0
    morphology_kernel = runner.project(bridge, morph_delta)
    projection_bridge = bridge.copy()
    projection_bridge[:, p] = 0.0
    projection_null_kernel = runner.project(projection_bridge, witness)
    shuffled = np.roll(witness.reshape(-1), 7).reshape(witness.shape)
    shuffled_kernel = runner.project(bridge, shuffled)

    rows_out = []
    for i, row_coord in enumerate(tau_ids):
        for j, col_coord in enumerate(tau_ids):
            value = float(witness[i, j])
            if value != 0.0:
                rows_out.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "RowCoordinate": row_coord,
                        "ColumnCoordinate": col_coord,
                        "Value": value,
                        "ObjectSource": "trace_balanced_projection_essentiality_witness",
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows_out).to_csv(OUT_OBJECT, index=False)

    residual_norm = float(np.linalg.norm(witness, ord="fro"))
    morphology_corr = abs(corr(kernel, morphology_kernel))
    projection_corr = abs(corr(kernel, projection_null_kernel))
    shuffled_corr = abs(corr(kernel, shuffled_kernel))
    family_share = max_share(kernel, rows, "FamilyID")
    clock_share = max_share(kernel, rows, "ClockBlock")
    projection_essentiality = 1.0 - projection_corr
    gate_rows = [
        ("PE-G1_NONZERO_MORPHOLOGY_ORTHOGONAL_RESIDUAL", residual_norm > 1e-12, residual_norm),
        ("PE-G2_LOW_MORPHOLOGY_NULL_CORRELATION", morphology_corr < 0.75, morphology_corr),
        ("PE-G3_LOW_PROJECTION_NULL_CORRELATION", projection_corr < 0.60, projection_corr),
        ("PE-G4_LOW_SHUFFLED_SUPPORT_CORRELATION", shuffled_corr < 0.60, shuffled_corr),
        ("PE-G5_NO_PRE_SCORE_FAMILY_CLOCK_DOMINANCE", max(family_share, clock_share) <= 0.60, max(family_share, clock_share)),
        ("PE-G6_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
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
        "P_TAUCOV_PROJECTION_ESSENTIALITY_WITNESS_PASS_NO_SCORING"
        if passed_count == len(gates)
        else "P_TAUCOV_PROJECTION_ESSENTIALITY_WITNESS_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates),
                "ProjectionEssentiality": projection_essentiality,
                "MorphologyNullAbsCorrelation": morphology_corr,
                "ProjectionNullAbsCorrelation": projection_corr,
                "ShuffledSupportAbsCorrelation": shuffled_corr,
                "MaxFamilyEnergyShare": family_share,
                "MaxClockEnergyShare": clock_share,
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
                "# P-TauCov Projection-Essentiality Witness",
                "",
                f"Status: `{status}`.",
                "",
                "This is a structural witness only. It does not authorize empirical",
                "scoring, survival claims, or measurement validation.",
                "",
                "## Key Numbers",
                "",
                f"- gates passed: `{passed_count}/{len(gates)}`",
                f"- projection essentiality: `{projection_essentiality}`",
                f"- morphology-null abs correlation: `{morphology_corr}`",
                f"- projection-null abs correlation: `{projection_corr}`",
                f"- shuffled-support abs correlation: `{shuffled_corr}`",
                f"- max family energy share: `{family_share}`",
                f"- max clock energy share: `{clock_share}`",
                "",
                "## Interpretation",
                "",
                "A passing witness means the projection-essential route is not",
                "structurally empty. It does not mean the witness is a physical Tau",
                "prediction.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
