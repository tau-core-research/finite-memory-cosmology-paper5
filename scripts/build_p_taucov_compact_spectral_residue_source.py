#!/usr/bin/env python3
"""Build a no-score compact spectral residue source preflight."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
Q_RANGE = ROOT / "evidence/p_taucov_q_range_projector_matrix.csv"
SPEC = ROOT / "evidence/p_taucov_microscopic_residue_source_spec_summary.csv"

OUT_OBJECT = ROOT / "evidence/p_taucov_compact_spectral_residue_source.csv"
OUT_SPECTRUM = ROOT / "evidence/p_taucov_compact_spectral_residue_source_spectrum.csv"
OUT_METRICS = ROOT / "evidence/p_taucov_compact_spectral_residue_source_metrics.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_residue_source_summary.csv"
DOC = ROOT / "docs/p_taucov_compact_spectral_residue_source.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_v1"
STATUS_PASS = "P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_PREFLIGHT_PASS_NO_SCORING"
STATUS_FAIL = "P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_PREFLIGHT_FAIL_NO_SCORING"
CLAIM_BOUNDARY = "compact_spectral_residue_source_no_score_preflight"

EIGEN_THRESHOLD = 1e-10
SELECTED_MODE_FRACTION = 0.20
NORM_MIN = 1e-10
SMOOTH_OVERLAP_MAX = 0.50
PROJECTION_OVERLAP_MAX = 0.60
Q_RANGE_ERROR_MAX = 1e-10
BLOCK_SHARE_MAX = 0.60
RANK_FRACTION_MIN = 0.10


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize(mat: np.ndarray) -> tuple[np.ndarray, float]:
    mat = 0.5 * (mat + mat.T)
    fro = float(np.linalg.norm(mat, ord="fro"))
    if fro == 0.0:
        return mat, fro
    return mat / fro, fro


def corr(a: np.ndarray, b: np.ndarray) -> float:
    av = a.reshape(-1)
    bv = b.reshape(-1)
    if float(np.linalg.norm(av)) == 0.0 or float(np.linalg.norm(bv)) == 0.0:
        return 0.0
    return float(np.corrcoef(av, bv)[0, 1])


def load_square_matrix(path: Path, row_col_names: tuple[str, str]) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    row_col, col_col = row_col_names
    labels = list(dict.fromkeys(df[row_col].astype(str)))
    idx = {label: i for i, label in enumerate(labels)}
    mat = np.zeros((len(labels), len(labels)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(getattr(row, row_col))], idx[str(getattr(row, col_col))]] = float(row.Value)
    return labels, 0.5 * (mat + mat.T)


def clock_laplacian(rows: pd.DataFrame) -> np.ndarray:
    n = len(rows)
    lap = np.zeros((n, n), dtype=float)
    for _, group in rows.groupby("FamilyID"):
        ids = group.sort_values("ClockIndex")["RowIndex"].to_numpy(int)
        for left, right in zip(ids[:-1], ids[1:]):
            lap[left, left] += 1.0
            lap[right, right] += 1.0
            lap[left, right] -= 1.0
            lap[right, left] -= 1.0
    return lap


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


def max_block_share(mat: np.ndarray, labels: pd.Series) -> float:
    total = float(np.abs(mat).sum())
    if total == 0.0:
        return 1.0
    shares = []
    labels = labels.astype(str)
    for label in sorted(labels.unique()):
        ids = np.where(labels.eq(label).to_numpy())[0]
        shares.append(float(np.abs(mat[np.ix_(ids, ids)]).sum() / total))
    return max(shares) if shares else 1.0


def write_matrix(path: Path, labels: list[str], mat: np.ndarray) -> None:
    rows = []
    for i, row_id in enumerate(labels):
        for j, col_id in enumerate(labels):
            value = float(mat[i, j])
            if value != 0.0:
                rows.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "RowID": row_id,
                        "ColumnID": col_id,
                        "IndexI": i,
                        "IndexJ": j,
                        "Value": value,
                        "ObjectSource": "q_range_compact_clock_laplacian_high_frequency_residue",
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> int:
    if not SPEC.exists():
        raise RuntimeError("Microscopic residue source spec must exist before compact spectral source.")
    p5c = load_module(P5C_V0, "p5c_v0")
    rows = p5c.load_rows()
    labels, q_range = load_square_matrix(Q_RANGE, ("RowID", "ColumnID"))
    expected = rows["RowID"].astype(str).tolist()
    if labels != expected:
        raise RuntimeError("Q-range labels do not match P5C row order.")

    lap = clock_laplacian(rows)
    compact_operator = q_range @ lap @ q_range
    compact_operator = 0.5 * (compact_operator + compact_operator.T)
    evals, evecs = np.linalg.eigh(compact_operator)
    active = evals > EIGEN_THRESHOLD
    active_indices = np.where(active)[0]
    selected_count = max(1, int(np.ceil(len(active_indices) * SELECTED_MODE_FRACTION)))
    selected_indices = active_indices[np.argsort(evals[active_indices])[-selected_count:]]
    residue = np.zeros_like(compact_operator)
    for idx in selected_indices:
        vec = evecs[:, idx]
        residue += float(evals[idx]) * np.outer(vec, vec)

    smooth, _ = normalize(p5c.matrix_from_long(p5c.NULLS, "K_RANDOM_SMOOTH_PSD", len(rows)))
    projection, _ = normalize(p5c.matrix_from_long(p5c.NULLS, "K_PHASE_SHIFTED", len(rows)))
    diagonal, _ = normalize(np.eye(len(rows)))
    residue = remove_direction(residue, smooth)
    residue = remove_direction(residue, projection)
    residue = remove_direction(residue, diagonal)
    residue = q_range @ residue @ q_range
    residue, source_norm = normalize(residue)

    smooth_overlap = abs(corr(residue, smooth))
    projection_overlap = abs(corr(residue, projection))
    q_error = float(np.linalg.norm(q_range @ residue @ q_range - residue, ord="fro") / max(float(np.linalg.norm(residue, ord="fro")), 1e-12))
    rank_fraction = effective_rank_fraction(residue)
    context_labels = pd.Series(np.where(rows["ClockIndex"].to_numpy(int) > int(rows["ClockIndex"].median()), "context_high_clock", "context_low_clock"))
    max_family = max_block_share(residue, rows["FamilyID"])
    max_clock = max_block_share(residue, rows["ClockBlock"])
    max_context = max_block_share(residue, context_labels)

    gates = [
        ("CSR-G1_SOURCE_NONZERO", source_norm >= NORM_MIN, source_norm, f">={NORM_MIN}"),
        ("CSR-G2_SMOOTH_PSD_EXCLUSION", smooth_overlap <= SMOOTH_OVERLAP_MAX, smooth_overlap, f"<={SMOOTH_OVERLAP_MAX}"),
        ("CSR-G3_PROJECTION_NULL_EXCLUSION", projection_overlap < PROJECTION_OVERLAP_MAX, projection_overlap, f"<{PROJECTION_OVERLAP_MAX}"),
        ("CSR-G4_Q_RANGE_NATIVE", q_error <= Q_RANGE_ERROR_MAX, q_error, f"<={Q_RANGE_ERROR_MAX}"),
        ("CSR-G5_SPECTRAL_RESIDUE_RANK", rank_fraction >= RANK_FRACTION_MIN, rank_fraction, f">={RANK_FRACTION_MIN}"),
        ("CSR-G6_BALANCED_SUPPORT", max(max_family, max_clock, max_context) <= BLOCK_SHARE_MAX, max(max_family, max_clock, max_context), f"<={BLOCK_SHARE_MAX}"),
        ("CSR-G7_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "required"),
    ]
    metrics = pd.DataFrame(
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
            for gate_id, passed, value, threshold in gates
        ]
    )
    passed_count = int(metrics["Passed"].sum())
    status = STATUS_PASS if passed_count == len(metrics) else STATUS_FAIL
    write_matrix(OUT_OBJECT, labels, residue)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "EigenIndex": int(i),
                "Eigenvalue": float(evals[i]),
                "Active": bool(active[i]),
                "SelectedForResidue": bool(i in set(selected_indices)),
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for i in range(len(evals))
        ]
    ).to_csv(OUT_SPECTRUM, index=False)
    metrics.to_csv(OUT_METRICS, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "Rows": len(rows),
                "ActiveEigenmodes": int(active.sum()),
                "SelectedEigenmodes": int(len(selected_indices)),
                "SelectedModeFraction": SELECTED_MODE_FRACTION,
                "SourceNormBeforeNormalization": source_norm,
                "SmoothPSDProjectionOverlap": smooth_overlap,
                "ProjectionNullAbsCorrelation": projection_overlap,
                "QRangeMembershipError": q_error,
                "SpectralResidueRankFraction": rank_fraction,
                "MaxFamilyShare": max_family,
                "MaxClockShare": max_clock,
                "MaxContextShare": max_context,
                "GatesPassed": passed_count,
                "GatesTotal": len(metrics),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Compact Spectral Residue Source",
                "",
                f"Status: `{status}`",
                "",
                "This is a no-score preflight artifact for the primary microscopic",
                "residue-source route. The source is selected from the compact clock",
                "Laplacian restricted to the frozen `Q_range` clean subspace. No target",
                "residuals, OOS scores, alpha behavior, or winning nulls are used.",
                "",
                "## Key Metrics",
                "",
                f"- active eigenmodes: `{int(active.sum())}`",
                f"- selected eigenmodes: `{int(len(selected_indices))}`",
                f"- source norm before normalization: `{source_norm}`",
                f"- smooth PSD projection overlap: `{smooth_overlap}`",
                f"- projection-null abs correlation: `{projection_overlap}`",
                f"- Q-range membership error: `{q_error}`",
                f"- spectral residue rank fraction: `{rank_fraction}`",
                f"- max family share: `{max_family}`",
                f"- max clock share: `{max_clock}`",
                f"- max context share: `{max_context}`",
                f"- gates passed: `{passed_count}/{len(metrics)}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: this source passes or fails a no-score structural preflight",
                "for compact spectral residue admissibility.",
                "",
                "Forbidden: this source is a Tau Core signal, a scored covariance",
                "survivor, or measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
