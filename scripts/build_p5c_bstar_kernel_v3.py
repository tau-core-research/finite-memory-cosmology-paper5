#!/usr/bin/env python3
"""Build P5C Bstar kernel v3: residual-complex orientation pre-score artifact.

v3 is deliberately pre-score only. It does not tune smoothing, family balance,
sector thresholds, or PSD projection against target outcomes. Instead it
freezes a complex family-clock orientation rule motivated by the parent
B-Hessian residual complex:

    u_i = sector_weight(i) * branch_sign(f) * exp(i theta_k) * exp(i omega_f)
    K_signed(i,j) = Re(conj(u_i) H_parent(sector_i, sector_j) u_j)

The signed orientation kernel and its PSD covariance projection are written as
separate artifacts. Scoring is not authorized by this script.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
ROW_SOURCE = (
    ROOT
    / "data/physical_nulls/backreaction_reproduction/"
    "registered_protocol_guided_reproduction_backreaction_vector.csv"
)
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_SIGNED = EVIDENCE / "p5c_bstar_kernel_v3_signed_orientation.csv"
OUT_PSD = EVIDENCE / "p5c_bstar_kernel_v3_psd_projection.csv"
OUT_NULLS = EVIDENCE / "p5c_bstar_kernel_v3_null_kernels.csv"
OUT_SUMMARY = EVIDENCE / "p5c_bstar_kernel_v3_summary.csv"
OUT_MANIFEST = EVIDENCE / "p5c_bstar_kernel_v3_manifest.yaml"
OUT_SHA = EVIDENCE / "p5c_bstar_kernel_v3.sha256"
OUT_DOC = DOCS / "p5c_bstar_kernel_v3.md"

PROTOCOL_ID = "P5C_BSTAR_COVARIANCE_OPERATOR_KERNEL_PROTOCOL_v1"
KERNEL_ID = "K_BSTAR_P5C_v3_RESIDUAL_COMPLEX_ORIENTATION"
CLAIM_BOUNDARY = "p5c_kernel_v3_prescore_orientation_artifact_no_scoring_authorization"

FORBIDDEN_COLUMNS = {
    "target_y",
    "target",
    "residual_y",
    "residual",
    "poly_deg2_prediction",
    "poly_deg2_residual",
    "k2_prediction",
    "k2_residual",
    "chi2",
    "chi2_contribution",
    "winner_label",
    "score",
    "fit_rank",
}

CONFIG = {
    "sector_rule": "clock_index_0_3_protected_4_7_active_8_11_null",
    "family_phase_rule": "omega_f_2pi_f_over_3_sorted_family_order",
    "clock_phase_rule": "theta_k_2pi_k_over_12",
    "branch_signs": {
        "REGISTERED_HD_CRITERIA_1_SIMPLE_PROXY": 1.0,
        "REGISTERED_HD_CRITERIA_2_LOW_LOSS_PROXY": -1.0,
        "REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY": 1.0,
    },
    "sector_weights": {
        "protected": 1.0,
        "active": 0.85,
        "null": 0.20,
    },
    "h_parent_real": [
        [1.00, -0.55, 0.00],
        [-0.55, 0.35, -0.25],
        [0.00, -0.25, 0.05],
    ],
    "h_parent_imag": [
        [0.00, 0.45, -0.20],
        [-0.45, 0.00, 0.35],
        [0.20, -0.35, 0.00],
    ],
    "signed_preprocess": {
        "symmetrize": True,
        "remove_diagonal": True,
        "remove_identity_component": True,
        "remove_family_dummy_components": True,
        "normalize": "frobenius_unit_norm",
    },
    "psd_projection": "positive_spectral_part_then_frobenius_unit_norm",
    "random_smooth_null_count": 64,
    "pre_score_thresholds": {
        "wrong_clock_abs_corr": 0.50,
        "phase_shift_abs_corr": 0.50,
        "family_permuted_abs_corr": 0.50,
        "random_smooth_psd_median_abs_corr": 0.60,
        "diagonal_energy_share": 0.10,
        "max_family_block_energy_share": 0.20,
        "max_family_gain_capacity": 0.40,
    },
}

SECTOR_ORDER = ["protected", "active", "null"]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_row_source(df: pd.DataFrame) -> None:
    forbidden = FORBIDDEN_COLUMNS.intersection(df.columns)
    if forbidden:
        raise ValueError(f"Forbidden target/scoring leakage columns present: {sorted(forbidden)}")
    required = {"FamilyID", "SampleID", "z"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required row metadata columns: {sorted(missing)}")


def canonical_rows() -> pd.DataFrame:
    rows = pd.read_csv(ROW_SOURCE)
    validate_row_source(rows)
    rows = rows.sort_values(["FamilyID", "z", "SampleID"]).reset_index(drop=True)
    rows["RowIndex"] = np.arange(len(rows))
    rows["ClockIndex"] = rows.groupby("FamilyID").cumcount()
    rows["ClockBlock"] = rows["ClockIndex"].map(
        lambda idx: "clock_block_0" if idx < 4 else ("clock_block_1" if idx < 8 else "clock_block_2")
    )
    rows["Sector"] = rows["ClockIndex"].map(
        lambda idx: "protected" if idx < 4 else ("active" if idx < 8 else "null")
    )
    rows["RowID"] = [
        f"{family_id}::z_{z:.6g}" for family_id, z in zip(rows["FamilyID"], rows["z"])
    ]
    families = sorted(rows["FamilyID"].unique())
    family_phase = {family_id: 2.0 * np.pi * idx / len(families) for idx, family_id in enumerate(families)}
    rows["FamilyPhase"] = rows["FamilyID"].map(family_phase).astype(float)
    rows["ClockPhase"] = 2.0 * np.pi * rows["ClockIndex"].to_numpy(float) / 12.0
    rows["BranchSign"] = rows["FamilyID"].map(CONFIG["branch_signs"]).astype(float)
    rows["SectorWeight"] = rows["Sector"].map(CONFIG["sector_weights"]).astype(float)
    rows["SectorIndex"] = rows["Sector"].map({name: idx for idx, name in enumerate(SECTOR_ORDER)}).astype(int)
    if rows[["BranchSign", "SectorWeight", "SectorIndex"]].isna().any().any():
        raise ValueError("Missing frozen branch sign, sector weight, or sector index.")
    return rows


def h_parent() -> np.ndarray:
    real = np.asarray(CONFIG["h_parent_real"], dtype=float)
    imag = np.asarray(CONFIG["h_parent_imag"], dtype=float)
    h = real + 1j * imag
    herm = 0.5 * (h + h.conj().T)
    return herm


def build_complex_embedding(rows: pd.DataFrame) -> np.ndarray:
    phase = rows["ClockPhase"].to_numpy(float) + rows["FamilyPhase"].to_numpy(float)
    amp = rows["SectorWeight"].to_numpy(float) * rows["BranchSign"].to_numpy(float)
    return amp * np.exp(1j * phase)


def remove_identity_component(kernel: np.ndarray) -> np.ndarray:
    ident = np.eye(kernel.shape[0])
    coeff = float(np.sum(kernel * ident) / np.sum(ident * ident))
    return kernel - coeff * ident


def remove_family_dummy_components(kernel: np.ndarray, rows: pd.DataFrame) -> np.ndarray:
    out = kernel.copy()
    for _, idx in rows.groupby("FamilyID").groups.items():
        arr = np.array(list(idx), dtype=int)
        dummy = np.zeros_like(out)
        dummy[np.ix_(arr, arr)] = 1.0
        coeff = float(np.sum(out * dummy) / max(float(np.sum(dummy * dummy)), 1e-12))
        out -= coeff * dummy
    return out


def normalize_fro(kernel: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(kernel, "fro"))
    if norm <= 1e-12:
        raise ValueError("Kernel collapsed before normalization.")
    return kernel / norm


def preprocess_signed(kernel: np.ndarray, rows: pd.DataFrame) -> np.ndarray:
    out = 0.5 * (kernel + kernel.T)
    if CONFIG["signed_preprocess"]["remove_diagonal"]:
        out = out.copy()
        np.fill_diagonal(out, 0.0)
    if CONFIG["signed_preprocess"]["remove_identity_component"]:
        out = remove_identity_component(out)
    if CONFIG["signed_preprocess"]["remove_family_dummy_components"]:
        out = remove_family_dummy_components(out, rows)
    if CONFIG["signed_preprocess"]["remove_diagonal"]:
        np.fill_diagonal(out, 0.0)
    return normalize_fro(out)


def build_signed_kernel(rows: pd.DataFrame) -> np.ndarray:
    u = build_complex_embedding(rows)
    h = h_parent()
    sector = rows["SectorIndex"].to_numpy(int)
    n = len(rows)
    kernel = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            value = np.conjugate(u[i]) * h[sector[i], sector[j]] * u[j]
            kernel[i, j] = float(np.real(value))
    return preprocess_signed(kernel, rows)


def psd_projection(kernel: np.ndarray) -> tuple[np.ndarray, float, float]:
    sym = 0.5 * (kernel + kernel.T)
    eigvals, eigvecs = np.linalg.eigh(sym)
    min_eig = float(np.min(eigvals))
    positive = np.clip(eigvals, 0.0, None)
    positive_energy = float(np.sum(positive * positive))
    total_energy = float(np.sum(eigvals * eigvals))
    retained = positive_energy / max(total_energy, 1e-12)
    repaired = (eigvecs * positive) @ eigvecs.T
    return normalize_fro(repaired), min_eig, retained


def permuted(kernel: np.ndarray, perm: np.ndarray) -> np.ndarray:
    return kernel[np.ix_(perm, perm)]


def build_permutation(rows: pd.DataFrame, mode: str) -> np.ndarray:
    n = len(rows)
    perm = np.arange(n)
    if mode == "wrong_clock":
        for _, idx in rows.groupby("FamilyID").groups.items():
            arr = np.array(list(idx), dtype=int)
            perm[arr] = arr[::-1]
    elif mode == "phase_shift":
        for _, idx in rows.groupby("FamilyID").groups.items():
            arr = np.array(list(idx), dtype=int)
            perm[arr] = np.roll(arr, 3)
    elif mode == "family_permuted":
        families = sorted(rows["FamilyID"].unique())
        rotated = {families[i]: families[(i + 1) % len(families)] for i in range(len(families))}
        for family_id, source_family in rotated.items():
            target = rows.index[rows["FamilyID"].eq(family_id)].to_numpy()
            source = rows.index[rows["FamilyID"].eq(source_family)].to_numpy()
            perm[target] = source
    else:
        raise ValueError(f"Unknown permutation mode: {mode}")
    return perm


def center_by_group(features: np.ndarray, labels: pd.Series) -> np.ndarray:
    out = features.copy()
    for _, idx in labels.groupby(labels).groups.items():
        arr = np.array(list(idx), dtype=int)
        out[arr] -= np.mean(out[arr], axis=0, keepdims=True)
    return out


def random_smooth_psd_nulls(rows: pd.DataFrame) -> list[np.ndarray]:
    rng = np.random.default_rng(20260523)
    clock = rows["ClockIndex"].to_numpy(float) / 11.0
    family_codes = rows["FamilyID"].astype("category").cat.codes.to_numpy(float)
    nulls: list[np.ndarray] = []
    for _ in range(int(CONFIG["random_smooth_null_count"])):
        phases = rng.uniform(0.0, 2.0 * np.pi, size=4)
        coeffs = rng.normal(size=8)
        cols = [
            np.sin(2.0 * np.pi * clock + phases[0]),
            np.cos(2.0 * np.pi * clock + phases[1]),
            np.sin(4.0 * np.pi * clock + phases[2]),
            np.cos(4.0 * np.pi * clock + phases[3]),
            clock,
            clock * clock,
            family_codes - family_codes.mean(),
            rng.normal(size=len(rows)) * 0.15,
        ]
        features = np.column_stack([coeff * col for coeff, col in zip(coeffs, cols)])
        features = center_by_group(features, rows["FamilyID"])
        kernel = features @ features.T
        psd, _, _ = psd_projection(kernel)
        nulls.append(psd)
    return nulls


def matrix_correlation(a: np.ndarray, b: np.ndarray) -> float:
    va = a.reshape(-1)
    vb = b.reshape(-1)
    va = va - np.mean(va)
    vb = vb - np.mean(vb)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom <= 1e-12:
        return 0.0
    return float((va @ vb) / denom)


def family_block_energy_share(kernel: np.ndarray, rows: pd.DataFrame) -> float:
    total_energy = float(np.sum(kernel * kernel))
    shares = []
    for _, idx in rows.groupby("FamilyID").groups.items():
        arr = np.array(list(idx), dtype=int)
        block = kernel[np.ix_(arr, arr)]
        shares.append(float(np.sum(block * block) / max(total_energy, 1e-12)))
    return float(max(shares))


def family_gain_capacity(kernel: np.ndarray, rows: pd.DataFrame) -> float:
    positive_total = float(np.sum(np.clip(kernel, 0.0, None) ** 2))
    capacities = []
    for _, idx in rows.groupby("FamilyID").groups.items():
        arr = np.array(list(idx), dtype=int)
        block = kernel[np.ix_(arr, arr)]
        capacities.append(float(np.sum(np.clip(block, 0.0, None) ** 2) / max(positive_total, 1e-12)))
    return float(max(capacities))


def diagonal_energy_share(kernel: np.ndarray) -> float:
    return float(np.sum(np.diag(kernel) ** 2) / max(float(np.sum(kernel * kernel)), 1e-12))


def build_nulls(signed: np.ndarray, psd: np.ndarray, rows: pd.DataFrame) -> dict[str, np.ndarray]:
    nulls = {
        "K_WRONG_CLOCK_SIGNED": permuted(signed, build_permutation(rows, "wrong_clock")),
        "K_PHASE_SHIFTED_SIGNED": permuted(signed, build_permutation(rows, "phase_shift")),
        "K_FAMILY_PERMUTED_SIGNED": permuted(signed, build_permutation(rows, "family_permuted")),
        "K_WRONG_CLOCK_PSD": permuted(psd, build_permutation(rows, "wrong_clock")),
        "K_PHASE_SHIFTED_PSD": permuted(psd, build_permutation(rows, "phase_shift")),
        "K_FAMILY_PERMUTED_PSD": permuted(psd, build_permutation(rows, "family_permuted")),
    }
    for idx, mat in enumerate(random_smooth_psd_nulls(rows)):
        nulls[f"K_RANDOM_SMOOTH_PSD_{idx:02d}"] = mat
    return nulls


def diagnostics(signed: np.ndarray, psd: np.ndarray, rows: pd.DataFrame, nulls: dict[str, np.ndarray]) -> dict[str, float | str | bool]:
    thresholds = CONFIG["pre_score_thresholds"]
    random_corrs = [
        abs(matrix_correlation(signed, mat))
        for name, mat in nulls.items()
        if name.startswith("K_RANDOM_SMOOTH_PSD_")
    ]
    wrong_corr = abs(matrix_correlation(signed, nulls["K_WRONG_CLOCK_SIGNED"]))
    phase_corr = abs(matrix_correlation(signed, nulls["K_PHASE_SHIFTED_SIGNED"]))
    family_corr = abs(matrix_correlation(signed, nulls["K_FAMILY_PERMUTED_SIGNED"]))
    diag_share = diagonal_energy_share(signed)
    max_family = family_block_energy_share(signed, rows)
    max_gain_capacity = family_gain_capacity(signed, rows)
    status = "FREEZE_READY"
    failures = []
    checks = [
        ("wrong_clock_abs_corr", wrong_corr, thresholds["wrong_clock_abs_corr"]),
        ("phase_shift_abs_corr", phase_corr, thresholds["phase_shift_abs_corr"]),
        ("family_permuted_abs_corr", family_corr, thresholds["family_permuted_abs_corr"]),
        ("random_smooth_psd_median_abs_corr", float(np.median(random_corrs)), thresholds["random_smooth_psd_median_abs_corr"]),
        ("diagonal_energy_share", diag_share, thresholds["diagonal_energy_share"]),
        ("max_family_block_energy_share", max_family, thresholds["max_family_block_energy_share"]),
        ("max_family_gain_capacity", max_gain_capacity, thresholds["max_family_gain_capacity"]),
    ]
    for name, value, threshold in checks:
        if value > threshold:
            failures.append(f"{name}={value:.6g}>{threshold:.6g}")
    if failures:
        status = "K_BSTAR_P5C_v3_NOT_SCOREABLE"

    eig_signed = np.linalg.eigvalsh(0.5 * (signed + signed.T))
    eig_psd = np.linalg.eigvalsh(0.5 * (psd + psd.T))
    return {
        "ProtocolID": PROTOCOL_ID,
        "KernelID": KERNEL_ID,
        "Rows": int(len(rows)),
        "Families": int(rows["FamilyID"].nunique()),
        "ClockPositions": int(rows["z"].nunique()),
        "SignedMinEigenvalue": float(np.min(eig_signed)),
        "SignedMaxEigenvalue": float(np.max(eig_signed)),
        "PSDMinEigenvalue": float(np.min(eig_psd)),
        "PSDMaxEigenvalue": float(np.max(eig_psd)),
        "SignedFrobeniusNorm": float(np.linalg.norm(signed, "fro")),
        "PSDFrobeniusNorm": float(np.linalg.norm(psd, "fro")),
        "WrongClockAbsCorrelation": wrong_corr,
        "PhaseShiftAbsCorrelation": phase_corr,
        "FamilyPermutedAbsCorrelation": family_corr,
        "RandomSmoothPSDMedianAbsCorrelation": float(np.median(random_corrs)),
        "RandomSmoothPSDMaxAbsCorrelation": float(np.max(random_corrs)),
        "DiagonalEnergyShare": diag_share,
        "MaxFamilyBlockEnergyShare": max_family,
        "MaxFamilyGainCapacity": max_gain_capacity,
        "PreScoreFailures": "; ".join(failures),
        "PreScoreStatus": status,
        "ScoringAuthorized": False,
        "TargetResidualUsed": False,
        "ScoreUsed": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    }


def write_matrix_csv(path: Path, matrix: np.ndarray, rows: pd.DataFrame, kernel_id: str, artifact_kind: str) -> None:
    records = []
    row_ids = rows["RowID"].tolist()
    for i, row_i in enumerate(row_ids):
        for j, row_j in enumerate(row_ids):
            records.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "KernelID": kernel_id,
                    "ArtifactKind": artifact_kind,
                    "RowI": row_i,
                    "RowJ": row_j,
                    "IndexI": i,
                    "IndexJ": j,
                    "Value": float(matrix[i, j]),
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(records).to_csv(path, index=False)


def write_nulls(path: Path, nulls: dict[str, np.ndarray], rows: pd.DataFrame) -> None:
    records = []
    row_ids = rows["RowID"].tolist()
    for null_id, mat in nulls.items():
        for i, row_i in enumerate(row_ids):
            for j, row_j in enumerate(row_ids):
                records.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "KernelID": null_id,
                        "RowI": row_i,
                        "RowJ": row_j,
                        "IndexI": i,
                        "IndexJ": j,
                        "Value": float(mat[i, j]),
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(records).to_csv(path, index=False)


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    rows = canonical_rows()
    signed = build_signed_kernel(rows)
    psd, psd_min_before, psd_retained = psd_projection(signed)
    nulls = build_nulls(signed, psd, rows)
    diag = diagnostics(signed, psd, rows, nulls)
    diag["PSDMinEigenvalueBeforeProjection"] = psd_min_before
    diag["PSDPositiveSpectralEnergyRetained"] = psd_retained

    write_matrix_csv(OUT_SIGNED, signed, rows, KERNEL_ID, "signed_orientation")
    write_matrix_csv(OUT_PSD, psd, rows, f"{KERNEL_ID}_PSD_PROJECTION", "psd_projection")
    write_nulls(OUT_NULLS, nulls, rows)
    pd.DataFrame([diag]).to_csv(OUT_SUMMARY, index=False)

    sha_signed = file_sha256(OUT_SIGNED)
    sha_psd = file_sha256(OUT_PSD)
    sha_nulls = file_sha256(OUT_NULLS)
    OUT_SHA.write_text(
        "\n".join(
            [
                f"{sha_signed}  {OUT_SIGNED.name}",
                f"{sha_psd}  {OUT_PSD.name}",
                f"{sha_nulls}  {OUT_NULLS.name}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    manifest = {
        "protocol_id": PROTOCOL_ID,
        "kernel_id": KERNEL_ID,
        "signed_orientation_sha256": sha_signed,
        "psd_projection_sha256": sha_psd,
        "null_kernels_sha256": sha_nulls,
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "config": CONFIG,
        "pre_score_status": diag["PreScoreStatus"],
        "scoring_authorized_by_this_artifact": False,
        "target_residual_used": False,
        "score_used": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    OUT_MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    OUT_DOC.write_text(
        "\n".join(
            [
                "# P5C Bstar Kernel v3",
                "",
                f"Status: `{diag['PreScoreStatus']}`",
                "",
                "v3 is a residual-complex orientation pre-score artifact.",
                "It stores a signed orientation kernel separately from its PSD covariance projection.",
                "This document does not authorize scoring.",
                "",
                "## Diagnostics",
                "",
                f"- rows: {diag['Rows']}",
                f"- families: {diag['Families']}",
                f"- clock positions: {diag['ClockPositions']}",
                f"- wrong-clock abs correlation: {diag['WrongClockAbsCorrelation']}",
                f"- phase-shift abs correlation: {diag['PhaseShiftAbsCorrelation']}",
                f"- family-permuted abs correlation: {diag['FamilyPermutedAbsCorrelation']}",
                f"- random smooth PSD median abs correlation: {diag['RandomSmoothPSDMedianAbsCorrelation']}",
                f"- random smooth PSD max abs correlation: {diag['RandomSmoothPSDMaxAbsCorrelation']}",
                f"- diagonal energy share: {diag['DiagonalEnergyShare']}",
                f"- max family block energy share: {diag['MaxFamilyBlockEnergyShare']}",
                f"- max family gain capacity: {diag['MaxFamilyGainCapacity']}",
                f"- PSD positive spectral energy retained: {diag['PSDPositiveSpectralEnergyRetained']}",
                f"- signed orientation sha256: `{sha_signed}`",
                f"- PSD projection sha256: `{sha_psd}`",
                "",
                "## Scoring Boundary",
                "",
                "`SCORING_AUTHORIZED=false`.",
                "",
                "If the pre-score gate fails, this candidate is not scoreable and must not be used",
                "as a post-hoc replacement for v2.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"wrote {OUT_SIGNED.relative_to(ROOT)}")
    print(f"wrote {OUT_PSD.relative_to(ROOT)}")
    print(f"wrote {OUT_NULLS.relative_to(ROOT)}")
    print(f"wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"wrote {OUT_MANIFEST.relative_to(ROOT)}")
    print(diag["PreScoreStatus"])
    if diag["PreScoreFailures"]:
        print(diag["PreScoreFailures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
