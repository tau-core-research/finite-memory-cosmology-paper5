#!/usr/bin/env python3
"""Build the strict-linear projected morphology derivative audit."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data" / "p_taucov" / "linear"

A_B = DATA / "A_B.csv"
A_PHI = DATA / "A_Phi.csv"
P0 = DATA / "P0.csv"
BASIS = DATA / "coordinate_basis.csv"

OUT_DB = EVIDENCE / "p_taucov_projected_morphology_derivative_b.csv"
OUT_DPHI = EVIDENCE / "p_taucov_projected_morphology_derivative_phi.csv"
OUT_AUDIT = EVIDENCE / "p_taucov_projected_morphology_derivative_audit.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_projected_morphology_derivative_summary.csv"
DOC = DOCS / "p_taucov_projected_morphology_derivative_audit.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_AUDIT_v1"
CLAIM_BOUNDARY = "projected_morphology_derivative_audit_no_scoring"


def load_square(path: Path) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(path)
    coords = df["coordinate_id"].astype(str).tolist()
    matrix = df.drop(columns=["coordinate_id"]).to_numpy(dtype=float)
    return coords, matrix


def write_matrix(path: Path, matrix_id: str, coords: list[str], matrix: np.ndarray) -> None:
    rows = []
    for i, row_coord in enumerate(coords):
        for j, col_coord in enumerate(coords):
            value = float(matrix[i, j])
            if value != 0.0:
                rows.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "MatrixID": matrix_id,
                        "RowCoordinate": row_coord,
                        "ColumnCoordinate": col_coord,
                        "Value": value,
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    basis = pd.read_csv(BASIS)
    coords = basis["coordinate_id"].astype(str).tolist()
    coords_p0, p0 = load_square(P0)
    coords_ab, a_b = load_square(A_B)
    coords_aphi, a_phi = load_square(A_PHI)
    if coords_p0 != coords or coords_ab != coords or coords_aphi != coords:
        raise RuntimeError("Coordinate order mismatch in linear morphology inputs.")

    d_b_m_proj = p0 @ a_b
    d_phi_m_proj = p0 @ a_phi
    write_matrix(OUT_DB, "D_B_M_proj_strict_linear", coords, d_b_m_proj)
    write_matrix(OUT_DPHI, "D_Phi_M_proj_strict_linear", coords, d_phi_m_proj)

    db_norm = float(np.linalg.norm(d_b_m_proj, ord="fro"))
    dphi_norm = float(np.linalg.norm(d_phi_m_proj, ord="fro"))
    pmorph_row_zero = bool(np.allclose(d_b_m_proj[coords.index("TEMPLATE_P_MORPH_PROJECTION"), :], 0.0))
    morph_row_nonzero = bool(
        np.linalg.norm(d_b_m_proj[coords.index("TEMPLATE_M_PARENT_MORPHOLOGY"), :]) > 1e-12
    )
    gates = [
        ("PMD-G1_A_B_AVAILABLE", A_B.exists(), 1.0, "D_B M_parent source exists"),
        ("PMD-G2_P0_AVAILABLE", P0.exists(), 1.0, "strict-linear projection P0 exists"),
        ("PMD-G3_D_B_M_PROJ_COMPUTABLE", db_norm > 0.0, db_norm, "D_B M_proj = P0 A_B"),
        ("PMD-G4_D_PHI_M_PROJ_COMPUTABLE", dphi_norm > 0.0, dphi_norm, "D_Phi M_proj = P0 A_Phi"),
        ("PMD-G5_STRICT_LINEAR_NO_D_B_P_TERM", pmorph_row_zero, float(pmorph_row_zero), "D_B P_morph term is not used"),
        ("PMD-G6_MORPHOLOGY_ROW_RETAINED", morph_row_nonzero, float(morph_row_nonzero), "morphology carrier survives projection"),
        ("PMD-G7_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "only frozen linear inputs used"),
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
        "P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_PASS_NO_SCORING"
        if bool(audit["Passed"].all())
        else "P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(audit["Passed"].sum()),
                "GatesTotal": len(audit),
                "DBMProjFrobeniusNorm": db_norm,
                "DPhiMProjFrobeniusNorm": dphi_norm,
                "StrictLinearFormula": "D_B_M_proj=P0*A_B;D_Phi_M_proj=P0*A_Phi",
                "DBPmorhTermIncluded": False,
                "ResolvesBlocker": "D_B_M_proj" if status.endswith("PASS_NO_SCORING") else "NONE",
                "StillOpen": "FULL_DYNAMICAL_STABILITY;COVARIANCE_MAP;PHYSICAL_MORPHOLOGY_MODEL",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Projected Morphology Derivative Audit

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This audit resolves whether the strict-linear P-TauCov source packet already
provides the projected morphology derivatives required by the reduced
branch-Jacobian route.

It does not authorize scoring and does not claim a physical morphology model.

## Strict-Linear Rule

With fixed projection `P0` and linear parent morphology maps:

```text
M_parent(Phi,B) = A_Phi Phi + A_B B
```

the projected morphology derivatives are:

```text
D_B M_proj = P0 A_B
D_Phi M_proj = P0 A_Phi
```

The derivative of `P_morph` itself is intentionally excluded in this strict
linear pass:

```text
D_B P_morph = 0
```

## Key Numbers

- `||D_B M_proj||_F = {db_norm}`
- `||D_Phi M_proj||_F = {dphi_norm}`
- gates passed: `{int(audit["Passed"].sum())}/{len(audit)}`

## Claim Boundary

Allowed statement:

> A strict-linear, target-blind projected morphology derivative has been
> computed from frozen `P0`, `A_B`, and `A_Phi`.

Forbidden statement:

> This derivative is a physical morphology model, authorizes scoring, or
> validates Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
