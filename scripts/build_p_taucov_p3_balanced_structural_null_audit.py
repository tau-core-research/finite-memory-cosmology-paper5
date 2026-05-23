#!/usr/bin/env python3
"""Build a target-blind structural null audit for the frozen P3 balanced object."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "evidence/p_taucov_p3_balanced_preflight_matrix.csv"
ROWS_SOURCE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
OUT_NULLS = ROOT / "evidence/p_taucov_p3_balanced_structural_null_audit.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_structural_null_audit_summary.csv"
OUT_MD = ROOT / "docs/p_taucov_p3_balanced_structural_null_audit.md"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_v1"
STATUS_PASS = "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_PASS_NO_SCORING"
STATUS_FAIL = "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_FAIL_NO_SCORING"


def read_kernel(path: Path) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    ids = sorted(set(df["RowID"].astype(str)) | set(df["ColumnID"].astype(str)))
    idx = {rid: i for i, rid in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowID)], idx[str(row.ColumnID)]] = float(row.Value)
    return ids, normalize(0.5 * (mat + mat.T))


def normalize(mat: np.ndarray) -> np.ndarray:
    mat = 0.5 * (mat + mat.T)
    fro = float(np.linalg.norm(mat, ord="fro"))
    if fro == 0.0:
        return mat
    return mat / fro


def corr(a: np.ndarray, b: np.ndarray) -> float:
    af = a.reshape(-1)
    bf = b.reshape(-1)
    denom = float(np.linalg.norm(af) * np.linalg.norm(bf))
    return 0.0 if denom == 0.0 else float(np.dot(af, bf) / denom)


def row_metadata(row_ids: list[str]) -> pd.DataFrame:
    raw = pd.read_csv(ROWS_SOURCE)
    meta = raw[["EmpiricalIndex", "EmpiricalRowID", "FamilyID", "ClockIndex"]].drop_duplicates()
    meta = meta.sort_values("EmpiricalIndex")
    by_id = {str(row.EmpiricalRowID): row for row in meta.itertuples(index=False)}
    rows = []
    for rid in row_ids:
        row = by_id[rid]
        rows.append({"RowID": rid, "FamilyID": str(row.FamilyID), "ClockIndex": int(row.ClockIndex)})
    return pd.DataFrame(rows)


def permute(mat: np.ndarray, order: np.ndarray) -> np.ndarray:
    return normalize(mat[np.ix_(order, order)])


def block_permutation(meta: pd.DataFrame, key: str, shift: int = 1) -> np.ndarray:
    labels = sorted(meta[key].unique())
    shifted = {label: labels[(i + shift) % len(labels)] for i, label in enumerate(labels)}
    target_labels = meta[key].map(shifted).tolist()
    order = []
    used: set[int] = set()
    for label in target_labels:
        candidates = [i for i, value in enumerate(meta[key].tolist()) if value == label and i not in used]
        if not candidates:
            candidates = [i for i, value in enumerate(meta[key].tolist()) if value == label]
        choice = candidates[0]
        used.add(choice)
        order.append(choice)
    return np.array(order, dtype=int)


def random_symmetric_nulls(n: int, count: int = 64) -> list[np.ndarray]:
    rng = np.random.default_rng(20260523)
    out = []
    for _ in range(count):
        raw = rng.normal(size=(n, n))
        sym = 0.5 * (raw + raw.T)
        np.fill_diagonal(sym, 0.0)
        out.append(normalize(sym))
    return out


def main() -> int:
    row_ids, kernel = read_kernel(KERNEL)
    meta = row_metadata(row_ids)
    n = len(row_ids)

    nulls: dict[str, tuple[np.ndarray, str]] = {
        "SIGN_FLIP": (-kernel, "orientation_control_signed_not_abs_gate"),
        "ROW_REVERSE": (permute(kernel, np.arange(n - 1, -1, -1)), "structured_permutation"),
        "CLOCK_PHASE_SHIFT": (permute(kernel, np.roll(np.arange(n), 1)), "structured_permutation"),
        "FAMILY_CYCLE": (permute(kernel, block_permutation(meta, "FamilyID", 1)), "structured_permutation"),
    }
    rng = np.random.default_rng(20260523)
    nulls["SUPPORT_SHUFFLE"] = (permute(kernel, rng.permutation(n)), "structured_permutation")

    rows = []
    for null_id, (mat, null_class) in nulls.items():
        rows.append(
            {
                "AuditID": AUDIT_ID,
                "NullID": null_id,
                "CorrelationWithP3Balanced": corr(kernel, mat),
                "AbsCorrelationWithP3Balanced": abs(corr(kernel, mat)),
                "NullClass": null_class,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
            }
        )
    random_corrs = [corr(kernel, mat) for mat in random_symmetric_nulls(n)]
    rows.append(
        {
            "AuditID": AUDIT_ID,
            "NullID": "RANDOM_SYMMETRIC_OFFDIAGONAL_MEDIAN",
            "CorrelationWithP3Balanced": float(np.median(random_corrs)),
            "AbsCorrelationWithP3Balanced": float(np.median(np.abs(random_corrs))),
            "NullClass": "random_symmetric_offdiagonal_64_median",
            "UsesTargetResiduals": False,
            "UsesScoreOutcome": False,
            "ScoringAuthorized": False,
        }
    )
    rows.append(
        {
            "AuditID": AUDIT_ID,
            "NullID": "RANDOM_SYMMETRIC_OFFDIAGONAL_MAXABS",
            "CorrelationWithP3Balanced": float(random_corrs[int(np.argmax(np.abs(random_corrs)))]),
            "AbsCorrelationWithP3Balanced": float(np.max(np.abs(random_corrs))),
            "NullClass": "random_symmetric_offdiagonal_64_maxabs",
            "UsesTargetResiduals": False,
            "UsesScoreOutcome": False,
            "ScoringAuthorized": False,
        }
    )
    table = pd.DataFrame(rows)
    table.to_csv(OUT_NULLS, index=False)

    structured = table[table["NullClass"].eq("structured_permutation")]
    sign_flip_corr = float(table[table["NullID"].eq("SIGN_FLIP")]["CorrelationWithP3Balanced"].iloc[0])
    max_structured_abs = float(structured["AbsCorrelationWithP3Balanced"].max())
    random_median_abs = float(table[table["NullID"].eq("RANDOM_SYMMETRIC_OFFDIAGONAL_MEDIAN")]["AbsCorrelationWithP3Balanced"].iloc[0])
    random_max_abs = float(table[table["NullID"].eq("RANDOM_SYMMETRIC_OFFDIAGONAL_MAXABS")]["AbsCorrelationWithP3Balanced"].iloc[0])
    pass_gate = bool(sign_flip_corr < 0.0 and max_structured_abs < 0.95 and random_median_abs < 0.25)
    status = STATUS_PASS if pass_gate else STATUS_FAIL
    pd.DataFrame(
        [
            {
                "AuditID": AUDIT_ID,
                "Status": status,
                "StructuredNullCount": int(len(structured)),
                "SignFlipCorrelation": sign_flip_corr,
                "MaxStructuredAbsCorrelation": max_structured_abs,
                "RandomMedianAbsCorrelation": random_median_abs,
                "RandomMaxAbsCorrelation": random_max_abs,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": "p3_balanced_structural_null_audit_no_scoring",
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)

    md = f"""# P-TauCov P3 Balanced Structural Null Audit

Audit ID: `{AUDIT_ID}`

Status:

`{status}`

## Purpose

This audit checks whether the frozen P3 balanced object is merely a row-order, clock-shift, family-cycle, support-shuffle, or random symmetric off-diagonal pattern.

The sign flip is tracked separately as an orientation control. It is not included in the absolute structured-null maximum because every signed kernel has absolute correlation one with its own negative.

It uses no target residuals and authorizes no empirical scoring.

## Summary Metrics

```text
SignFlipCorrelation = {sign_flip_corr}
MaxStructuredAbsCorrelation = {max_structured_abs}
RandomMedianAbsCorrelation = {random_median_abs}
RandomMaxAbsCorrelation = {random_max_abs}
```

## Interpretation

Passing this audit means only that the frozen P3 balanced object is structurally nontrivial relative to the declared target-blind nulls.

It does not mean that the object predicts data, survives a scorecard, or validates Tau Core.

## Claim Boundary

Allowed statement:

> The frozen P3 balanced object is not identical to the declared structural null patterns and remains eligible for later protocol design.

Forbidden statement:

> The structural null audit establishes a Tau signal or empirical survival.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
