#!/usr/bin/env python3
"""Build a minimal Q-native branch-response curvature preflight."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_v1"
CLAIM = "q_native_branch_response_curvature_preflight_no_scoring_no_survival"


def load_embedding() -> tuple[list[str], list[str], np.ndarray, pd.DataFrame]:
    df = pd.read_csv(EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv")
    rows = list(dict.fromkeys(df["EmpiricalRowID"].astype(str)))
    coords = list(dict.fromkeys(df["TauCoordinate"].astype(str)))
    r_idx = {r: i for i, r in enumerate(rows)}
    c_idx = {c: i for i, c in enumerate(coords)}
    mat = np.zeros((len(rows), len(coords)), dtype=float)
    for rec in df.to_dict("records"):
        mat[r_idx[str(rec["EmpiricalRowID"])], c_idx[str(rec["TauCoordinate"])]] = float(rec["EmbeddingValue"])
    meta = df[["EmpiricalRowID", "FamilyID", "ClockIndex"]].drop_duplicates().set_index("EmpiricalRowID").loc[rows]
    return rows, coords, mat, meta


def load_score_matrix(path: Path, matrix_id: str | None = None) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    if matrix_id is not None and "MatrixID" in df.columns:
        df = df[df["MatrixID"].astype(str) == matrix_id]
    row_col = "RowID" if "RowID" in df.columns else "RowCoordinate"
    col_col = "ColumnID" if "ColumnID" in df.columns else "ColumnCoordinate"
    rows = list(dict.fromkeys(df[row_col].astype(str)))
    cols = list(dict.fromkeys(df[col_col].astype(str)))
    labels = rows if rows == cols else sorted(set(rows) | set(cols))
    idx = {label: i for i, label in enumerate(labels)}
    mat = np.zeros((len(labels), len(labels)), dtype=float)
    for rec in df.to_dict("records"):
        mat[idx[str(rec[row_col])], idx[str(rec[col_col])] ] = float(rec["Value"])
    return labels, mat


def align(labels: list[str], mat: np.ndarray, target: list[str]) -> np.ndarray:
    idx = {label: i for i, label in enumerate(labels)}
    out = np.zeros((len(target), len(target)), dtype=float)
    for i, row in enumerate(target):
        for j, col in enumerate(target):
            out[i, j] = mat[idx[row], idx[col]]
    return out


def frob(x: np.ndarray) -> float:
    return float(np.linalg.norm(x, ord="fro"))


def family_energy_share(mat: np.ndarray, families: list[str]) -> float:
    total = float(np.sum(mat * mat))
    if total == 0.0:
        return 0.0
    shares = []
    for fam in sorted(set(families)):
        idx = [i for i, f in enumerate(families) if f == fam]
        block = mat[np.ix_(idx, idx)]
        shares.append(float(np.sum(block * block)) / total)
    return max(shares) if shares else 0.0


def diagonal_share(mat: np.ndarray) -> float:
    total = float(np.sum(mat * mat))
    if total == 0.0:
        return 0.0
    return float(np.sum(np.diag(mat) ** 2) / total)


def main() -> int:
    rows, coords, emb, meta = load_embedding()
    q_labels, q_raw = load_score_matrix(EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv", "PIBAL_PIPERP_PIBAL")
    p_labels, piperp_raw = load_score_matrix(EVIDENCE / "p_taucov_tccs_piperp_matrix.csv")
    q_clean = align(q_labels, q_raw, rows)
    piperp = align(p_labels, piperp_raw, rows)
    ident = np.eye(len(rows))

    coord_index = {c: i for i, c in enumerate(coords)}
    b = emb[:, coord_index["TEMPLATE_B_BRANCH_RESPONSE"]]
    phi = emb[:, coord_index["TEMPLATE_PHI_PARENT_SOURCE"]]
    v_branch = b - phi
    v_clean = q_clean @ v_branch
    raw_norm = float(np.linalg.norm(v_branch))
    clean_norm = float(np.linalg.norm(v_clean))
    support = clean_norm / raw_norm if raw_norm > 0.0 else 0.0

    k_raw = np.outer(v_branch, v_branch)
    k_q = np.outer(v_clean, v_clean)
    k_norm = frob(k_q)
    q_closure = frob(q_clean @ k_q @ q_clean - k_q) / k_norm if k_norm > 0.0 else 0.0
    projection_leakage = frob((ident - piperp) @ k_q) / k_norm if k_norm > 0.0 else 0.0
    families = meta["FamilyID"].astype(str).tolist()
    fam_share = family_energy_share(k_q, families)
    diag_share = diagonal_share(k_q)

    gates = [
        ("BRQ-G1_SOURCE_DECLARED", True, "B_BRANCH_RESPONSE_MINUS_PHI_PARENT_SOURCE", "declared"),
        ("BRQ-G2_NONZERO_SOURCE", raw_norm > 1e-12, raw_norm, ">1e-12"),
        ("BRQ-G3_Q_SUPPORT", support >= 0.20, support, ">=0.20"),
        ("BRQ-G4_Q_NATIVE_CLOSURE", q_closure <= 1e-10, q_closure, "<=1e-10"),
        ("BRQ-G5_PROJECTION_LEAKAGE", projection_leakage <= 0.10, projection_leakage, "<=0.10"),
        ("BRQ-G6_FAMILY_SHARE", fam_share <= 0.50, fam_share, "<=0.50"),
        ("BRQ-G7_DIAGONAL_SHARE", diag_share <= 0.10, diag_share, "<=0.10"),
        ("BRQ-G8_NO_SCORING", True, "no_target_residuals_no_score_outcomes", "required"),
    ]
    passed = sum(bool(g[1]) for g in gates)
    status = (
        "P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_PASS_NO_SCORING"
        if passed == len(gates)
        else "P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_FAIL_NO_SCORING"
    )

    EVIDENCE.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "SourceVector": "TEMPLATE_B_BRANCH_RESPONSE_MINUS_TEMPLATE_PHI_PARENT_SOURCE",
                "RawVectorNorm": raw_norm,
                "CleanVectorNorm": clean_norm,
                "SupportRetention": support,
                "QNativeClosureError": q_closure,
                "ProjectionLeakage": projection_leakage,
                "MaxFamilyEnergyShare": fam_share,
                "DiagonalEnergyShare": diag_share,
                "PassedGates": passed,
                "TotalGates": len(gates),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(ok),
                "Observed": observed,
                "Threshold": threshold,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for gate_id, ok, observed, threshold in gates
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_gates.csv", index=False)
    with (EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_matrix.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ProtocolID", "FreezeID", "RowID", "ColumnID", "Value", "ScoringAuthorized", "ClaimBoundary"])
        for i, row in enumerate(rows):
            for j, col in enumerate(rows):
                writer.writerow([PROTOCOL_ID, FREEZE_ID, row, col, k_q[i, j], False, CLAIM])
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "RowID": row,
                "RawBranchContrast": v_branch[i],
                "QCleanBranchResponse": v_clean[i],
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for i, row in enumerate(rows)
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_vector.csv", index=False)

    (DOCS / "p_taucov_q_native_branch_response_curvature_preflight.md").write_text(
        f"""# P-TauCov Q-Native Branch-Response Curvature Preflight

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This preflight tests the minimal target-blind Q-native branch-response
curvature candidate:

```text
v_branch = E[:, TEMPLATE_B_BRANCH_RESPONSE] - E[:, TEMPLATE_PHI_PARENT_SOURCE]
J_response = Q_clean v_branch
K_Q = J_response J_response^T
```

It does not inspect target residual scores and does not authorize empirical
scoring.

## Metrics

| Quantity | Value |
|---|---:|
| raw vector norm | `{raw_norm}` |
| clean vector norm | `{clean_norm}` |
| support retention | `{support}` |
| Q-native closure error | `{q_closure}` |
| projection leakage | `{projection_leakage}` |
| max family energy share | `{fam_share}` |
| diagonal energy share | `{diag_share}` |
| passed gates | `{passed} / {len(gates)}` |

## Interpretation

This is a construction preflight only. If it passes, the candidate may be
considered for a future scoring manifest. If it fails, the minimal
branch-response contrast is not enough and a richer reduced-branch Jacobian is
needed.

## Claim Boundary

Allowed statement:

> A minimal Q-native branch-response curvature candidate has been inspected at pre-score level.

Forbidden statement:

> The branch-response curvature candidate validates Tau Core, authorizes scoring, or establishes empirical survival.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
