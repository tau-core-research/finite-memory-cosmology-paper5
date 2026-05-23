#!/usr/bin/env python3
"""Freeze the orthogonal range projector of Q_clean from its spectrum."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_v1"
CLAIM = "q_range_projector_freeze_no_object_no_scoring"
EIGEN_THRESHOLD = 1e-10


def load_matrix(path: Path, matrix_id: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    df = df[df["MatrixID"].astype(str) == matrix_id]
    rows = list(dict.fromkeys(df["RowID"].astype(str)))
    cols = list(dict.fromkeys(df["ColumnID"].astype(str)))
    if rows != cols:
        raise SystemExit("Q_clean labels are not square/aligned")
    idx = {r: i for i, r in enumerate(rows)}
    mat = np.zeros((len(rows), len(rows)), dtype=float)
    for rec in df.to_dict("records"):
        mat[idx[str(rec["RowID"])], idx[str(rec["ColumnID"])]] = float(rec["Value"])
    return rows, mat


def frob(x: np.ndarray) -> float:
    return float(np.linalg.norm(x, ord="fro"))


def write_matrix(path: Path, labels: list[str], mat: np.ndarray) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ProtocolID", "FreezeID", "RowID", "ColumnID", "Value", "ScoringAuthorized", "ClaimBoundary"])
        for i, row in enumerate(labels):
            for j, col in enumerate(labels):
                writer.writerow([PROTOCOL_ID, FREEZE_ID, row, col, mat[i, j], False, CLAIM])


def main() -> int:
    labels, q_clean = load_matrix(EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv", "PIBAL_PIPERP_PIBAL")
    q_sym = 0.5 * (q_clean + q_clean.T)
    evals, evecs = np.linalg.eigh(q_sym)
    active = evals > EIGEN_THRESHOLD
    u_active = evecs[:, active]
    q_range = u_active @ u_active.T if u_active.size else np.zeros_like(q_clean)

    symmetry_error = frob(q_range - q_range.T)
    idempotence_error = frob(q_range @ q_range - q_range)
    q_clean_symmetry_error = frob(q_clean - q_clean.T)
    rank = int(active.sum())
    trace = float(np.trace(q_range))
    min_active = float(evals[active].min()) if active.any() else 0.0
    max_inactive = float(evals[~active].max()) if (~active).any() else 0.0

    gates = [
        ("QR-G1_QCLEAN_SYMMETRIC", q_clean_symmetry_error < 1e-10, q_clean_symmetry_error, "<1e-10"),
        ("QR-G2_NONZERO_RANGE", rank > 0, rank, ">0"),
        ("QR-G3_PROJECTOR_SYMMETRIC", symmetry_error < 1e-10, symmetry_error, "<1e-10"),
        ("QR-G4_PROJECTOR_IDEMPOTENT", idempotence_error < 1e-10, idempotence_error, "<1e-10"),
        ("QR-G5_THRESHOLD_DECLARED", EIGEN_THRESHOLD == 1e-10, EIGEN_THRESHOLD, "1e-10"),
    ]
    status = (
        "P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_PASS_NO_SCORING"
        if all(bool(g[1]) for g in gates)
        else "P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_FAIL_NO_SCORING"
    )

    EVIDENCE.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    write_matrix(EVIDENCE / "p_taucov_q_range_projector_matrix.csv", labels, q_range)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "Rows": len(labels),
                "EigenThreshold": EIGEN_THRESHOLD,
                "ActiveRank": rank,
                "TraceQRange": trace,
                "MinActiveEigenvalue": min_active,
                "MaxInactiveEigenvalue": max_inactive,
                "QCleanSymmetryError": q_clean_symmetry_error,
                "QRangeSymmetryError": symmetry_error,
                "QRangeIdempotenceError": idempotence_error,
                "PassedGates": sum(bool(g[1]) for g in gates),
                "TotalGates": len(gates),
                "ObjectConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_range_projector_summary.csv", index=False)
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
    ).to_csv(EVIDENCE / "p_taucov_q_range_projector_gates.csv", index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "EigenIndex": i,
                "Eigenvalue": float(ev),
                "Active": bool(ev > EIGEN_THRESHOLD),
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for i, ev in enumerate(evals)
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_range_projector_spectrum.csv", index=False)

    (DOCS / "p_taucov_q_range_projector_freeze.md").write_text(
        f"""# P-TauCov Q-Range Projector Freeze

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This artifact freezes the orthogonal projector onto the range of the common
cleaner:

```text
Q_clean = Pi_bal Pi_perp Pi_bal
Q_range = U_active U_active^T
```

where active eigenvectors are selected from the spectrum of `Q_clean` using the
predeclared threshold:

```text
eigenvalue > {EIGEN_THRESHOLD}
```

It does not construct a Tau candidate and does not authorize empirical scoring.

## Metrics

| Quantity | Value |
|---|---:|
| rows | `{len(labels)}` |
| active rank | `{rank}` |
| trace `Q_range` | `{trace}` |
| min active eigenvalue | `{min_active}` |
| max inactive eigenvalue | `{max_inactive}` |
| `Q_clean` symmetry error | `{q_clean_symmetry_error}` |
| `Q_range` symmetry error | `{symmetry_error}` |
| `Q_range` idempotence error | `{idempotence_error}` |
| passed gates | `{sum(bool(g[1]) for g in gates)} / {len(gates)}` |

## Claim Boundary

Allowed statement:

> The orthogonal range projector of the frozen common cleaner has been constructed without target residual scoring.

Forbidden statement:

> The Q-range projector validates Tau Core, constructs a scoreable candidate, or authorizes empirical scoring.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
