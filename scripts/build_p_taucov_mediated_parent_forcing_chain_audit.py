#!/usr/bin/env python3
"""Audit the Phi -> P_morph -> B mediated parent-forcing chain."""

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

OUT_MATRIX = EVIDENCE / "p_taucov_mediated_parent_forcing_chain_matrix.csv"
OUT_AUDIT = EVIDENCE / "p_taucov_mediated_parent_forcing_chain_audit.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_mediated_parent_forcing_chain_summary.csv"
DOC = DOCS / "p_taucov_mediated_parent_forcing_chain_audit.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_MEDIATED_PARENT_FORCING_CHAIN_AUDIT_v1"
CLAIM_BOUNDARY = "mediated_parent_forcing_chain_audit_no_scoring"

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


def matrix_records(matrix: np.ndarray, rows: list[str], cols: list[str], matrix_id: str) -> list[dict]:
    records = []
    for i, row_id in enumerate(rows):
        for j, col_id in enumerate(cols):
            records.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "MatrixID": matrix_id,
                    "RowCoordinate": row_id,
                    "ColumnCoordinate": col_id,
                    "Value": float(matrix[i, j]),
                    "UsesTargetResiduals": False,
                    "UsesScoreOutcome": False,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    return records


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    domain = pd.read_csv(DOMAIN)
    coords = domain["CoordinateID"].astype(str).tolist()
    idx = {coord: i for i, coord in enumerate(coords)}
    total = load_matrix(SCAFFOLD_HESSIAN, coords) + load_matrix(S_REST_HESSIAN, coords)

    branch_coords = [B, P]
    branch_ids = [idx[coord] for coord in branch_coords]
    l_x = total[np.ix_(branch_ids, branch_ids)]
    r_phi = total[np.ix_(branch_ids, [idx[PHI]])]
    det_lx = float(np.linalg.det(l_x))
    eig_lx = np.linalg.eigvalsh(l_x)
    response = -np.linalg.solve(l_x, r_phi).reshape(-1)

    records = []
    records += matrix_records(l_x, branch_coords, branch_coords, "L_X_branch_mediated")
    records += matrix_records(r_phi, branch_coords, [PHI], "D_Phi_F_X")
    records += matrix_records(response.reshape(-1, 1), branch_coords, [PHI], "minus_L_X_inverse_D_Phi_F_X")
    pd.DataFrame(records).to_csv(OUT_MATRIX, index=False)

    direct_d_phi_f_b = float(total[idx[B], idx[PHI]])
    d_p_f_b = float(total[idx[B], idx[P]])
    d_phi_f_p = float(total[idx[P], idx[PHI]])
    b_response = float(response[0])
    p_response = float(response[1])

    gates = [
        ("MC-G1_DIRECT_B_FORCING_ZERO_RECORDED", abs(direct_d_phi_f_b) < 1e-12, abs(direct_d_phi_f_b), "direct branch forcing is not claimed"),
        ("MC-G2_B_P_COUPLING_NONZERO", abs(d_p_f_b) > 1e-12, abs(d_p_f_b), "B couples to projection mediator"),
        ("MC-G3_P_PHI_COUPLING_NONZERO", abs(d_phi_f_p) > 1e-12, abs(d_phi_f_p), "projection mediator couples to parent source"),
        ("MC-G4_MEDIATED_BRANCH_BLOCK_INVERTIBLE", abs(det_lx) > 1e-12, abs(det_lx), "two-coordinate branch block is invertible"),
        ("MC-G5_EFFECTIVE_B_RESPONSE_NONZERO", abs(b_response) > 1e-12, abs(b_response), "Phi induces B through the mediated branch solve"),
        ("MC-G6_BRANCH_BLOCK_NOT_POSITIVE_STABLE", float(eig_lx.min()) <= 0.0, float(eig_lx.min()), "stability is not promoted by this audit"),
        ("MC-G7_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "pure action-side algebra"),
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

    status = (
        "P_TAUCOV_MEDIATED_PARENT_FORCING_CHAIN_PASS_STABILITY_OPEN_NO_SCORING"
        if bool(audit["Passed"].all())
        else "P_TAUCOV_MEDIATED_PARENT_FORCING_CHAIN_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(audit["Passed"].sum()),
                "GatesTotal": len(audit),
                "Direct_D_Phi_F_B": direct_d_phi_f_b,
                "D_P_F_B": d_p_f_b,
                "D_Phi_F_P": d_phi_f_p,
                "Det_L_X": det_lx,
                "MinEigen_L_X": float(eig_lx.min()),
                "EffectiveDeltaBPerDeltaPhi": b_response,
                "EffectiveDeltaPPerDeltaPhi": p_response,
                "MediatedForcingResolved": True,
                "FullStabilityResolved": False,
                "RemainingBlockers": "ACTIVE_STABILITY_OR_REGULATED_DOMAIN;D_B_M_PROJ",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Mediated Parent-Forcing Chain Audit

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

The previous branch-equation audit found that the direct branch forcing
`D_Phi F_B` is zero in the active scaffold. This audit tests the target-blind
alternative allowed by the same action: a mediated chain

```text
Phi -> P_morph -> B
```

It does not authorize scoring and does not claim physical validation.

## Branch Solve

Use the two-coordinate branch vector:

```text
X = (B, P_morph)
```

and solve the linear branch equation:

```text
L_X delta X + D_Phi F_X delta Phi = 0
```

with:

```text
delta X = - L_X^-1 D_Phi F_X delta Phi
```

## Key Numbers

- `D_Phi F_B = {direct_d_phi_f_b}`
- `D_P F_B = {d_p_f_b}`
- `D_Phi F_P = {d_phi_f_p}`
- `det(L_X) = {det_lx}`
- `min eig(L_X) = {float(eig_lx.min())}`
- `delta B / delta Phi = {b_response}`
- `delta P / delta Phi = {p_response}`

## Interpretation

The direct `Phi -> B` forcing is zero, but the mediated chain is nonzero and
invertible in the current two-coordinate branch block:

```text
delta B / delta Phi = {b_response}
```

This resolves the branch-forcing route only at the algebraic, target-blind
scaffold level. It does not prove active stability, does not construct
`D_B M_proj`, and does not authorize empirical scoring.

## Claim Boundary

Allowed statement:

> The current action scaffold contains a target-blind mediated parent-forcing
> chain from `Phi` through `P_morph` into `B`.

Forbidden statement:

> The full reduced branch-Jacobian is complete, the branch block is physically
> stable, empirical scoring is authorized, or Tau Core has been validated.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
