#!/usr/bin/env python3
"""Build and preflight the morphology-orthogonal P4 Tau-specific candidate."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_p_taucov_epsilon_p3_null_survival_suite.py"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
BASIS = ROOT / "evidence/p_taucov_p4_morphology_basis.csv"
OUT_CANDIDATE = ROOT / "evidence/p_taucov_p4_tau_specific_candidate.csv"
OUT_GATES = ROOT / "evidence/p_taucov_p4_tau_specific_candidate_preflight_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_p4_tau_specific_candidate_preflight_summary.csv"
DOC = ROOT / "docs/p_taucov_p4_tau_specific_candidate_preflight.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_P4_TAU_SPECIFIC_CANDIDATE_PREFLIGHT_v1"
CLAIM_BOUNDARY = "target_blind_p4_tau_specific_preflight_no_scoring"


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


def normalized_entropy(values: np.ndarray) -> float:
    weights = np.abs(values).reshape(-1)
    total = float(weights.sum())
    if total == 0.0:
        return 0.0
    probs = weights / total
    probs = probs[probs > 0.0]
    return float(-(probs * np.log(probs)).sum() / np.log(values.size))


def matrix_from_basis(path: Path, basis_id: str, coords: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    df = df[df["BasisID"].eq(basis_id)]
    idx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(coords), len(coords)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = float(row.Value)
    return 0.5 * (mat + mat.T)


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

    basis_ids = sorted(pd.read_csv(BASIS)["BasisID"].unique())
    residual = delta.copy()
    for basis_id in basis_ids:
        b = matrix_from_basis(BASIS, basis_id, tau_ids)
        residual = residual - float(np.sum(residual * b)) * b

    tau_norm_before = float(np.linalg.norm(delta, ord="fro"))
    tau_norm_after = float(np.linalg.norm(residual, ord="fro"))
    if tau_norm_after > 0.0:
        residual_normed = residual / tau_norm_after
    else:
        residual_normed = residual

    tau_index = {cid: i for i, cid in enumerate(tau_ids)}
    m_idx = tau_index["TEMPLATE_M_PARENT_MORPHOLOGY"]
    p_idx = tau_index["TEMPLATE_P_MORPH_PROJECTION"]
    morph_delta = delta.copy()
    morph_delta[m_idx, :] = 0.0
    morph_delta[:, m_idx] = 0.0
    projection_bridge = bridge.copy()
    projection_bridge[:, p_idx] = 0.0

    candidate_kernel = runner.project(bridge, residual_normed)
    p3_kernel = runner.project(bridge, delta)
    morphology_kernel = runner.project(bridge, morph_delta)
    projection_null_kernel = runner.project(projection_bridge, residual_normed)
    shuffled = np.roll(residual_normed.reshape(-1), 7).reshape(residual_normed.shape)
    shuffled_kernel = runner.project(bridge, shuffled)

    rows_out = []
    for i, row_coord in enumerate(tau_ids):
        for j, col_coord in enumerate(tau_ids):
            rows_out.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "RowCoordinate": row_coord,
                    "ColumnCoordinate": col_coord,
                    "DeltaCTauP4Candidate": float(residual_normed[i, j]),
                    "AbsDeltaCTauP4Candidate": abs(float(residual_normed[i, j])),
                    "UsesTargetResiduals": False,
                    "UsesScoreOutcome": False,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(rows_out).to_csv(OUT_CANDIDATE, index=False)

    support_entropy_p3 = normalized_entropy(delta)
    support_entropy_p4 = normalized_entropy(residual_normed)
    max_family_share = family_clock_max_share(candidate_kernel, rows, "FamilyID")
    max_clock_share = family_clock_max_share(candidate_kernel, rows, "ClockBlock")
    morphology_corr = corr(candidate_kernel, morphology_kernel)
    shuffled_corr = abs(corr(candidate_kernel, shuffled_kernel))
    projection_corr = abs(corr(candidate_kernel, projection_null_kernel))
    retained_norm = tau_norm_after / tau_norm_before if tau_norm_before else 0.0

    gate_rows = [
        ("P4-G1_NONZERO_TAU_RESIDUAL", tau_norm_after > 1e-12, retained_norm),
        ("P4-G2_LOW_MORPHOLOGY_NULL_CORRELATION", abs(morphology_corr) < 0.75, abs(morphology_corr)),
        ("P4-G3_SUPPORT_ENTROPY_NOT_NARROWER_THAN_P3", support_entropy_p4 >= support_entropy_p3, support_entropy_p4 - support_entropy_p3),
        ("P4-G4_NO_FAMILY_CLOCK_ENERGY_DOMINANCE", max(max_family_share, max_clock_share) <= 0.60, max(max_family_share, max_clock_share)),
        ("P4-G5_LOW_PROJECTION_AND_SHUFFLED_NULL_CORRELATION", max(projection_corr, shuffled_corr) < 0.60, max(projection_corr, shuffled_corr)),
        ("P4-G6_FROZEN_PREFLIGHT_ONLY", True, 1.0),
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
        "P_TAUCOV_P4_TAU_SPECIFIC_CANDIDATE_PREFLIGHT_PASS_NO_SCORING"
        if passed_count == len(gates)
        else "P_TAUCOV_P4_TAU_SPECIFIC_CANDIDATE_PREFLIGHT_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates),
                "TauNormRetainedAfterMorphologyProjection": retained_norm,
                "SupportEntropyP3": support_entropy_p3,
                "SupportEntropyP4": support_entropy_p4,
                "KernelCorrelationWithP3": corr(candidate_kernel, p3_kernel),
                "KernelCorrelationWithMorphologyNull": morphology_corr,
                "ProjectionNullAbsCorrelation": projection_corr,
                "ShuffledSupportAbsCorrelation": shuffled_corr,
                "MaxFamilyEnergyShare": max_family_share,
                "MaxClockEnergyShare": max_clock_share,
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
                "# P-TauCov P4 Tau-Specific Candidate Preflight",
                "",
                f"Status: `{status}`.",
                "",
                "This is a target-blind morphology-orthogonalization preflight. It",
                "does not run the empirical covariance scorecard and does not authorize",
                "a survival claim.",
                "",
                "## Key Numbers",
                "",
                f"- gates passed: `{passed_count}/{len(gates)}`",
                f"- tau norm retained after morphology projection: `{retained_norm}`",
                f"- support entropy P3: `{support_entropy_p3}`",
                f"- support entropy P4: `{support_entropy_p4}`",
                f"- kernel correlation with P3: `{float(summary.iloc[0]['KernelCorrelationWithP3'])}`",
                f"- kernel correlation with morphology-null: `{morphology_corr}`",
                f"- projection-null abs correlation: `{projection_corr}`",
                f"- shuffled-support abs correlation: `{shuffled_corr}`",
                f"- max family energy share: `{max_family_share}`",
                f"- max clock energy share: `{max_clock_share}`",
                "",
                "## Interpretation",
                "",
                "A passing preflight would authorize only the construction of a scoring",
                "authorization artifact. A failing preflight blocks P4 scoring and means",
                "the Tau-specific residual component is still not clean enough.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
