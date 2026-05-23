#!/usr/bin/env python3
"""Freeze the P5C v3 scoring mode decision using target-blind metrics only."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SIGNED = EVIDENCE / "p5c_bstar_kernel_v3_signed_orientation.csv"
PSD = EVIDENCE / "p5c_bstar_kernel_v3_psd_projection.csv"
NULLS = EVIDENCE / "p5c_bstar_kernel_v3_null_kernels.csv"
SUMMARY = EVIDENCE / "p5c_bstar_kernel_v3_summary.csv"

OUT_CSV = EVIDENCE / "p5c_kernel_v3_scoring_mode_freeze.csv"
OUT_YAML = EVIDENCE / "p5c_kernel_v3_scoring_mode_freeze.yaml"
OUT_DOC = DOCS / "p5c_kernel_v3_scoring_mode_freeze.md"

PROTOCOL_ID = "P5C_BSTAR_COVARIANCE_OPERATOR_KERNEL_PROTOCOL_v1"
AUDIT_ID = "P5C_KERNEL_V3_SCORING_MODE_FREEZE"
KERNEL_ID = "K_BSTAR_P5C_v3_RESIDUAL_COMPLEX_ORIENTATION"
CLAIM_BOUNDARY = "p5c_kernel_v3_scoring_mode_freeze_no_target_score_no_empirical_claim"

THRESHOLDS = {
    "psd_orientation_retention": 0.60,
    "psd_random_smooth_median_abs_corr": 0.60,
    "psd_family_block_energy_share": 0.20,
    "psd_diagonal_energy_share": 0.10,
    "psd_family_gain_capacity": 0.40,
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_from_long(path: Path, kernel_id: str) -> np.ndarray:
    df = pd.read_csv(path)
    df = df[df["KernelID"].eq(kernel_id)]
    n = int(max(df["IndexI"].max(), df["IndexJ"].max())) + 1
    mat = np.zeros((n, n), dtype=float)
    for row in df.itertuples(index=False):
        mat[int(row.IndexI), int(row.IndexJ)] = float(row.Value)
    return 0.5 * (mat + mat.T)


def null_matrix(null_id: str) -> np.ndarray:
    df = pd.read_csv(NULLS)
    df = df[df["KernelID"].eq(null_id)]
    n = int(max(df["IndexI"].max(), df["IndexJ"].max())) + 1
    mat = np.zeros((n, n), dtype=float)
    for row in df.itertuples(index=False):
        mat[int(row.IndexI), int(row.IndexJ)] = float(row.Value)
    return 0.5 * (mat + mat.T)


def rows_from_kernel() -> pd.DataFrame:
    df = pd.read_csv(SIGNED)
    rows = df[["IndexI", "RowI"]].drop_duplicates().sort_values("IndexI").rename(
        columns={"IndexI": "RowIndex", "RowI": "RowID"}
    )
    rows["FamilyID"] = rows["RowID"].str.split("::", regex=False).str[0]
    rows["ClockIndex"] = rows.groupby("FamilyID").cumcount()
    return rows.reset_index(drop=True)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    va = a.reshape(-1) - np.mean(a)
    vb = b.reshape(-1) - np.mean(b)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom <= 1e-12:
        return 0.0
    return float(va @ vb / denom)


def diagonal_energy_share(kernel: np.ndarray) -> float:
    return float(np.sum(np.diag(kernel) ** 2) / max(float(np.sum(kernel * kernel)), 1e-12))


def family_block_energy_share(kernel: np.ndarray, rows: pd.DataFrame) -> float:
    total = float(np.sum(kernel * kernel))
    shares = []
    for _, idx in rows.groupby("FamilyID").groups.items():
        arr = np.array(list(idx), dtype=int)
        block = kernel[np.ix_(arr, arr)]
        shares.append(float(np.sum(block * block) / max(total, 1e-12)))
    return float(max(shares))


def family_gain_capacity(kernel: np.ndarray, rows: pd.DataFrame) -> float:
    positive_total = float(np.sum(np.clip(kernel, 0.0, None) ** 2))
    shares = []
    for _, idx in rows.groupby("FamilyID").groups.items():
        arr = np.array(list(idx), dtype=int)
        block = kernel[np.ix_(arr, arr)]
        shares.append(float(np.sum(np.clip(block, 0.0, None) ** 2) / max(positive_total, 1e-12)))
    return float(max(shares))


def random_smooth_correlations(kernel: np.ndarray) -> list[float]:
    df = pd.read_csv(NULLS)
    out = []
    for null_id in sorted({x for x in df["KernelID"].unique() if x.startswith("K_RANDOM_SMOOTH_PSD_")}):
        out.append(abs(corr(kernel, null_matrix(null_id))))
    return out


def main() -> int:
    signed = matrix_from_long(SIGNED, KERNEL_ID)
    psd = matrix_from_long(PSD, f"{KERNEL_ID}_PSD_PROJECTION")
    rows = rows_from_kernel()
    summary = pd.read_csv(SUMMARY).iloc[0].to_dict()

    psd_random = random_smooth_correlations(psd)
    signed_random = random_smooth_correlations(signed)
    psd_orientation_retention = abs(corr(signed, psd))
    psd_diag = diagonal_energy_share(psd)
    psd_family = family_block_energy_share(psd, rows)
    psd_gain = family_gain_capacity(psd, rows)
    psd_wrong = abs(corr(psd, null_matrix("K_WRONG_CLOCK_PSD")))
    psd_phase = abs(corr(psd, null_matrix("K_PHASE_SHIFTED_PSD")))
    psd_family_perm = abs(corr(psd, null_matrix("K_FAMILY_PERMUTED_PSD")))

    failures = []
    checks = [
        ("psd_orientation_retention", psd_orientation_retention, ">=", THRESHOLDS["psd_orientation_retention"]),
        ("psd_random_smooth_median_abs_corr", float(np.median(psd_random)), "<=", THRESHOLDS["psd_random_smooth_median_abs_corr"]),
        ("psd_family_block_energy_share", psd_family, "<=", THRESHOLDS["psd_family_block_energy_share"]),
        ("psd_diagonal_energy_share", psd_diag, "<=", THRESHOLDS["psd_diagonal_energy_share"]),
        ("psd_family_gain_capacity", psd_gain, "<=", THRESHOLDS["psd_family_gain_capacity"]),
    ]
    for name, value, op, threshold in checks:
        failed = value < threshold if op == ">=" else value > threshold
        if failed:
            failures.append(f"{name}={value:.6g}{op}gate({threshold:.6g}) failed")

    if failures:
        primary_mode = "SCORING_BLOCKED_OPEN_SIGNED_OPERATOR_CONTRAST_PROTOCOL"
        secondary_mode = "NONE"
        status = "PSD_MODE_NOT_REPRESENTATIVE"
        scoring_authorized = False
    else:
        primary_mode = "PSD_COVARIANCE_DEFORMATION"
        secondary_mode = "SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY"
        status = "SCORING_MODE_FREEZE_READY"
        scoring_authorized = False

    record = {
        "ProtocolID": PROTOCOL_ID,
        "AuditID": AUDIT_ID,
        "KernelID": KERNEL_ID,
        "PrimaryScoringMode": primary_mode,
        "SecondaryMode": secondary_mode,
        "Status": status,
        "ScoringAuthorizedByThisArtifact": scoring_authorized,
        "PSDOrientationRetention": psd_orientation_retention,
        "PSDRandomSmoothMedianAbsCorrelation": float(np.median(psd_random)),
        "PSDRandomSmoothMaxAbsCorrelation": float(np.max(psd_random)),
        "PSDDiagonalEnergyShare": psd_diag,
        "PSDMaxFamilyBlockEnergyShare": psd_family,
        "PSDMaxFamilyGainCapacity": psd_gain,
        "PSDWrongClockAbsCorrelation": psd_wrong,
        "PSDPhaseShiftAbsCorrelation": psd_phase,
        "PSDFamilyPermutedAbsCorrelation": psd_family_perm,
        "SignedRandomSmoothMedianAbsCorrelation": float(np.median(signed_random)),
        "SignedWrongClockAbsCorrelation": float(summary["WrongClockAbsCorrelation"]),
        "SignedPhaseShiftAbsCorrelation": float(summary["PhaseShiftAbsCorrelation"]),
        "SignedFamilyPermutedAbsCorrelation": float(summary["FamilyPermutedAbsCorrelation"]),
        "PreScoreFailures": "; ".join(failures),
        "TargetResidualUsed": False,
        "ScoreUsed": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    pd.DataFrame([record]).to_csv(OUT_CSV, index=False)
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "audit_id": AUDIT_ID,
        "kernel_id": KERNEL_ID,
        "primary_scoring_mode": primary_mode,
        "secondary_mode": secondary_mode,
        "status": status,
        "scoring_authorized_by_this_artifact": scoring_authorized,
        "thresholds": THRESHOLDS,
        "metrics": record,
        "signed_kernel_sha256": file_sha256(SIGNED),
        "psd_kernel_sha256": file_sha256(PSD),
        "null_kernels_sha256": file_sha256(NULLS),
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "target_residual_used": False,
        "score_used": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    OUT_YAML.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P5C Kernel v3 Scoring Mode Freeze",
                "",
                f"Status: `{status}`",
                "",
                "This freeze chooses the scoring-mode direction using target-blind structural retention metrics only.",
                "It does not authorize scoring.",
                "",
                "## Decision",
                "",
                f"- primary scoring mode: `{primary_mode}`",
                f"- secondary mode: `{secondary_mode}`",
                "- scoring authorized by this artifact: `false`",
                "",
                "## Metrics",
                "",
                f"- PSD orientation retention: {psd_orientation_retention}",
                f"- PSD random smooth median abs correlation: {float(np.median(psd_random))}",
                f"- PSD random smooth max abs correlation: {float(np.max(psd_random))}",
                f"- PSD diagonal energy share: {psd_diag}",
                f"- PSD max family block energy share: {psd_family}",
                f"- PSD max family gain capacity: {psd_gain}",
                f"- PSD wrong-clock abs correlation: {psd_wrong}",
                f"- PSD phase-shift abs correlation: {psd_phase}",
                f"- PSD family-permuted abs correlation: {psd_family_perm}",
                "",
                "## Boundary",
                "",
                "The signed orientation score may be reported only as a diagnostic under this freeze.",
                "It cannot become a survival claim if the PSD primary score fails.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    print(f"primary={primary_mode}")
    if failures:
        print("; ".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
