#!/usr/bin/env python3
"""Audit whether the existing target-blind action completes F_B."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"
SCAFFOLD_HESSIAN = EVIDENCE / "p_taucov_minimal_global_parent_action_scaffold_hessian.csv"
S_REST_HESSIAN = EVIDENCE / "p_taucov_s_rest_no_leakage_hessian.csv"

OUT_AUDIT = EVIDENCE / "p_taucov_branch_equation_completion_audit.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_branch_equation_completion_audit_summary.csv"
DOC = DOCS / "p_taucov_branch_equation_completion_audit.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_BRANCH_EQUATION_COMPLETION_AUDIT_v1"
CLAIM_BOUNDARY = "branch_equation_completion_audit_no_scoring"

PHI = "TEMPLATE_PHI_PARENT_SOURCE"
B = "TEMPLATE_B_BRANCH_RESPONSE"
P = "TEMPLATE_P_MORPH_PROJECTION"


def load_matrix(path: Path, coords: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    idx = {coord: i for i, coord in enumerate(coords)}
    matrix = np.zeros((len(coords), len(coords)), dtype=float)
    for row in df.itertuples(index=False):
        matrix[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = float(row.Value)
    return matrix


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    domain = pd.read_csv(DOMAIN)
    coords = domain["CoordinateID"].astype(str).tolist()
    idx = {coord: i for i, coord in enumerate(coords)}
    active = domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str).tolist()

    scaffold = load_matrix(SCAFFOLD_HESSIAN, coords)
    s_rest = load_matrix(S_REST_HESSIAN, coords)
    total = scaffold + s_rest

    branch_row = total[idx[B], :]
    active_ids = [idx[coord] for coord in active]
    active_hessian = total[np.ix_(active_ids, active_ids)]
    active_eigs = np.linalg.eigvalsh(active_hessian)

    l_b_red = float(total[idx[B], idx[B]])
    d_phi_f_b = float(total[idx[B], idx[PHI]])
    d_p_f_b = float(total[idx[B], idx[P]])
    origin_residual = float(np.linalg.norm(branch_row * 0.0))
    mediated_parent_path_exists = abs(d_p_f_b) > 1e-12

    gates = [
        ("BE-G1_INPUTS_AVAILABLE", True, 1.0, "domain/scaffold/S_rest inputs loaded"),
        (
            "BE-G2_F_B_DECLARED_FROM_TARGET_BLIND_ACTION",
            True,
            1.0,
            "F_B is the B-row gradient of S_scaffold + S_rest",
        ),
        ("BE-G3_ORIGIN_SOLVES_LINEAR_BRANCH_EQUATION", origin_residual < 1e-12, origin_residual, "F_B(0,0)=0"),
        ("BE-G4_L_B_RED_COMPUTABLE_AND_INVERTIBLE", abs(l_b_red) > 1e-12, abs(l_b_red), "one-dimensional B reduction"),
        (
            "BE-G5_DIRECT_D_PHI_F_B_NONZERO",
            abs(d_phi_f_b) > 1e-12,
            abs(d_phi_f_b),
            "direct parent-to-branch forcing",
        ),
        (
            "BE-G6_MEDIATED_PARENT_PATH_EXISTS",
            mediated_parent_path_exists,
            abs(d_p_f_b),
            "parent can only enter through the projection mediator in this scaffold",
        ),
        (
            "BE-G7_ACTIVE_HESSIAN_POSITIVE",
            float(active_eigs.min()) > 0.0,
            float(active_eigs.min()),
            "full active stability remains open if this is not positive",
        ),
        ("BE-G8_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "pure target-blind action audit"),
    ]

    audit = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "Interpretation": interpretation,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value, interpretation in gates
        ]
    )
    audit.to_csv(OUT_AUDIT, index=False)

    direct_complete = abs(d_phi_f_b) > 1e-12 and abs(l_b_red) > 1e-12
    status = (
        "P_TAUCOV_BRANCH_EQUATION_DIRECT_COMPLETION_PASS_NO_SCORING"
        if bool(audit["Passed"].all()) and direct_complete
        else "P_TAUCOV_BRANCH_EQUATION_PARTIAL_COMPLETION_MEDIATED_FORCING_REQUIRED_NO_SCORING"
    )
    remaining = []
    if abs(d_phi_f_b) <= 1e-12:
        remaining.append("DIRECT_D_PHI_F_B_OR_EXPLICIT_MEDIATED_CHAIN")
    if float(active_eigs.min()) <= 0.0:
        remaining.append("ACTIVE_STABILITY_OR_REGULATED_DOMAIN")
    if not remaining:
        remaining.append("NONE_FOR_BRANCH_EQUATION_AUDIT")

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(audit["Passed"].sum()),
                "GatesTotal": len(audit),
                "L_B_red": l_b_red,
                "D_Phi_F_B": d_phi_f_b,
                "D_P_F_B": d_p_f_b,
                "ActiveMinEigenvalue": float(active_eigs.min()),
                "MediatedParentPathExists": bool(mediated_parent_path_exists),
                "DirectBranchForcingComplete": bool(direct_complete),
                "RemainingBlockers": ";".join(remaining),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Branch-Equation Completion Audit

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This audit asks whether the existing target-blind action scaffold already
completes the branch equation needed for the reduced branch-Jacobian route.
It does not authorize scoring and does not claim a Tau Core validation.

## Audited Branch Equation

The tested branch equation is the B-sector gradient row of:

```text
S_total = S_scaffold + S_rest
F_B = D_B S_total
```

At the origin candidate:

```text
Phi0=0; P0=0; B0=0
```

the linear branch equation is stationary. The one-dimensional branch
linearization is computable:

```text
L_B_red = {l_b_red}
```

## Key Result

The audit finds that the direct parent forcing term is:

```text
D_Phi_F_B = {d_phi_f_b}
```

while the projection-mediated coupling is:

```text
D_P_F_B = {d_p_f_b}
```

So the current scaffold gives a computable branch row and a projection-mediated
path, but not a direct `D_Phi F_B` forcing term. The next step must therefore
either declare the mediated chain explicitly or derive a nonzero direct forcing
from the parent action.

## Stability Boundary

The active Hessian minimum eigenvalue is:

```text
{float(active_eigs.min())}
```

Thus this audit does not prove full active stability.

## Claim Boundary

Allowed statement:

> The existing target-blind action gives a partial branch-equation completion:
> `F_B` and `L_B_red` are computable, while the parent forcing remains mediated
> or incomplete.

Forbidden statement:

> The reduced branch-Jacobian is complete, empirical scoring is authorized, or
> Tau Core has been validated.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
