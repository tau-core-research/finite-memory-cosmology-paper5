#!/usr/bin/env python3
"""Audit parent-derived candidates for common-clean-subspace support."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_v1"
CLAIM = "common_clean_subspace_support_audit_no_scoring_no_survival"


PARENT_CANDIDATES = [
    ("PROJECTION_ESSENTIALITY_HESSIAN", EVIDENCE / "p_taucov_projection_essentiality_parent_action_hessian.csv"),
    ("MINIMAL_GLOBAL_PARENT_ACTION_HESSIAN", EVIDENCE / "p_taucov_minimal_global_parent_action_scaffold_hessian.csv"),
    ("PARENT_HESSIAN_COMMUTATOR_OBJECT", EVIDENCE / "p_taucov_parent_hessian_commutator_object.csv"),
    ("S_REST_NO_LEAKAGE_HESSIAN", EVIDENCE / "p_taucov_s_rest_no_leakage_hessian.csv"),
]

SCORE_CANDIDATES = [
    ("TCCS_TRANSFER_CURVATURE", EVIDENCE / "p_taucov_tccs_transfer_curvature_preflight_matrix.csv"),
]


def frob(x: np.ndarray) -> float:
    return float(np.linalg.norm(x, ord="fro"))


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
        mat[idx[str(rec[row_col])], idx[str(rec[col_col])]] = float(rec["Value"])
    return labels, mat


def load_parent_matrix(path: Path, coords: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    mat = np.zeros((len(coords), len(coords)), dtype=float)
    idx = {c: i for i, c in enumerate(coords)}
    for rec in df.to_dict("records"):
        r = str(rec["RowCoordinate"])
        c = str(rec["ColumnCoordinate"])
        if r in idx and c in idx:
            mat[idx[r], idx[c]] = float(rec["Value"])
    return mat


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


def align(labels: list[str], mat: np.ndarray, target: list[str]) -> np.ndarray:
    idx = {label: i for i, label in enumerate(labels)}
    out = np.zeros((len(target), len(target)), dtype=float)
    for i, row in enumerate(target):
        for j, col in enumerate(target):
            out[i, j] = mat[idx[row], idx[col]]
    return out


def matrix_corr(a: np.ndarray, b: np.ndarray) -> float:
    av = a.reshape(-1)
    bv = b.reshape(-1)
    an = np.linalg.norm(av)
    bn = np.linalg.norm(bv)
    if an == 0.0 or bn == 0.0:
        return 0.0
    return float(np.dot(av, bv) / (an * bn))


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


def write_matrix(path: Path, labels: list[str], mat: np.ndarray, candidate_id: str) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ProtocolID", "FreezeID", "CandidateID", "RowID", "ColumnID", "Value", "ScoringAuthorized", "ClaimBoundary"])
        for i, row in enumerate(labels):
            for j, col in enumerate(labels):
                writer.writerow([PROTOCOL_ID, FREEZE_ID, candidate_id, row, col, mat[i, j], False, CLAIM])


def main() -> None:
    rows, coords, emb, meta = load_embedding()
    q_labels, q_clean_raw = load_score_matrix(EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv", "PIBAL_PIPERP_PIBAL")
    p_labels, piperp_raw = load_score_matrix(EVIDENCE / "p_taucov_tccs_piperp_matrix.csv")
    q_clean = align(q_labels, q_clean_raw, rows)
    piperp = align(p_labels, piperp_raw, rows)
    ident = np.eye(len(rows))
    families = meta["FamilyID"].astype(str).tolist()

    candidates: list[tuple[str, str, np.ndarray]] = []
    for cid, path in PARENT_CANDIDATES:
        if path.exists():
            parent = load_parent_matrix(path, coords)
            score = emb @ parent @ emb.T
            candidates.append((cid, "parent_lift", score))
    for cid, path in SCORE_CANDIDATES:
        if path.exists():
            labels, score_raw = load_score_matrix(path)
            candidates.append((cid, "score_native", align(labels, score_raw, rows)))

    rows_out = []
    gates_out = []
    matrices = []
    for cid, source, k_parent in candidates:
        raw_norm = frob(k_parent)
        k_clean = q_clean @ k_parent @ q_clean
        clean_norm = frob(k_clean)
        support = clean_norm / raw_norm if raw_norm > 0.0 else 0.0
        leak = frob((ident - piperp) @ k_clean) / clean_norm if clean_norm > 0.0 else 0.0
        fam_share = family_energy_share(k_clean, families)
        diag = diagonal_share(k_clean)
        q_corr = matrix_corr(k_parent, q_clean)
        gates = [
            ("CCS-A1_NONZERO_PARENT", raw_norm > 1e-12, raw_norm, ">1e-12"),
            ("CCS-A2_SUPPORT_RETENTION", support >= 0.20, support, ">=0.20"),
            ("CCS-A3_PROJECTION_LEAKAGE", leak <= 0.10, leak, "<=0.10"),
            ("CCS-A4_FAMILY_SHARE", fam_share <= 0.50, fam_share, "<=0.50"),
            ("CCS-A5_DIAGONAL_SHARE", diag <= 0.10, diag, "<=0.10"),
        ]
        passed = sum(bool(g[1]) for g in gates)
        status = "CANDIDATE_SUPPORT_PASS_NO_SCORING" if passed == len(gates) else "CANDIDATE_SUPPORT_FAIL_NO_SCORING"
        rows_out.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CandidateID": cid,
                "SourceType": source,
                "Status": status,
                "RawNorm": raw_norm,
                "CleanNorm": clean_norm,
                "SupportRetention": support,
                "ProjectionLeakage": leak,
                "MaxFamilyEnergyShare": fam_share,
                "DiagonalEnergyShare": diag,
                "QCleanCorrelation": q_corr,
                "PassedGates": passed,
                "TotalGates": len(gates),
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        )
        for gate_id, gate_passed, observed, threshold in gates:
            gates_out.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "CandidateID": cid,
                    "GateID": gate_id,
                    "Passed": bool(gate_passed),
                    "Observed": observed,
                    "Threshold": threshold,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM,
                }
            )
        matrices.append((cid, k_clean))

    if not rows_out:
        raise SystemExit("No candidates found")

    EVIDENCE.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    pd.DataFrame(rows_out).to_csv(EVIDENCE / "p_taucov_common_clean_subspace_support_audit_summary.csv", index=False)
    pd.DataFrame(gates_out).to_csv(EVIDENCE / "p_taucov_common_clean_subspace_support_audit_gates.csv", index=False)
    with (EVIDENCE / "p_taucov_common_clean_subspace_support_audit_matrices.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ProtocolID", "FreezeID", "CandidateID", "RowID", "ColumnID", "Value", "ScoringAuthorized", "ClaimBoundary"])
        for cid, mat in matrices:
            for i, row in enumerate(rows):
                for j, col in enumerate(rows):
                    writer.writerow([PROTOCOL_ID, FREEZE_ID, cid, row, col, mat[i, j], False, CLAIM])

    best = max(rows_out, key=lambda r: (r["PassedGates"], r["SupportRetention"]))
    any_pass = any(r["PassedGates"] == r["TotalGates"] for r in rows_out)
    status = (
        "P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_HAS_PREFLIGHT_CANDIDATE_NO_SCORING"
        if any_pass
        else "P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_NO_PASSING_CANDIDATE_NO_SCORING"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "CandidatesTested": len(rows_out),
                "PassingCandidates": sum(r["PassedGates"] == r["TotalGates"] for r in rows_out),
                "BestCandidateID": best["CandidateID"],
                "BestCandidatePassedGates": best["PassedGates"],
                "BestCandidateSupportRetention": best["SupportRetention"],
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_common_clean_subspace_support_audit_overview.csv", index=False)

    table = "\n".join(
        f"| `{r['CandidateID']}` | `{r['Status']}` | `{r['SupportRetention']}` | `{r['ProjectionLeakage']}` | `{r['MaxFamilyEnergyShare']}` | `{r['DiagonalEnergyShare']}` | `{r['PassedGates']} / {r['TotalGates']}` |"
        for r in rows_out
    )
    (DOCS / "p_taucov_common_clean_subspace_support_audit.md").write_text(
        f"""# P-TauCov Common-Clean-Subspace Support Audit

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This target-blind audit tests whether existing parent-derived candidate
matrices have non-negligible support in the frozen common clean subspace:

```text
Q_clean = Pi_bal Pi_perp Pi_bal
K_clean = Q_clean K_parent Q_clean
```

It does not inspect target residual scores and does not authorize empirical
scoring.

## Candidate Results

| Candidate | Status | Support retention | Projection leakage | Max family share | Diagonal share | Gates |
|---|---|---:|---:|---:|---:|---:|
{table}

## Interpretation

Passing this audit would only mean that a candidate is worth considering for a
future frozen scoring manifest. It would not be a Tau validation claim.

If no candidate passes, the current parent-curvature inventory does not yet
provide a clean Tau-specific support object.

## Claim Boundary

Allowed statement:

> Existing parent-derived candidates have been audited for common-clean-subspace support without target residual scoring.

Forbidden statement:

> This audit validates Tau Core, authorizes empirical scoring, or establishes empirical survival.
""",
        encoding="utf-8",
    )
    print(status)


if __name__ == "__main__":
    main()
