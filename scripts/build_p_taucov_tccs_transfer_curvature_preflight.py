#!/usr/bin/env python3
"""Build the TCCS transfer-curvature pre-score object."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

EMBEDDING = EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv"
PMORPH = EVIDENCE / "p_taucov_tccs_pmorph_parent_operator.csv"
PIPERP = EVIDENCE / "p_taucov_tccs_piperp_matrix.csv"
PIBAL = EVIDENCE / "p_taucov_clock_family_balance_projector_matrix.csv"
HESSIAN = EVIDENCE / "p_taucov_projection_essentiality_parent_action_hessian.csv"

OUT_TRANSFER = EVIDENCE / "p_taucov_tccs_transfer_preflight_matrix.csv"
OUT_CURV = EVIDENCE / "p_taucov_tccs_transfer_curvature_preflight_matrix.csv"
OUT_GATES = EVIDENCE / "p_taucov_tccs_transfer_curvature_preflight_gates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_transfer_curvature_preflight_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_transfer_curvature_preflight.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_v1"
CLAIM_BOUNDARY = "tccs_transfer_curvature_preflight_no_scoring_no_survival"


def dense_from_sparse(path: Path, ids: list[str], row_col_name: tuple[str, str] = ("RowID", "ColumnID"), value_col: str = "Value") -> np.ndarray:
    df = pd.read_csv(path)
    index = {x: i for i, x in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for _, row in df.iterrows():
        r = str(row[row_col_name[0]])
        c = str(row[row_col_name[1]])
        if r in index and c in index:
            mat[index[r], index[c]] = float(row[value_col])
    return mat


def matrix_records(matrix: np.ndarray, ids: list[str]) -> list[dict]:
    rows = []
    for i, row_id in enumerate(ids):
        for j, col_id in enumerate(ids):
            value = float(matrix[i, j])
            if abs(value) > 1e-14:
                rows.append({"RowID": row_id, "ColumnID": col_id, "Value": value})
    return rows


def main() -> int:
    for path in [EMBEDDING, PMORPH, PIPERP, PIBAL, HESSIAN]:
        if not path.exists():
            raise FileNotFoundError(f"Missing input: {path.relative_to(ROOT)}")

    emb_df = pd.read_csv(EMBEDDING)
    row_ids = list(dict.fromkeys(emb_df["EmpiricalRowID"].astype(str).tolist()))
    coord_ids = list(dict.fromkeys(emb_df["TauCoordinate"].astype(str).tolist()))
    e = emb_df.pivot(index="EmpiricalRowID", columns="TauCoordinate", values="EmbeddingValue").loc[row_ids, coord_ids].to_numpy(float)

    h = np.zeros((len(coord_ids), len(coord_ids)), dtype=float)
    cindex = {coord: i for i, coord in enumerate(coord_ids)}
    for _, row in pd.read_csv(HESSIAN).iterrows():
        r = str(row["RowCoordinate"])
        c = str(row["ColumnCoordinate"])
        if r in cindex and c in cindex:
            h[cindex[r], cindex[c]] = float(row["Value"])

    pmorph = dense_from_sparse(PMORPH, coord_ids)
    piperp = dense_from_sparse(PIPERP, row_ids)
    pibal = dense_from_sparse(PIBAL, row_ids)
    p_score = e @ pmorph @ e.T
    h_score = e @ h @ e.T

    comm = h_score @ p_score - p_score @ h_score
    transfer = piperp @ comm @ p_score
    curvature = transfer @ transfer.T
    curvature_perp = piperp @ curvature @ piperp
    curvature_bal = pibal @ curvature_perp @ pibal

    transfer_norm = float(np.linalg.norm(transfer))
    curv_norm = float(np.linalg.norm(curvature))
    perp_norm = float(np.linalg.norm(curvature_perp))
    bal_norm = float(np.linalg.norm(curvature_bal))
    retained = 0.0 if curv_norm == 0.0 else bal_norm / curv_norm
    k_curv = curvature_bal / bal_norm if bal_norm > 0.0 else curvature_bal

    row_meta = emb_df[["EmpiricalRowID", "FamilyID", "ClockIndex"]].drop_duplicates().set_index("EmpiricalRowID").loc[row_ids]
    families = row_meta["FamilyID"].astype(str).tolist()
    total_energy = float(np.sum(k_curv * k_curv))
    family_energy = {}
    for family in sorted(set(families)):
        mask = np.array([fam == family for fam in families], dtype=bool)
        block = k_curv[np.ix_(mask, mask)]
        family_energy[family] = 0.0 if total_energy == 0.0 else float(np.sum(block * block) / total_energy)
    max_family_energy = max(family_energy.values()) if family_energy else 0.0
    diagonal_share = 0.0 if total_energy == 0.0 else float(np.sum(np.diag(k_curv) ** 2) / total_energy)
    symmetry_error = float(np.max(np.abs(k_curv - k_curv.T))) if k_curv.size else 0.0
    min_eigen = float(np.linalg.eigvalsh((k_curv + k_curv.T) / 2.0).min()) if k_curv.size else 0.0
    perp_leakage = float(np.linalg.norm((np.eye(len(row_ids)) - piperp) @ k_curv))

    gates = [
        ("TC-O1_NONZERO_TRANSFER", transfer_norm > 1e-12, transfer_norm, ">1e-12"),
        ("TC-O2_NONZERO_CURVATURE", curv_norm > 1e-12, curv_norm, ">1e-12"),
        ("TC-O3_NONZERO_AFTER_PERP_BALANCE", bal_norm > 1e-12, bal_norm, ">1e-12"),
        ("TC-O4_BALANCED_RETAINED_NORM", retained >= 0.20, retained, ">=0.20"),
        ("TC-O5_MAX_FAMILY_ENERGY", max_family_energy <= 0.50, max_family_energy, "<=0.50"),
        ("TC-O6_DIAGONAL_CONTROL", diagonal_share <= 0.10, diagonal_share, "<=0.10"),
        ("TC-O7_PSD_SYMMETRY", symmetry_error < 1e-10, symmetry_error, "<1e-10"),
        ("TC-O8_PSD_MIN_EIGEN", min_eigen >= -1e-10, min_eigen, ">=-1e-10"),
        ("TC-O9_PERP_LEAKAGE", perp_leakage < 1e-10, perp_leakage, "<1e-10"),
    ]
    gates_df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate,
                "Passed": bool(passed),
                "Observed": float(observed),
                "Threshold": threshold,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate, passed, observed, threshold in gates
        ]
    )
    status = (
        "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_PASS_NO_SCORING"
        if bool(gates_df["Passed"].all())
        else "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_FAIL_NO_SCORING"
    )

    for out_path, matrix in [(OUT_TRANSFER, transfer), (OUT_CURV, k_curv)]:
        pd.DataFrame(
            [
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    **record,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
                for record in matrix_records(matrix, row_ids)
            ]
        ).to_csv(out_path, index=False)
    gates_df.to_csv(OUT_GATES, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "TransferNorm": transfer_norm,
                "CurvatureNorm": curv_norm,
                "PerpCurvatureNorm": perp_norm,
                "BalancedCurvatureNorm": bal_norm,
                "BalancedRetainedNorm": retained,
                "MaxFamilyEnergyShare": max_family_energy,
                "DiagonalEnergyShare": diagonal_share,
                "SymmetryError": symmetry_error,
                "MinEigenvalue": min_eigen,
                "PerpLeakageNorm": perp_leakage,
                "PassedGates": int(gates_df["Passed"].sum()),
                "TotalGates": int(len(gates_df)),
                "ObjectConstructedForPreflight": bool(gates_df["Passed"].all()),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        f"""# P-TauCov TCCS Transfer-Curvature Preflight

Freeze ID: `P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_v1`

Status:

`{status}`

## Purpose

This artifact tests the no-go-corrected TCCS object class at pre-score level:

```text
T_transfer = Pi_perp [H,P] P
K_curv = Pi_perp [H,P] P [H,P]^T Pi_perp
```

It does not use target residuals and does not authorize empirical scoring.

## Preflight Metrics

| Quantity | Value |
|---|---:|
| transfer norm | `{transfer_norm}` |
| curvature norm | `{curv_norm}` |
| post-Pi_perp curvature norm | `{perp_norm}` |
| post-Pi_bal curvature norm | `{bal_norm}` |
| retained norm | `{retained}` |
| max family energy share | `{max_family_energy}` |
| diagonal energy share | `{diagonal_share}` |
| symmetry error | `{symmetry_error}` |
| minimum eigenvalue | `{min_eigen}` |
| Pi_perp leakage norm | `{perp_leakage}` |

## Claim Boundary

Allowed statement:

> The no-go-corrected transfer-curvature object has been inspected at pre-score level.

Forbidden statement:

> The transfer-curvature object has survived empirical scoring or validated Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
