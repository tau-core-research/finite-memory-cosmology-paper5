#!/usr/bin/env python3
"""Run epsilon-P3 P-TauCov alignment scorecard after final authorization.

This script is intentionally inert until a final authorization manifest exists
and explicitly sets `PTauCovScoringAuthorized: true`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization.yaml"
BRANCH = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.csv"
OBSERVED = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_matrix.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_alignment_scorecard.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_alignment_scorecard_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_EPSILON_P3_ALIGNMENT_SCORECARD_v1"
CLAIM_BOUNDARY = "epsilon_p3_alignment_scorecard_requires_final_authorization"


def load_authorization() -> dict:
    if not AUTH.exists():
        raise RuntimeError("Missing final authorization manifest; scoring is not authorized.")
    auth = yaml.safe_load(AUTH.read_text(encoding="utf-8")) or {}
    if auth.get("PTauCovScoringAuthorized") is not True:
        raise RuntimeError("Final authorization does not permit P-TauCov scoring.")
    return auth


def matrix_from_long(path: Path, value_col: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    ids = sorted(set(df["RowCoordinate"].astype(str)) | set(df["ColumnCoordinate"].astype(str)))
    idx = {cid: i for i, cid in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = float(getattr(row, value_col))
    return ids, mat


def frobenius_alignment(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> float:
    a_m = a * mask
    b_m = b * mask
    denom = float(np.linalg.norm(a_m, ord="fro") * np.linalg.norm(b_m, ord="fro"))
    if denom == 0.0:
        return float("nan")
    return float(np.sum(a_m * b_m) / denom)


def main() -> int:
    load_authorization()
    branch_ids, branch_delta = matrix_from_long(BRANCH, "DeltaCTau")
    observed_ids, observed = matrix_from_long(OBSERVED, "ObservedWhitenedCovarianceResidual")
    if branch_ids != observed_ids:
        raise RuntimeError("Observed input coordinate IDs do not match frozen branch support IDs.")

    branch = pd.read_csv(BRANCH)
    omega = np.zeros_like(branch_delta, dtype=float)
    idx = {cid: i for i, cid in enumerate(branch_ids)}
    for row in branch.itertuples(index=False):
        omega[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = 1.0
    outside = 1.0 - omega
    np.fill_diagonal(outside, 0.0)

    inside_alignment = frobenius_alignment(observed, branch_delta, omega)
    outside_alignment = frobenius_alignment(observed, branch_delta, outside)
    rows = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "StatisticID": "INSIDE_BRANCH_ALIGNMENT",
                "Value": inside_alignment,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "StatisticID": "OUTSIDE_BRANCH_ALIGNMENT",
                "Value": outside_alignment,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    )
    rows.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "InsideAlignment": inside_alignment,
                "OutsideAlignment": outside_alignment,
                "PTauCovScoringAuthorized": True,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    print("P_TAUCOV_EPSILON_P3_ALIGNMENT_SCORECARD_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
