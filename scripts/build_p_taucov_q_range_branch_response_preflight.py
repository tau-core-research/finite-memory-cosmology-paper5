#!/usr/bin/env python3
"""Retest minimal branch-response contrast using frozen Q_range."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_v1"
CLAIM = "q_range_branch_response_preflight_no_scoring_no_survival"


def load_embedding():
    df = pd.read_csv(EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv")
    rows = list(dict.fromkeys(df["EmpiricalRowID"].astype(str)))
    coords = list(dict.fromkeys(df["TauCoordinate"].astype(str)))
    mat = np.zeros((len(rows), len(coords)))
    r_idx = {r: i for i, r in enumerate(rows)}
    c_idx = {c: i for i, c in enumerate(coords)}
    for rec in df.to_dict("records"):
        mat[r_idx[str(rec["EmpiricalRowID"])], c_idx[str(rec["TauCoordinate"])]] = float(rec["EmbeddingValue"])
    meta = df[["EmpiricalRowID", "FamilyID", "ClockIndex"]].drop_duplicates().set_index("EmpiricalRowID").loc[rows]
    return rows, coords, mat, meta


def load_matrix(path: Path):
    df = pd.read_csv(path)
    rows = list(dict.fromkeys(df["RowID"].astype(str)))
    cols = list(dict.fromkeys(df["ColumnID"].astype(str)))
    idx = {r: i for i, r in enumerate(rows)}
    mat = np.zeros((len(rows), len(cols)))
    for rec in df.to_dict("records"):
        mat[idx[str(rec["RowID"])], idx[str(rec["ColumnID"])]] = float(rec["Value"])
    return rows, mat


def align(labels, mat, target):
    idx = {x: i for i, x in enumerate(labels)}
    out = np.zeros((len(target), len(target)))
    for i, r in enumerate(target):
        for j, c in enumerate(target):
            out[i, j] = mat[idx[r], idx[c]]
    return out


def frob(x):
    return float(np.linalg.norm(x, ord="fro"))


def share_family(mat, families):
    total = float(np.sum(mat * mat))
    if total == 0:
        return 0.0
    return max(float(np.sum(mat[np.ix_([i for i, f in enumerate(families) if f == fam], [i for i, f in enumerate(families) if f == fam])] ** 2)) / total for fam in sorted(set(families)))


def diag_share(mat):
    total = float(np.sum(mat * mat))
    return 0.0 if total == 0 else float(np.sum(np.diag(mat) ** 2) / total)


def main():
    rows, coords, emb, meta = load_embedding()
    q_labels, q_range_raw = load_matrix(EVIDENCE / "p_taucov_q_range_projector_matrix.csv")
    p_labels, piperp_raw = load_matrix(EVIDENCE / "p_taucov_tccs_piperp_matrix.csv")
    q_range = align(q_labels, q_range_raw, rows)
    piperp = align(p_labels, piperp_raw, rows)
    ident = np.eye(len(rows))

    cidx = {c: i for i, c in enumerate(coords)}
    v = emb[:, cidx["TEMPLATE_B_BRANCH_RESPONSE"]] - emb[:, cidx["TEMPLATE_PHI_PARENT_SOURCE"]]
    vq = q_range @ v
    raw_norm = float(np.linalg.norm(v))
    q_norm = float(np.linalg.norm(vq))
    retention = q_norm / raw_norm if raw_norm > 0 else 0.0
    kq = np.outer(vq, vq)
    kn = frob(kq)
    closure = frob(q_range @ kq @ q_range - kq) / kn if kn > 0 else 0.0
    leakage = frob((ident - piperp) @ kq) / kn if kn > 0 else 0.0
    families = meta["FamilyID"].astype(str).tolist()
    fam = share_family(kq, families)
    diag = diag_share(kq)
    gates = [
        ("QBR-G1_NONZERO_SOURCE", raw_norm > 1e-12, raw_norm, ">1e-12"),
        ("QBR-G2_QRANGE_RETENTION", retention >= 0.20, retention, ">=0.20"),
        ("QBR-G3_QRANGE_CLOSURE", closure <= 1e-10, closure, "<=1e-10"),
        ("QBR-G4_PROJECTION_LEAKAGE", leakage <= 0.10, leakage, "<=0.10"),
        ("QBR-G5_FAMILY_SHARE", fam <= 0.50, fam, "<=0.50"),
        ("QBR-G6_DIAGONAL_SHARE", diag <= 0.10, diag, "<=0.10"),
    ]
    passed = sum(bool(g[1]) for g in gates)
    status = "P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_PASS_NO_SCORING" if passed == len(gates) else "P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_FAIL_NO_SCORING"

    pd.DataFrame([{
        "ProtocolID": PROTOCOL_ID, "FreezeID": FREEZE_ID, "Status": status,
        "RawVectorNorm": raw_norm, "QRangeVectorNorm": q_norm,
        "QRangeRetention": retention, "QRangeClosureError": closure,
        "ProjectionLeakage": leakage, "MaxFamilyEnergyShare": fam,
        "DiagonalEnergyShare": diag, "PassedGates": passed, "TotalGates": len(gates),
        "ScoringAuthorized": False, "SurvivalClaimAuthorized": False,
        "TauCoreValidationClaimAuthorized": False, "ClaimBoundary": CLAIM
    }]).to_csv(EVIDENCE / "p_taucov_q_range_branch_response_preflight_summary.csv", index=False)
    pd.DataFrame([{
        "ProtocolID": PROTOCOL_ID, "FreezeID": FREEZE_ID, "GateID": gid,
        "Passed": bool(ok), "Observed": obs, "Threshold": th,
        "ScoringAuthorized": False, "ClaimBoundary": CLAIM
    } for gid, ok, obs, th in gates]).to_csv(EVIDENCE / "p_taucov_q_range_branch_response_preflight_gates.csv", index=False)
    with (EVIDENCE / "p_taucov_q_range_branch_response_preflight_matrix.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ProtocolID", "FreezeID", "RowID", "ColumnID", "Value", "ScoringAuthorized", "ClaimBoundary"])
        for i, r in enumerate(rows):
            for j, c in enumerate(rows):
                w.writerow([PROTOCOL_ID, FREEZE_ID, r, c, kq[i, j], False, CLAIM])
    (DOCS / "p_taucov_q_range_branch_response_preflight.md").write_text(f"""# P-TauCov Q-Range Branch-Response Preflight

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This preflight retests the minimal branch-response contrast using the frozen
orthogonal range projector `Q_range`, rather than repeated multiplication by
the non-idempotent cleaner `Q_clean`.

```text
v_branch = E[:, B_BRANCH_RESPONSE] - E[:, PHI_PARENT_SOURCE]
v_Q = Q_range v_branch
K_Q = v_Q v_Q^T
```

It does not inspect target residual scores and does not authorize empirical scoring.

## Metrics

| Quantity | Value |
|---|---:|
| raw vector norm | `{raw_norm}` |
| Q-range vector norm | `{q_norm}` |
| Q-range retention | `{retention}` |
| Q-range closure error | `{closure}` |
| projection leakage | `{leakage}` |
| max family energy share | `{fam}` |
| diagonal energy share | `{diag}` |
| passed gates | `{passed} / {len(gates)}` |

## Claim Boundary

Allowed statement:

> The minimal branch-response contrast has been retested with the frozen Q-range projector.

Forbidden statement:

> This preflight validates Tau Core, authorizes scoring, or establishes empirical survival.
""", encoding="utf-8")
    print(status)


if __name__ == "__main__":
    main()
