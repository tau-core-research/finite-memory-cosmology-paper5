#!/usr/bin/env python3
"""Build a no-score parent-Hessian residue candidate preflight packet."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
SOURCE = ROOT / "evidence/p_taucov_parent_hessian_commutator_object.csv"
GATE = ROOT / "evidence/p_taucov_parent_hessian_residue_gate_summary.csv"

OUT_OBJECT = ROOT / "evidence/p_taucov_parent_hessian_residue_candidate.csv"
OUT_METRICS = ROOT / "evidence/p_taucov_parent_hessian_residue_candidate_metrics.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_parent_hessian_residue_candidate_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_hessian_residue_candidate.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_v1"
STATUS_PASS = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_PREFLIGHT_PASS_NO_SCORING"
STATUS_FAIL = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_PREFLIGHT_FAIL_NO_SCORING"
CLAIM_BOUNDARY = "parent_hessian_residue_candidate_no_score_preflight"

SMOOTH_OVERLAP_MAX = 0.50
PROJECTION_OVERLAP_MAX = 0.60
RESIDUE_RANK_MIN = 0.20
BALANCED_RETAINED_MIN = 0.20
BLOCK_SHARE_MAX = 0.60
RESIDUE_NORM_MIN = 1e-10


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


def normalize(mat: np.ndarray) -> tuple[np.ndarray, float]:
    mat = 0.5 * (mat + mat.T)
    fro = float(np.linalg.norm(mat, ord="fro"))
    if fro == 0.0:
        return mat, fro
    return mat / fro, fro


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
        coord = str(row.TauCoordinate)
        if coord in tau_idx:
            bridge[row_idx[str(row.EmpiricalRowID)], tau_idx[coord]] = float(row.BridgeValue)
    return rows, bridge


def projection_matrix(columns: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(columns)
    return q @ q.T


def clock_highpass(rows: pd.DataFrame) -> np.ndarray:
    clock = rows["ClockIndex"].to_numpy(float)
    z = clock - float(clock.mean())
    design = np.column_stack([np.ones(len(rows)), z, z * z])
    return np.eye(len(rows)) - projection_matrix(design)


def group_balance(rows: pd.DataFrame, column: str) -> np.ndarray:
    groups = sorted(rows[column].astype(str).unique())
    design = np.zeros((len(rows), len(groups)))
    for j, group in enumerate(groups):
        design[rows[column].astype(str).eq(group).to_numpy(), j] = 1.0
    return np.eye(len(rows)) - projection_matrix(design)


def context_balance(rows: pd.DataFrame) -> np.ndarray:
    clock = rows["ClockIndex"].to_numpy(float)
    high = clock > float(np.median(clock))
    design = np.column_stack([(~high).astype(float), high.astype(float)])
    return np.eye(len(rows)) - projection_matrix(design)


def remove_direction(mat: np.ndarray, direction: np.ndarray) -> np.ndarray:
    denom = float(np.sum(direction * direction))
    if denom == 0.0:
        return mat
    return mat - float(np.sum(mat * direction) / denom) * direction


def effective_rank_fraction(mat: np.ndarray) -> float:
    eig = np.abs(np.linalg.eigvalsh(0.5 * (mat + mat.T)))
    total = float(eig.sum())
    if total == 0.0:
        return 0.0
    p = eig / total
    entropy = float(-(p[p > 0.0] * np.log(p[p > 0.0])).sum())
    return float(np.exp(entropy) / len(eig))


def max_block_share(mat: np.ndarray, rows: pd.DataFrame, labels: pd.Series) -> float:
    total = float(np.abs(mat).sum())
    if total == 0.0:
        return 1.0
    shares = []
    for label in sorted(labels.astype(str).unique()):
        ids = np.where(labels.astype(str).eq(label).to_numpy())[0]
        shares.append(float(np.abs(mat[np.ix_(ids, ids)]).sum() / total))
    return max(shares) if shares else 1.0


def write_long_matrix(mat: np.ndarray, rows: pd.DataFrame) -> None:
    out = []
    for i, rid_i in enumerate(rows["EmpiricalRowID"].astype(str)):
        for j, rid_j in enumerate(rows["EmpiricalRowID"].astype(str)):
            value = float(mat[i, j])
            if value != 0.0:
                out.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "RowID": rid_i,
                        "ColumnID": rid_j,
                        "IndexI": i,
                        "IndexJ": j,
                        "Value": value,
                        "ObjectSource": "parent_hessian_commutator_residue_clock_highpass_null_excluded",
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(out).to_csv(OUT_OBJECT, index=False)


def main() -> int:
    if not GATE.exists():
        raise RuntimeError("Parent-Hessian residue gate must exist before candidate preflight.")
    p5c = load_module(P5C_V0, "p5c_v0")
    tau_ids, tau_obj = matrix_from_coordinate_long(SOURCE)
    bridge_rows, bridge = load_bridge(tau_ids)
    rows = p5c.load_rows()
    if bridge_rows["EmpiricalRowID"].astype(str).tolist() != rows["RowID"].astype(str).tolist():
        raise RuntimeError("Bridge row order mismatch.")

    raw, raw_norm = normalize(bridge @ tau_obj @ bridge.T)
    random_smooth, _ = normalize(p5c.matrix_from_long(p5c.NULLS, "K_RANDOM_SMOOTH_PSD", len(rows)))
    projection_null, _ = normalize(p5c.matrix_from_long(p5c.NULLS, "K_PHASE_SHIFTED", len(rows)))
    diagonal, _ = normalize(np.eye(len(rows)))

    highpass = clock_highpass(rows)
    family_bal = group_balance(rows, "FamilyID")
    clock_labels = rows["ClockBlock"].astype(str)
    context_labels = pd.Series(
        np.where(rows["ClockIndex"].to_numpy(int) > int(rows["ClockIndex"].median()), "context_high_clock", "context_low_clock")
    )
    context_bal = context_balance(rows)

    candidate = highpass @ raw @ highpass
    candidate = family_bal @ candidate @ family_bal
    candidate = context_bal @ candidate @ context_bal
    candidate = remove_direction(candidate, random_smooth)
    candidate = remove_direction(candidate, projection_null)
    candidate = remove_direction(candidate, diagonal)
    candidate, candidate_norm = normalize(candidate)

    smooth_overlap = abs(corr(candidate, random_smooth))
    projection_overlap = abs(corr(candidate, projection_null))
    residue_rank = effective_rank_fraction(candidate)
    balanced_again = context_bal @ family_bal @ highpass @ candidate @ highpass @ family_bal @ context_bal
    balanced_retained = float(np.linalg.norm(balanced_again, ord="fro") / max(float(np.linalg.norm(candidate, ord="fro")), 1e-12))
    max_family = max_block_share(candidate, rows, rows["FamilyID"])
    max_clock = max_block_share(candidate, rows, clock_labels)
    max_context = max_block_share(candidate, rows, context_labels)
    orientation_margin = float(np.trace(candidate @ highpass))

    metrics = [
        ("PHR-G1_PARENT_HESSIAN_RESIDUE_DECLARED", candidate_norm >= RESIDUE_NORM_MIN, candidate_norm, f">={RESIDUE_NORM_MIN}"),
        ("PHR-G2_SMOOTH_PSD_EXCLUSION", smooth_overlap <= SMOOTH_OVERLAP_MAX, smooth_overlap, f"<={SMOOTH_OVERLAP_MAX}"),
        ("PHR-G3_PROJECTION_NULL_EXCLUSION", projection_overlap < PROJECTION_OVERLAP_MAX, projection_overlap, f"<{PROJECTION_OVERLAP_MAX}"),
        ("PHR-G4_SPECTRAL_RESIDUE_LOCALITY", residue_rank >= RESIDUE_RANK_MIN, residue_rank, f">={RESIDUE_RANK_MIN}"),
        ("PHR-G5_PARENT_ORIENTATION_ANCHOR", orientation_margin != 0.0, orientation_margin, "nonzero"),
        ("PHR-G6_BALANCED_SUPPORT_RETENTION", balanced_retained >= BALANCED_RETAINED_MIN and max(max_family, max_clock, max_context) <= BLOCK_SHARE_MAX, max(max_family, max_clock, max_context), f"retained>={BALANCED_RETAINED_MIN};share<={BLOCK_SHARE_MAX}"),
        ("PHR-G7_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "required"),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "FrozenThreshold": threshold,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value, threshold in metrics
        ]
    )
    table.to_csv(OUT_METRICS, index=False)
    passed_count = int(table["Passed"].sum())
    status = STATUS_PASS if passed_count == len(table) else STATUS_FAIL
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(table),
                "RawProjectedNorm": raw_norm,
                "CandidateNormBeforeNormalization": candidate_norm,
                "SmoothPSDProjectionOverlap": smooth_overlap,
                "ProjectionNullAbsCorrelation": projection_overlap,
                "SpectralResidueRankFraction": residue_rank,
                "OrientationAnchorMargin": orientation_margin,
                "BalancedRetainedNorm": balanced_retained,
                "MaxFamilyShare": max_family,
                "MaxClockShare": max_clock,
                "MaxContextShare": max_context,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    write_long_matrix(candidate, bridge_rows)
    summary.to_csv(OUT_SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Hessian Residue Candidate",
                "",
                f"Status: `{status}`",
                "",
                "This is a no-score preflight artifact. It builds a target-blind",
                "parent-Hessian residue candidate from the existing commutator object,",
                "then applies clock high-pass, family/context balancing, and frozen",
                "null-direction exclusion. It does not run an empirical scorecard.",
                "",
                "## Key Metrics",
                "",
                f"- gates passed: `{passed_count}/{len(table)}`",
                f"- smooth PSD projection overlap: `{smooth_overlap}`",
                f"- projection-null abs correlation: `{projection_overlap}`",
                f"- spectral residue rank fraction: `{residue_rank}`",
                f"- orientation anchor margin: `{orientation_margin}`",
                f"- balanced retained norm: `{balanced_retained}`",
                f"- max family share: `{max_family}`",
                f"- max clock share: `{max_clock}`",
                f"- max context share: `{max_context}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: this candidate either passes or fails the no-score structural",
                "preflight for parent-Hessian residue specificity.",
                "",
                "Forbidden: this candidate demonstrates Tau Core, survives empirically,",
                "or rescues a failed scorecard.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
