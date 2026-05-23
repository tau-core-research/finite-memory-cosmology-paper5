#!/usr/bin/env python3
"""Build the target-blind clock/family balance projector for future P-TauCov candidates."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
OUT_MATRIX = ROOT / "evidence/p_taucov_clock_family_balance_projector_matrix.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_clock_family_balance_projector_summary.csv"
OUT_MD = ROOT / "docs/p_taucov_clock_family_balance_projector.md"

AUDIT_ID = "P_TAUCOV_CLOCK_FAMILY_BALANCE_PROJECTOR_v1"
STATUS = "P_TAUCOV_BALANCE_PROJECTOR_FROZEN_NO_CANDIDATE_NO_SCORING"


def load_rows() -> pd.DataFrame:
    spec = importlib.util.spec_from_file_location("p5c_v0", P5C_V0)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load P5C module.")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.load_rows()


def indicator_matrix(labels: list[str]) -> np.ndarray:
    values = sorted(set(labels))
    mat = np.zeros((len(labels), len(values)), dtype=float)
    for i, label in enumerate(labels):
        mat[i, values.index(label)] = 1.0
    return mat


def orthogonal_projector(x: np.ndarray) -> np.ndarray:
    u, s, _ = np.linalg.svd(x, full_matrices=False)
    tol = np.finfo(float).eps * max(x.shape) * float(s[0])
    rank = int(np.sum(s > tol))
    q = u[:, :rank]
    return q @ q.T


def main() -> int:
    rows = load_rows()
    row_ids = rows["RowID"].astype(str).tolist()
    family = rows["FamilyID"].astype(str).tolist()
    clock = rows["ClockBlock"].astype(str).tolist()

    intercept = np.ones((len(rows), 1), dtype=float)
    family_ind = indicator_matrix(family)
    clock_ind = indicator_matrix(clock)
    nuisance = np.concatenate([intercept, family_ind, clock_ind], axis=1)
    p_nuisance = orthogonal_projector(nuisance)
    r_balance = np.eye(len(rows)) - p_nuisance
    r_balance = 0.5 * (r_balance + r_balance.T)

    matrix_rows = []
    for i, rid_i in enumerate(row_ids):
        for j, rid_j in enumerate(row_ids):
            value = float(r_balance[i, j])
            if abs(value) > 1e-14:
                matrix_rows.append(
                    {
                        "AuditID": AUDIT_ID,
                        "RowID": rid_i,
                        "ColumnID": rid_j,
                        "Value": value,
                    }
                )
    pd.DataFrame(matrix_rows).to_csv(OUT_MATRIX, index=False)

    family_leak = float(np.linalg.norm(r_balance @ family_ind, ord="fro"))
    clock_leak = float(np.linalg.norm(r_balance @ clock_ind, ord="fro"))
    intercept_leak = float(np.linalg.norm(r_balance @ intercept, ord="fro"))
    symmetry_error = float(np.linalg.norm(r_balance - r_balance.T, ord="fro"))
    idempotence_error = float(np.linalg.norm(r_balance @ r_balance - r_balance, ord="fro"))
    rank = int(np.linalg.matrix_rank(r_balance))
    trace = float(np.trace(r_balance))

    summary = {
        "AuditID": AUDIT_ID,
        "Status": STATUS,
        "Rows": int(len(rows)),
        "Families": int(len(set(family))),
        "ClockBlocks": int(len(set(clock))),
        "ProjectorRank": rank,
        "ProjectorTrace": trace,
        "SymmetryErrorFrobenius": symmetry_error,
        "IdempotenceErrorFrobenius": idempotence_error,
        "FamilyIndicatorLeakageFrobenius": family_leak,
        "ClockIndicatorLeakageFrobenius": clock_leak,
        "InterceptLeakageFrobenius": intercept_leak,
        "UsesTargetResiduals": False,
        "UsesScoreOutcome": False,
        "CandidateConstructed": False,
        "ScoringAuthorized": False,
        "ClaimBoundary": "target_blind_balance_projector_no_candidate_no_scoring",
    }
    pd.DataFrame([summary]).to_csv(OUT_SUMMARY, index=False)

    md = f"""# P-TauCov Clock/Family Balance Projector

Audit ID: `{AUDIT_ID}`

Status:

`{STATUS}`

## Purpose

The previous diagonal-orthogonal P-TauCov candidate failed because its positive alignment was family-localized and clock-inconsistent. This artifact freezes a target-blind balance projector that can be applied to any future parent-derived response kernel before scoring is authorized.

This is not a candidate and not a scorecard.

## Construction

Let `X` contain only target-blind nuisance directions:

- the intercept;
- registered family indicators;
- frozen clock-block indicators.

The balance projector is:

```text
R_balance = I - X (X^T X)^+ X^T
```

For any future parent-derived kernel `K_parent`, the admissible balanced form must be constructed before scoring as:

```text
K_balanced = R_balance K_parent R_balance
```

Then diagonal leakage must be removed or explicitly excluded by the signed statistic policy.

## Frozen Metrics

```text
Rows = {summary["Rows"]}
Families = {summary["Families"]}
ClockBlocks = {summary["ClockBlocks"]}
ProjectorRank = {summary["ProjectorRank"]}
ProjectorTrace = {summary["ProjectorTrace"]}
SymmetryErrorFrobenius = {summary["SymmetryErrorFrobenius"]}
IdempotenceErrorFrobenius = {summary["IdempotenceErrorFrobenius"]}
FamilyIndicatorLeakageFrobenius = {summary["FamilyIndicatorLeakageFrobenius"]}
ClockIndicatorLeakageFrobenius = {summary["ClockIndicatorLeakageFrobenius"]}
InterceptLeakageFrobenius = {summary["InterceptLeakageFrobenius"]}
```

## Claim Boundary

This artifact authorizes only a preprocessing constraint for future P-TauCov candidate construction.

It does not authorize:

- scoring;
- a new candidate;
- covariance survival;
- Tau Core validation;
- measurement validation.

## Forbidden Use

This projector must not be used to tune a candidate after scoring. It must be applied only to a parent-derived response object that was declared before score access.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
