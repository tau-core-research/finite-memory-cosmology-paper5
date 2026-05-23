#!/usr/bin/env python3
"""Build a pre-score TCCS object-construction artifact."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

EMBEDDING = EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv"
JTAU = EVIDENCE / "p_taucov_tccs_jtau_anchor_candidate_matrix.csv"
PMORPH = EVIDENCE / "p_taucov_tccs_pmorph_parent_operator.csv"
PIPERP = EVIDENCE / "p_taucov_tccs_piperp_matrix.csv"
PIBAL = EVIDENCE / "p_taucov_clock_family_balance_projector_matrix.csv"
HESSIAN = EVIDENCE / "p_taucov_projection_essentiality_parent_action_hessian.csv"

OUT_MATRIX = EVIDENCE / "p_taucov_tccs_object_preflight_matrix.csv"
OUT_GATES = EVIDENCE / "p_taucov_tccs_object_preflight_gates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_object_preflight_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_object_preflight.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_OBJECT_PREFLIGHT_v1"
CLAIM_BOUNDARY = "tccs_object_preflight_no_scoring_no_survival"


def dense_from_sparse(path: Path, row_col_name: tuple[str, str] = ("RowID", "ColumnID"), value_col: str = "Value", ids: list[str] | None = None) -> tuple[np.ndarray, list[str]]:
    df = pd.read_csv(path)
    rcol, ccol = row_col_name
    if ids is None:
        ids = sorted(set(df[rcol].astype(str)).union(set(df[ccol].astype(str))))
    index = {x: i for i, x in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for _, row in df.iterrows():
        r = str(row[rcol])
        c = str(row[ccol])
        if r in index and c in index:
            mat[index[r], index[c]] = float(row[value_col])
    return mat, ids


def dense_coordinate_matrix(path: Path, ids: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    if "coordinate_id" not in df.columns:
        raise ValueError(f"Expected coordinate_id column in {path}")
    return df.set_index("coordinate_id").loc[ids, ids].to_numpy(float)


def matrix_to_records(matrix: np.ndarray, ids: list[str]) -> list[dict]:
    records = []
    for i, row_id in enumerate(ids):
        for j, col_id in enumerate(ids):
            value = float(matrix[i, j])
            if abs(value) > 1e-14:
                records.append({"RowID": row_id, "ColumnID": col_id, "Value": value})
    return records


def corr(a: np.ndarray, b: np.ndarray) -> float:
    av = a.reshape(-1)
    bv = b.reshape(-1)
    na = float(np.linalg.norm(av))
    nb = float(np.linalg.norm(bv))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(av, bv) / (na * nb))


def main() -> int:
    for path in [EMBEDDING, JTAU, PMORPH, PIPERP, PIBAL, HESSIAN]:
        if not path.exists():
            raise FileNotFoundError(f"Missing input: {path.relative_to(ROOT)}")

    emb_df = pd.read_csv(EMBEDDING)
    row_ids = list(dict.fromkeys(emb_df["EmpiricalRowID"].astype(str).tolist()))
    coord_ids = list(dict.fromkeys(emb_df["TauCoordinate"].astype(str).tolist()))
    e = emb_df.pivot(index="EmpiricalRowID", columns="TauCoordinate", values="EmbeddingValue").loc[row_ids, coord_ids].to_numpy(float)

    h_df = pd.read_csv(HESSIAN)
    h = np.zeros((len(coord_ids), len(coord_ids)), dtype=float)
    cindex = {coord: i for i, coord in enumerate(coord_ids)}
    for _, row in h_df.iterrows():
        r = str(row["RowCoordinate"])
        c = str(row["ColumnCoordinate"])
        if r in cindex and c in cindex:
            h[cindex[r], cindex[c]] = float(row["Value"])
    jtau = dense_coordinate_matrix(JTAU, coord_ids)
    pmorph, _ = dense_from_sparse(PMORPH, ids=coord_ids)
    piperp, _ = dense_from_sparse(PIPERP, ids=row_ids)
    pibal, _ = dense_from_sparse(PIBAL, ids=row_ids)

    comm_parent = h @ pmorph - pmorph @ h
    orientation_margin = corr(comm_parent, jtau)
    oriented_parent = comm_parent if orientation_margin > 0.0 else -comm_parent
    raw_score = e @ oriented_parent @ e.T
    after_perp = piperp @ raw_score @ piperp
    after_bal = pibal @ after_perp @ pibal
    norm_raw = float(np.linalg.norm(raw_score))
    norm_perp = float(np.linalg.norm(after_perp))
    norm_bal = float(np.linalg.norm(after_bal))
    retained = 0.0 if norm_raw == 0.0 else norm_bal / norm_raw
    tccs = after_bal / norm_bal if norm_bal > 0 else after_bal

    row_meta = emb_df[["EmpiricalRowID", "FamilyID", "ClockIndex"]].drop_duplicates().set_index("EmpiricalRowID").loc[row_ids]
    families = row_meta["FamilyID"].astype(str).tolist()
    family_energy = {}
    total_energy = float(np.sum(tccs * tccs))
    for family in sorted(set(families)):
        mask = np.array([fam == family for fam in families], dtype=bool)
        block = tccs[np.ix_(mask, mask)]
        family_energy[family] = 0.0 if total_energy == 0.0 else float(np.sum(block * block) / total_energy)
    max_family_energy = max(family_energy.values()) if family_energy else 0.0
    diagonal_share = 0.0 if total_energy == 0.0 else float(np.sum(np.diag(tccs) ** 2) / total_energy)
    symmetry_error = float(np.max(np.abs(tccs + tccs.T))) if tccs.size else 0.0
    perp_leakage = float(np.linalg.norm((np.eye(len(row_ids)) - piperp) @ tccs))

    gates = [
        ("TCCS-O1_NONZERO_COMMUTATOR", norm_raw > 1e-12, norm_raw, ">1e-12"),
        ("TCCS-O2_POSITIVE_ORIENTATION_MARGIN", orientation_margin > 0.0, orientation_margin, ">0"),
        ("TCCS-O3_NONZERO_AFTER_PERP_BALANCE", norm_bal > 1e-12, norm_bal, ">1e-12"),
        ("TCCS-O4_BALANCED_RETAINED_NORM", retained >= 0.20, retained, ">=0.20"),
        ("TCCS-O5_MAX_FAMILY_ENERGY", max_family_energy <= 0.50, max_family_energy, "<=0.50"),
        ("TCCS-O6_DIAGONAL_CONTROL", diagonal_share <= 0.10, diagonal_share, "<=0.10"),
        ("TCCS-O7_PERP_LEAKAGE", perp_leakage < 1e-10, perp_leakage, "<1e-10"),
        ("TCCS-O8_ORIENTED_SKEW_STRUCTURE", symmetry_error < 1e-10, symmetry_error, "<1e-10"),
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
        "P_TAUCOV_TCCS_OBJECT_PREFLIGHT_PASS_NO_SCORING"
        if bool(gates_df["Passed"].all())
        else "P_TAUCOV_TCCS_OBJECT_PREFLIGHT_FAIL_NO_SCORING"
    )

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **record,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for record in matrix_to_records(tccs, row_ids)
        ]
    ).to_csv(OUT_MATRIX, index=False)
    gates_df.to_csv(OUT_GATES, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "RawNorm": norm_raw,
                "PerpNorm": norm_perp,
                "BalancedNorm": norm_bal,
                "BalancedRetainedNorm": retained,
                "OrientationMargin": orientation_margin,
                "MaxFamilyEnergyShare": max_family_energy,
                "DiagonalEnergyShare": diagonal_share,
                "PerpLeakageNorm": perp_leakage,
                "SkewSymmetryError": symmetry_error,
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
        f"""# P-TauCov TCCS Object Preflight

Freeze ID: `P_TAUCOV_TCCS_OBJECT_PREFLIGHT_v1`

Status:

`{status}`

## Purpose

This artifact constructs the TCCS object only at pre-score level:

```text
T_tau = Normalize(Pi_bal Pi_perp Orient_+([L_B_red, P_morph]; J_tau) Pi_perp Pi_bal)
```

It does not use target residuals and does not authorize empirical scoring.

## Preflight Metrics

| Quantity | Value |
|---|---:|
| raw commutator norm | `{norm_raw}` |
| post-Pi_perp norm | `{norm_perp}` |
| post-Pi_bal norm | `{norm_bal}` |
| retained norm | `{retained}` |
| orientation margin | `{orientation_margin}` |
| max family energy share | `{max_family_energy}` |
| diagonal energy share | `{diagonal_share}` |
| Pi_perp leakage norm | `{perp_leakage}` |
| skew-symmetry error | `{symmetry_error}` |

## Claim Boundary

Allowed statement:

> A TCCS object has been constructed for pre-score structural inspection if all gates pass.

Forbidden statement:

> The TCCS object has survived empirical scoring or validated Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
