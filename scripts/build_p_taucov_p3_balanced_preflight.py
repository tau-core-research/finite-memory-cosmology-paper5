#!/usr/bin/env python3
"""Build a no-scoring balance preflight for the P3 parent-side operator."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
P3 = ROOT / "data/p_taucov/linear/P3_core_mixing_operator.csv"
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
PROJECTOR = ROOT / "evidence/p_taucov_clock_family_balance_projector_matrix.csv"
OUT_MATRIX = ROOT / "evidence/p_taucov_p3_balanced_preflight_matrix.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_preflight_summary.csv"
OUT_MD = ROOT / "docs/p_taucov_p3_balanced_preflight.md"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_PREFLIGHT_v1"
STATUS = "P_TAUCOV_P3_BALANCED_PREFLIGHT_READY_NO_CANDIDATE_NO_SCORING"

COORDINATE_ALIASES = {
    "Phi_source": "TEMPLATE_PHI_PARENT_SOURCE",
    "P_projection": "TEMPLATE_P_MORPH_PROJECTION",
}


def read_square_csv(path: Path) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    ids = df.iloc[:, 0].astype(str).tolist()
    mat = df[ids].astype(float).to_numpy()
    return ids, mat


def read_long_matrix(path: Path) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    ids = sorted(set(df["RowID"].astype(str)) | set(df["ColumnID"].astype(str)))
    idx = {rid: i for i, rid in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowID)], idx[str(row.ColumnID)]] = float(row.Value)
    return ids, 0.5 * (mat + mat.T)


def bridge_matrix(tau_ids: list[str]) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(BRIDGE)
    row_ids = (
        df[["EmpiricalIndex", "EmpiricalRowID"]]
        .drop_duplicates()
        .sort_values("EmpiricalIndex")["EmpiricalRowID"]
        .astype(str)
        .tolist()
    )
    tau_idx = {cid: i for i, cid in enumerate(tau_ids)}
    empirical_idx = {rid: i for i, rid in enumerate(row_ids)}
    bridge = np.zeros((len(row_ids), len(tau_ids)), dtype=float)
    for row in df.itertuples(index=False):
        tau_coordinate = COORDINATE_ALIASES.get(str(row.TauCoordinate), str(row.TauCoordinate))
        if tau_coordinate in tau_idx:
            bridge[empirical_idx[str(row.EmpiricalRowID)], tau_idx[tau_coordinate]] = float(row.BridgeValue)
    return row_ids, bridge


def normalize(mat: np.ndarray) -> np.ndarray:
    mat = 0.5 * (mat + mat.T)
    fro = float(np.linalg.norm(mat, ord="fro"))
    if fro == 0.0:
        return mat
    return mat / fro


def offdiag(mat: np.ndarray) -> np.ndarray:
    out = mat.copy()
    np.fill_diagonal(out, 0.0)
    return out


def main() -> int:
    tau_ids, p3 = read_square_csv(P3)
    empirical_ids, bridge = bridge_matrix(tau_ids)
    projector_ids, r_balance = read_long_matrix(PROJECTOR)
    if empirical_ids != projector_ids:
        raise RuntimeError("Projector row order mismatch.")

    k_parent_empirical = normalize(bridge @ p3 @ p3.T @ bridge.T)
    k_balanced_raw = r_balance @ k_parent_empirical @ r_balance
    k_balanced = normalize(k_balanced_raw)
    k_balanced_offdiag = normalize(offdiag(k_balanced))

    parent_fro = float(np.linalg.norm(k_parent_empirical, ord="fro"))
    balanced_raw_fro = float(np.linalg.norm(k_balanced_raw, ord="fro"))
    retention = 0.0 if parent_fro == 0.0 else float(balanced_raw_fro / parent_fro)
    diagonal_share = float(np.linalg.norm(np.diag(np.diag(k_balanced)), ord="fro") / np.linalg.norm(k_balanced, ord="fro"))
    offdiag_share = float(np.linalg.norm(offdiag(k_balanced), ord="fro") / np.linalg.norm(k_balanced, ord="fro"))
    rank = int(np.linalg.matrix_rank(k_balanced))
    eigvals = np.linalg.eigvalsh(k_balanced)

    family_clock_leak = float(np.linalg.norm(r_balance @ k_balanced - k_balanced, ord="fro"))
    idempotent_under_balance = float(np.linalg.norm(r_balance @ k_balanced @ r_balance - k_balanced, ord="fro"))

    matrix_rows = []
    for i, rid_i in enumerate(empirical_ids):
        for j, rid_j in enumerate(empirical_ids):
            value = float(k_balanced_offdiag[i, j])
            if abs(value) > 1e-14:
                matrix_rows.append(
                    {
                        "AuditID": AUDIT_ID,
                        "RowID": rid_i,
                        "ColumnID": rid_j,
                        "Value": value,
                        "Construction": "P3_parent_operator_projected_by_R_balance_then_zero_diagonal_normalized",
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                    }
                )
    pd.DataFrame(matrix_rows).to_csv(OUT_MATRIX, index=False)

    summary = {
        "AuditID": AUDIT_ID,
        "Status": STATUS,
        "Rows": int(len(empirical_ids)),
        "ParentFrobeniusNorm": parent_fro,
        "BalancedRawFrobeniusNorm": balanced_raw_fro,
        "BalanceRetention": retention,
        "BalancedRank": rank,
        "MinEigenvalueBalanced": float(eigvals.min()),
        "MaxEigenvalueBalanced": float(eigvals.max()),
        "DiagonalShareBeforeOffdiagRemoval": diagonal_share,
        "OffDiagonalShareBeforeOffdiagRemoval": offdiag_share,
        "BalanceProjectorLeftLeakageFrobenius": family_clock_leak,
        "BalanceProjectorSandwichLeakageFrobenius": idempotent_under_balance,
        "OffDiagonalMatrixRows": int(len(matrix_rows)),
        "UsesTargetResiduals": False,
        "UsesScoreOutcome": False,
        "CandidateConstructed": False,
        "ScoringAuthorized": False,
        "ClaimBoundary": "p3_balanced_preflight_no_candidate_no_scoring",
    }
    pd.DataFrame([summary]).to_csv(OUT_SUMMARY, index=False)

    md = f"""# P-TauCov P3 Balanced Preflight

Audit ID: `{AUDIT_ID}`

Status:

`{STATUS}`

## Purpose

This preflight applies the frozen clock/family balance projector to the target-blind P3 parent-side core-mixing operator. It checks whether nontrivial structure remains after removing intercept, family, and clock-block nuisance directions.

This is not a candidate and not a scorecard.

## Construction

```text
K_parent = bridge P3 P3^T bridge^T
K_balanced = R_balance K_parent R_balance
K_preflight = offdiag(K_balanced) / ||offdiag(K_balanced)||_F
```

The off-diagonal matrix is emitted only as a preflight artifact. It is not authorized for scoring.

## Metrics

```text
Rows = {summary["Rows"]}
BalanceRetention = {summary["BalanceRetention"]}
BalancedRank = {summary["BalancedRank"]}
MinEigenvalueBalanced = {summary["MinEigenvalueBalanced"]}
MaxEigenvalueBalanced = {summary["MaxEigenvalueBalanced"]}
DiagonalShareBeforeOffdiagRemoval = {summary["DiagonalShareBeforeOffdiagRemoval"]}
OffDiagonalShareBeforeOffdiagRemoval = {summary["OffDiagonalShareBeforeOffdiagRemoval"]}
BalanceProjectorLeftLeakageFrobenius = {summary["BalanceProjectorLeftLeakageFrobenius"]}
BalanceProjectorSandwichLeakageFrobenius = {summary["BalanceProjectorSandwichLeakageFrobenius"]}
```

## Interpretation

If retention is nonzero and balance leakage is numerical-noise level, then the parent-side P3 object has a score-independent balanced residual structure that can be audited further.

This still does not authorize scoring. A separate readiness and manifest gate would be required.

## Claim Boundary

Allowed statement:

> The target-blind P3 parent-side operator retains a balanced, nontrivial off-diagonal structure after family/clock nuisance removal.

Forbidden statement:

> The balanced P3 object has produced a Tau signal, survived P-TauCov scoring, or validated Tau Core.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
