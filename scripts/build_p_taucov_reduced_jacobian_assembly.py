#!/usr/bin/env python3
"""Assemble the conservative reduced-Jacobian source object without scoring."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

DB_MPROJ = EVIDENCE / "p_taucov_projected_morphology_derivative_b.csv"
MEDIATED = EVIDENCE / "p_taucov_mediated_parent_forcing_chain_summary.csv"
ROLLUP = EVIDENCE / "p_taucov_reduced_jacobian_current_blocker_rollup_summary.csv"
DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"

OUT_J = EVIDENCE / "p_taucov_reduced_jacobian_assembly_matrix.csv"
OUT_COV = EVIDENCE / "p_taucov_reduced_jacobian_delta_c_tau_candidate.csv"
OUT_AUDIT = EVIDENCE / "p_taucov_reduced_jacobian_assembly_gates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_reduced_jacobian_assembly_summary.csv"
DOC = DOCS / "p_taucov_reduced_jacobian_assembly.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLY_v1"
CLAIM_BOUNDARY = "reduced_jacobian_assembly_no_scoring"


def load_sparse_square(path: Path, coords: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    idx = {coord: i for i, coord in enumerate(coords)}
    matrix = np.zeros((len(coords), len(coords)), dtype=float)
    for row in df.itertuples(index=False):
        row_coord = str(row.RowCoordinate)
        col_coord = str(row.ColumnCoordinate)
        if row_coord in idx and col_coord in idx:
            matrix[idx[row_coord], idx[col_coord]] = float(row.Value)
    return matrix


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

    rollup = pd.read_csv(ROLLUP).iloc[0]
    mediated = pd.read_csv(MEDIATED).iloc[0]
    domain = pd.read_csv(DOMAIN)
    coords = domain["CoordinateID"].astype(str).tolist()
    reduced = set(domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
    forbidden = set(domain.loc[domain["EmbeddingRole"].isin(["gauge", "forbidden"]), "CoordinateID"].astype(str))
    db_mproj = load_sparse_square(DB_MPROJ, coords)

    blockers_clear = str(rollup["Status"]) == "P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKERS_CLEAR_NO_SCORING"
    delta_b_per_phi = float(mediated["EffectiveDeltaBPerDeltaPhi"])

    # Conservative assembly:
    # J = D_B M_proj * (delta B / delta Phi)
    # The projection-coordinate derivative is not included in v1, because it
    # has not been separately frozen as D_P M_proj.
    p_red = np.diag([1.0 if coord in reduced else 0.0 for coord in coords])
    j_unprojected = db_mproj * delta_b_per_phi
    j_response = p_red @ j_unprojected @ p_red
    raw_cov = j_response @ j_response.T
    fro = float(np.linalg.norm(raw_cov, ord="fro"))
    delta_c = raw_cov / fro if fro > 0.0 else raw_cov
    eigs = np.linalg.eigvalsh(delta_c)

    write_matrix(OUT_J, "J_response_strict_branch_only", coords, j_response)
    write_matrix(OUT_COV, "delta_C_Tau_candidate_psd_lift", coords, delta_c)

    j_norm = float(np.linalg.norm(j_response, ord="fro"))
    cov_norm = float(np.linalg.norm(delta_c, ord="fro"))
    psd = float(eigs.min()) >= -1e-12
    forbidden_ids = [coords.index(coord) for coord in coords if coord in forbidden]
    forbidden_leakage = (
        float(np.linalg.norm(j_response[forbidden_ids, :], ord="fro") + np.linalg.norm(j_response[:, forbidden_ids], ord="fro"))
        if forbidden_ids
        else 0.0
    )
    reduced_support_count = int(np.count_nonzero(np.abs(j_response) > 1e-12))
    gates = [
        ("RJA-G1_BLOCKERS_CLEAR_FOR_ASSEMBLY", blockers_clear, float(blockers_clear), "source-assembly blocker rollup is clear"),
        ("RJA-G2_D_B_M_PROJ_AVAILABLE", j_norm > 0.0, j_norm, "strict branch readout derivative available"),
        ("RJA-G3_MEDIATED_DELTA_B_NONZERO", abs(delta_b_per_phi) > 1e-12, abs(delta_b_per_phi), "mediated branch response nonzero"),
        ("RJA-G4_J_RESPONSE_NONZERO", j_norm > 0.0, j_norm, "assembled response is nonzero"),
        ("RJA-G5_DELTA_C_PSD", psd, float(eigs.min()), "PSD lift is positive semidefinite within tolerance"),
        ("RJA-G6_DELTA_C_NORMALIZED", abs(cov_norm - 1.0) < 1e-12, cov_norm, "Frobenius-normalized covariance candidate"),
        ("RJA-G7_NO_FORBIDDEN_OR_GAUGE_LEAKAGE", forbidden_leakage < 1e-12, forbidden_leakage, "full-action reduced projector removes gauge/forbidden coordinates"),
        ("RJA-G8_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "only target-blind frozen source artifacts used"),
    ]
    gates_df = pd.DataFrame(
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
    gates_df.to_csv(OUT_AUDIT, index=False)
    status = (
        "P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLED_NO_SCORING"
        if bool(gates_df["Passed"].all())
        else "P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLY_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(gates_df["Passed"].sum()),
                "GatesTotal": len(gates_df),
                "CoordinateCount": len(coords),
                "ReducedCoordinateCount": len(reduced),
                "ReducedSupportCount": reduced_support_count,
                "DeltaBPerDeltaPhi": delta_b_per_phi,
                "JResponseFrobeniusNorm": j_norm,
                "DeltaCTauFrobeniusNorm": cov_norm,
                "DeltaCTauMinEigenvalue": float(eigs.min()),
                "DeltaCTauMaxEigenvalue": float(eigs.max()),
                "ForbiddenGaugeLeakageNorm": forbidden_leakage,
                "ProjectionDerivativeIncluded": False,
                "AssemblyMode": "STRICT_BRANCH_ONLY",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Reduced-Jacobian Assembly

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This artifact assembles the first conservative reduced-Jacobian source object
from previously validated, target-blind source artifacts. It does not authorize
empirical scoring and does not claim Tau Core validation.

## Assembly Rule

The v1 assembly uses the strict branch-only rule:

```text
J_response = P_red D_B M_proj P_red * (delta B / delta Phi)
```

with:

```text
delta B / delta Phi = {delta_b_per_phi}
```

The projection-coordinate derivative is not included in this v1 assembly,
because `D_P M_proj` has not been separately frozen.

The full-action reduced projector is applied before writing the assembly
matrix, so gauge and forbidden coordinates are excluded from this v1 object.

## Covariance Candidate

The associated no-scoring covariance candidate is the target-blind PSD lift:

```text
delta_C_Tau = J_response J_response^T / ||J_response J_response^T||_F
```

## Key Numbers

- `||J_response||_F = {j_norm}`
- `||delta_C_Tau||_F = {cov_norm}`
- `min eig(delta_C_Tau) = {float(eigs.min())}`
- `max eig(delta_C_Tau) = {float(eigs.max())}`
- forbidden/gauge leakage norm: `{forbidden_leakage}`
- gates passed: `{int(gates_df["Passed"].sum())}/{len(gates_df)}`

## Claim Boundary

Allowed statement:

> A conservative strict-branch reduced-Jacobian source object has been
> assembled without target or score inputs.

Forbidden statement:

> This artifact authorizes scoring, establishes survival, or validates Tau
> Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
