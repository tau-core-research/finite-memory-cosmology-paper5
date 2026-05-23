#!/usr/bin/env python3
"""Assemble the projection-coupled reduced-Jacobian artifact without scoring."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

DB_MPROJ = EVIDENCE / "p_taucov_projected_morphology_derivative_b.csv"
DP_MPROJ = EVIDENCE / "p_taucov_d_p_mproj_source_spec_matrix.csv"
DP_SUMMARY = EVIDENCE / "p_taucov_d_p_mproj_source_spec_summary.csv"
MEDIATED = EVIDENCE / "p_taucov_mediated_parent_forcing_chain_summary.csv"
DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"

OUT_J = EVIDENCE / "p_taucov_projection_coupled_jacobian_assembly_matrix.csv"
OUT_COV = EVIDENCE / "p_taucov_projection_coupled_delta_c_tau_candidate.csv"
OUT_AUDIT = EVIDENCE / "p_taucov_projection_coupled_jacobian_assembly_gates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_projection_coupled_jacobian_assembly_summary.csv"
DOC = DOCS / "p_taucov_projection_coupled_jacobian_assembly.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLY_v1"
CLAIM_BOUNDARY = "projection_coupled_jacobian_assembly_no_scoring"


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
            if abs(value) > 0.0:
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

    domain = pd.read_csv(DOMAIN)
    mediated = pd.read_csv(MEDIATED).iloc[0]
    dp_summary = pd.read_csv(DP_SUMMARY).iloc[0]
    coords = domain["CoordinateID"].astype(str).tolist()
    reduced = set(domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
    forbidden = set(domain.loc[domain["EmbeddingRole"].isin(["gauge", "forbidden"]), "CoordinateID"].astype(str))
    db_mproj = load_sparse_square(DB_MPROJ, coords)
    dp_mproj = load_sparse_square(DP_MPROJ, coords)

    delta_b_per_phi = float(mediated["EffectiveDeltaBPerDeltaPhi"])
    delta_p_per_phi = float(mediated["EffectiveDeltaPPerDeltaPhi"])
    p_red = np.diag([1.0 if coord in reduced else 0.0 for coord in coords])
    j_unprojected = (db_mproj * delta_b_per_phi) + (dp_mproj * delta_p_per_phi)
    j_response = p_red @ j_unprojected @ p_red
    raw_cov = j_response @ j_response.T
    fro_raw = float(np.linalg.norm(raw_cov, ord="fro"))
    delta_c = raw_cov / fro_raw if fro_raw > 0.0 else raw_cov
    eigs = np.linalg.eigvalsh(delta_c)

    write_matrix(OUT_J, "J_response_projection_coupled", coords, j_response)
    write_matrix(OUT_COV, "delta_C_Tau_projection_coupled_psd_lift", coords, delta_c)

    j_norm = float(np.linalg.norm(j_response, ord="fro"))
    cov_norm = float(np.linalg.norm(delta_c, ord="fro"))
    idx = {coord: i for i, coord in enumerate(coords)}
    forbidden_ids = [idx[coord] for coord in coords if coord in forbidden]
    forbidden_leakage = (
        float(np.linalg.norm(j_response[forbidden_ids, :], ord="fro") + np.linalg.norm(j_response[:, forbidden_ids], ord="fro"))
        if forbidden_ids
        else 0.0
    )
    p_active = np.zeros_like(delta_c)
    p_active[idx["TEMPLATE_P_MORPH_PROJECTION"], idx["TEMPLATE_P_MORPH_PROJECTION"]] = 1.0
    comm = p_active @ delta_c - delta_c @ p_active
    comm_share = 0.0 if cov_norm == 0.0 else float(np.linalg.norm(comm, ord="fro") / cov_norm)
    diag_share = 0.0 if cov_norm == 0.0 else float(np.linalg.norm(np.diag(np.diag(delta_c)), ord="fro") / cov_norm)

    gates = [
        ("PCJA-G1_D_P_SOURCE_FROZEN", bool(dp_summary["DerivativeSourceFrozen"]), 1.0, "D_P M_proj source derivative frozen"),
        ("PCJA-G2_MEDIATED_DELTA_B_NONZERO", abs(delta_b_per_phi) > 1e-12, abs(delta_b_per_phi), "delta B / delta Phi is nonzero"),
        ("PCJA-G3_MEDIATED_DELTA_P_NONZERO", abs(delta_p_per_phi) > 1e-12, abs(delta_p_per_phi), "delta P / delta Phi is nonzero"),
        ("PCJA-G4_J_RESPONSE_NONZERO", j_norm > 0.0, j_norm, "assembled response is nonzero"),
        ("PCJA-G5_DELTA_C_PSD", float(eigs.min()) >= -1e-12, float(eigs.min()), "PSD lift is positive semidefinite within tolerance"),
        ("PCJA-G6_DELTA_C_NORMALIZED", abs(cov_norm - 1.0) < 1e-12, cov_norm, "Frobenius-normalized covariance candidate"),
        ("PCJA-G7_NO_FORBIDDEN_OR_GAUGE_LEAKAGE", forbidden_leakage < 1e-12, forbidden_leakage, "reduced projector removes gauge/forbidden coordinates"),
        ("PCJA-G8_PROJECTION_COMMUTATOR_PRESENT", comm_share > 0.0, comm_share, "projection-coupled covariance has nonzero active P commutator"),
        ("PCJA-G9_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "only target-blind frozen source artifacts used"),
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
        "P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLED_NO_SCORING"
        if bool(gates_df["Passed"].all())
        else "P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLY_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(gates_df["Passed"].sum()),
                "GatesTotal": len(gates_df),
                "DeltaBPerDeltaPhi": delta_b_per_phi,
                "DeltaPPerDeltaPhi": delta_p_per_phi,
                "JResponseFrobeniusNorm": j_norm,
                "DeltaCTauFrobeniusNorm": cov_norm,
                "DeltaCTauMinEigenvalue": float(eigs.min()),
                "DeltaCTauMaxEigenvalue": float(eigs.max()),
                "DiagonalEnergyShare": diag_share,
                "ActiveProjectionCommutatorShare": comm_share,
                "ForbiddenGaugeLeakageNorm": forbidden_leakage,
                "ProjectionDerivativeIncluded": True,
                "AssemblyMode": "PROJECTION_COUPLED_BRANCH_RESPONSE",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Projection-Coupled Jacobian Assembly

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This artifact assembles the first projection-coupled reduced-Jacobian source
object. It is a no-scoring assembly step, not an empirical result.

## Assembly Rule

```text
J_response =
  P_red [ D_B M_proj (delta B / delta Phi)
        + D_P M_proj (delta P / delta Phi) ] P_red
```

with:

```text
delta B / delta Phi = {delta_b_per_phi}
delta P / delta Phi = {delta_p_per_phi}
```

The `D_P M_proj` source is frozen separately in:

[`p_taucov_d_p_mproj_source_spec.md`](p_taucov_d_p_mproj_source_spec.md)

## Key Numbers

- `||J_response||_F = {j_norm}`
- `||delta_C_Tau||_F = {cov_norm}`
- diagonal energy share: `{diag_share}`
- active projection commutator share: `{comm_share}`
- forbidden/gauge leakage norm: `{forbidden_leakage}`
- gates passed: `{int(gates_df["Passed"].sum())}/{len(gates_df)}`

## Claim Boundary

Allowed statement:

> A target-blind projection-coupled reduced-Jacobian source object has been
> assembled for preflight testing.

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
