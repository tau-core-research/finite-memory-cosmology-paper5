#!/usr/bin/env python3
"""Build a target-blind domain-compatibility audit for P-TauCov cleaners."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_v1"
CLAIM = "domain_compatibility_audit_no_scoring_no_survival"


def load_square_matrix(path: Path, row_col: str, col_col: str, value_col: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    rows = list(dict.fromkeys(df[row_col].astype(str)))
    cols = list(dict.fromkeys(df[col_col].astype(str)))
    labels = rows if rows == cols else sorted(set(rows) | set(cols))
    idx = {label: i for i, label in enumerate(labels)}
    matrix = np.zeros((len(labels), len(labels)), dtype=float)
    for rec in df.to_dict("records"):
        matrix[idx[str(rec[row_col])], idx[str(rec[col_col])]] = float(rec[value_col])
    return labels, matrix


def align_matrix(labels: list[str], matrix: np.ndarray, target_labels: list[str]) -> np.ndarray:
    idx = {label: i for i, label in enumerate(labels)}
    out = np.zeros((len(target_labels), len(target_labels)), dtype=float)
    for i, row in enumerate(target_labels):
        for j, col in enumerate(target_labels):
            out[i, j] = matrix[idx[row], idx[col]]
    return out


def frob(x: np.ndarray) -> float:
    return float(np.linalg.norm(x, ord="fro"))


def rank(x: np.ndarray, tol: float = 1e-10) -> int:
    return int(np.linalg.matrix_rank(x, tol=tol))


def write_matrix(path: Path, labels: list[str], matrix: np.ndarray, matrix_id: str) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "ProtocolID",
                "FreezeID",
                "MatrixID",
                "RowID",
                "ColumnID",
                "Value",
                "UsesTargetResiduals",
                "UsesScoreOutcomes",
                "ScoringAuthorized",
                "ClaimBoundary",
            ]
        )
        for i, row in enumerate(labels):
            for j, col in enumerate(labels):
                writer.writerow([PROTOCOL_ID, FREEZE_ID, matrix_id, row, col, matrix[i, j], False, False, False, CLAIM])


def main() -> None:
    p_labels, piperp_raw = load_square_matrix(
        EVIDENCE / "p_taucov_tccs_piperp_matrix.csv", "RowID", "ColumnID", "Value"
    )
    b_labels, pibal_raw = load_square_matrix(
        EVIDENCE / "p_taucov_clock_family_balance_projector_matrix.csv", "RowID", "ColumnID", "Value"
    )
    if set(p_labels) != set(b_labels):
        raise SystemExit("Pi_perp and Pi_bal label sets differ")

    labels = p_labels
    piperp = piperp_raw
    pibal = align_matrix(b_labels, pibal_raw, labels)

    n = len(labels)
    ident = np.eye(n)
    comm = pibal @ piperp - piperp @ pibal
    sym_cleaner = pibal @ piperp @ pibal
    alt_cleaner = piperp @ pibal @ piperp

    piperp_norm = frob(piperp)
    pibal_norm = frob(pibal)
    comm_norm = frob(comm)
    comm_rel = comm_norm / max(piperp_norm * pibal_norm, 1e-12)
    sym_diff = frob(sym_cleaner - alt_cleaner)
    sym_diff_rel = sym_diff / max(frob(sym_cleaner) + frob(alt_cleaner), 1e-12)

    piperp_idem = frob(piperp @ piperp - piperp)
    pibal_idem = frob(pibal @ pibal - pibal)
    piperp_sym = frob(piperp - piperp.T)
    pibal_sym = frob(pibal - pibal.T)

    rank_piperp = rank(piperp)
    rank_pibal = rank(pibal)
    rank_sym = rank(sym_cleaner)
    trace_sym = float(np.trace(sym_cleaner))

    # This is a structural audit. Thresholds are deliberately strict enough to
    # block scoring if the two cleaners are not approximately compatible.
    gates = [
        ("DC-A1_LABELS_MATCH", True, "true", "required"),
        ("DC-A2_PIPERP_PROJECTOR", piperp_idem < 1e-10 and piperp_sym < 1e-10, f"{piperp_idem};{piperp_sym}", "<1e-10"),
        ("DC-A3_PIBAL_PROJECTOR", pibal_idem < 1e-10 and pibal_sym < 1e-10, f"{pibal_idem};{pibal_sym}", "<1e-10"),
        ("DC-A4_LOW_COMMUTATOR", comm_rel <= 0.05, comm_rel, "<=0.05"),
        ("DC-A5_ORDER_STABILITY", sym_diff_rel <= 0.05, sym_diff_rel, "<=0.05"),
        ("DC-A6_NONZERO_COMMON_CLEANER", frob(sym_cleaner) > 1e-12 and rank_sym > 0, f"{frob(sym_cleaner)};{rank_sym}", ">0"),
        ("DC-A7_NO_RANK_COLLAPSE", rank_sym >= min(rank_piperp, rank_pibal) * 0.5, rank_sym, ">=0.5*min(rank)"),
    ]
    status = (
        "P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_PASS_NO_SCORING"
        if all(bool(g[1]) for g in gates)
        else "P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_FAIL_NO_SCORING"
    )

    EVIDENCE.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)

    write_matrix(EVIDENCE / "p_taucov_domain_compatibility_commutator_matrix.csv", labels, comm, "COMMUTATOR_PIBAL_PIPERP")
    write_matrix(EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv", labels, sym_cleaner, "PIBAL_PIPERP_PIBAL")

    summary_path = EVIDENCE / "p_taucov_domain_compatibility_audit_summary.csv"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "Rows": n,
                "RankPiPerp": rank_piperp,
                "RankPiBal": rank_pibal,
                "RankCommonCleaner": rank_sym,
                "TraceCommonCleaner": trace_sym,
                "PiPerpIdempotenceError": piperp_idem,
                "PiBalIdempotenceError": pibal_idem,
                "PiPerpSymmetryError": piperp_sym,
                "PiBalSymmetryError": pibal_sym,
                "CleanerCommutatorNorm": comm_norm,
                "CleanerCommutatorRelative": comm_rel,
                "OrderDifferenceNorm": sym_diff,
                "OrderDifferenceRelative": sym_diff_rel,
                "PassedGates": sum(bool(g[1]) for g in gates),
                "TotalGates": len(gates),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(summary_path, index=False)

    gates_path = EVIDENCE / "p_taucov_domain_compatibility_audit_gates.csv"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "Observed": observed,
                "Threshold": threshold,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for gate_id, passed, observed, threshold in gates
        ]
    ).to_csv(gates_path, index=False)

    doc = DOCS / "p_taucov_domain_compatibility_audit.md"
    doc.write_text(
        f"""# P-TauCov Domain-Compatibility Audit

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This target-blind audit checks whether the frozen projection-orthogonal cleaner
`Pi_perp` and the frozen branch/family balance cleaner `Pi_bal` behave as
compatible operators in the same score-space geometry.

It does not inspect target residual scores and does not authorize empirical
scoring.

## Metrics

| Quantity | Value |
|---|---:|
| rows | `{n}` |
| rank `Pi_perp` | `{rank_piperp}` |
| rank `Pi_bal` | `{rank_pibal}` |
| rank common cleaner `Pi_bal Pi_perp Pi_bal` | `{rank_sym}` |
| trace common cleaner | `{trace_sym}` |
| relative commutator norm | `{comm_rel}` |
| relative order-difference norm | `{sym_diff_rel}` |
| passed gates | `{sum(bool(g[1]) for g in gates)} / {len(gates)}` |

## Interpretation

If this audit fails, a future TCCS/P-TauCov object must not treat projection
orthogonality and branch balance as independent post-processing filters. The
operators must either be derived from a common parent domain, or their
non-commutation must be frozen as the observable itself before scoring.

## Claim Boundary

Allowed statement:

> The compatibility of the frozen cleaning operators has been audited without target residual scoring.

Forbidden statement:

> This audit validates a Tau signal, authorizes scoring, or proves physical domain compatibility.
""",
        encoding="utf-8",
    )

    print(status)


if __name__ == "__main__":
    main()
