#!/usr/bin/env python3
"""Freeze a target-blind D_P M_proj source spec for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"
GATE_SUMMARY = EVIDENCE / "p_taucov_projection_morphology_coupling_gate_summary.csv"
MEDIATED_SUMMARY = EVIDENCE / "p_taucov_mediated_parent_forcing_chain_summary.csv"

OUT_MATRIX = EVIDENCE / "p_taucov_d_p_mproj_source_spec_matrix.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_d_p_mproj_source_spec_summary.csv"
OUT_AUDIT = EVIDENCE / "p_taucov_d_p_mproj_source_spec_audit.csv"
DOC = DOCS / "p_taucov_d_p_mproj_source_spec.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_v1"
CLAIM_BOUNDARY = "d_p_mproj_source_spec_no_scoring"

BRANCH = "TEMPLATE_B_BRANCH_RESPONSE"
PROJECTION = "TEMPLATE_P_MORPH_PROJECTION"
FORBIDDEN_MORPH = "TEMPLATE_M_PARENT_MORPHOLOGY"


def write_sparse_matrix(path: Path, coords: list[str], matrix: np.ndarray) -> None:
    rows = []
    for i, row_coord in enumerate(coords):
        for j, col_coord in enumerate(coords):
            value = float(matrix[i, j])
            if abs(value) > 0.0:
                rows.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "MatrixID": "D_P_M_proj_minimal_branch_projection_coupling",
                        "RowCoordinate": row_coord,
                        "ColumnCoordinate": col_coord,
                        "Value": value,
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ObjectConstructionAuthorized": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    domain = pd.read_csv(DOMAIN)
    gate = pd.read_csv(GATE_SUMMARY).iloc[0]
    mediated = pd.read_csv(MEDIATED_SUMMARY).iloc[0]
    coords = domain["CoordinateID"].astype(str).tolist()
    idx = {coord: i for i, coord in enumerate(coords)}
    reduced = set(domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
    forbidden = set(domain.loc[domain["EmbeddingRole"].isin(["gauge", "forbidden"]), "CoordinateID"].astype(str))

    matrix = np.zeros((len(coords), len(coords)), dtype=float)
    amp = 1.0 / np.sqrt(2.0)
    matrix[idx[BRANCH], idx[PROJECTION]] = amp
    matrix[idx[PROJECTION], idx[BRANCH]] = amp
    write_sparse_matrix(OUT_MATRIX, coords, matrix)

    fro = float(np.linalg.norm(matrix, ord="fro"))
    diagonal_share = 0.0 if fro == 0.0 else float(np.linalg.norm(np.diag(np.diag(matrix)), ord="fro") / fro)
    p_projector = np.zeros_like(matrix)
    p_projector[idx[PROJECTION], idx[PROJECTION]] = 1.0
    comm = p_projector @ matrix - matrix @ p_projector
    comm_share = 0.0 if fro == 0.0 else float(np.linalg.norm(comm, ord="fro") / fro)
    active_ids = [idx[c] for c in coords if c in reduced]
    forbidden_ids = [idx[c] for c in coords if c in forbidden]
    reduced_norm = float(np.linalg.norm(matrix[np.ix_(active_ids, active_ids)], ord="fro"))
    forbidden_leakage = (
        float(np.linalg.norm(matrix[forbidden_ids, :], ord="fro") + np.linalg.norm(matrix[:, forbidden_ids], ord="fro"))
        if forbidden_ids
        else 0.0
    )
    projection_support = float(
        np.linalg.norm(matrix[idx[PROJECTION], :], ord=2) + np.linalg.norm(matrix[:, idx[PROJECTION]], ord=2)
    )
    branch_support = float(
        np.linalg.norm(matrix[idx[BRANCH], :], ord=2) + np.linalg.norm(matrix[:, idx[BRANCH]], ord=2)
    )

    gates = [
        (
            "DPM-G1_COUPLING_GATE_READY",
            str(gate["Status"]) == "P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_READY_NO_OBJECT_NO_SCORING",
            1.0,
            "projection/morphology coupling gate is ready",
        ),
        (
            "DPM-G2_MEDIATED_CHAIN_NONZERO",
            bool(mediated["MediatedForcingResolved"]),
            float(abs(float(mediated["EffectiveDeltaPPerDeltaPhi"]))),
            "mediated Phi -> P_morph -> B chain is nonzero",
        ),
        (
            "DPM-G3_ACTIVE_BRANCH_PROJECTION_SUPPORT",
            BRANCH in reduced and PROJECTION in reduced,
            1.0,
            "branch and projection coordinates are active in the reduced domain",
        ),
        (
            "DPM-G4_NO_FORBIDDEN_M_PARENT_LEAKAGE",
            forbidden_leakage < 1e-12,
            forbidden_leakage,
            "direct forbidden M_parent support is absent",
        ),
        (
            "DPM-G5_NONDIAGONAL_SOURCE",
            diagonal_share == 0.0,
            diagonal_share,
            "source derivative is not diagonal-only",
        ),
        (
            "DPM-G6_NONCOMMUTING_WITH_ACTIVE_PMORPH",
            comm_share >= 0.50,
            comm_share,
            "source derivative does not commute with the active projection readout",
        ),
        (
            "DPM-G7_PROJECTION_SUPPORT_PRESENT",
            projection_support > 0.0,
            projection_support,
            "source derivative explicitly touches TEMPLATE_P_MORPH_PROJECTION",
        ),
        (
            "DPM-G8_BRANCH_SUPPORT_PRESENT",
            branch_support > 0.0,
            branch_support,
            "source derivative explicitly touches TEMPLATE_B_BRANCH_RESPONSE",
        ),
        (
            "DPM-G9_NO_TARGET_OR_SCORE_INPUTS",
            True,
            1.0,
            "only frozen source/gate artifacts are used",
        ),
    ]
    audit = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "MetricValue": float(value),
                "Interpretation": interpretation,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value, interpretation in gates
        ]
    )
    audit.to_csv(OUT_AUDIT, index=False)
    status = (
        "P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_FROZEN_NO_OBJECT_NO_SCORING"
        if bool(audit["Passed"].all())
        else "P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_BLOCKED_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(audit["Passed"].sum()),
                "GatesTotal": len(audit),
                "SourceMatrix": OUT_MATRIX.name,
                "SourceFormula": "symmetric active branch/projection coupling, amplitude=1/sqrt(2)",
                "FrobeniusNorm": fro,
                "DiagonalEnergyShare": diagonal_share,
                "ActiveProjectionCommutatorShare": comm_share,
                "ReducedDomainNorm": reduced_norm,
                "ForbiddenGaugeLeakageNorm": forbidden_leakage,
                "ProjectionSupportNorm": projection_support,
                "BranchSupportNorm": branch_support,
                "DerivativeSourceFrozen": status.endswith("NO_OBJECT_NO_SCORING"),
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov D_P M_proj Source Spec

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

The strict branch-only reduced-Jacobian candidate failed because it had no
explicit projection/morphology channel. This source spec freezes the minimal
target-blind projection derivative needed for the next assembly attempt.

It is not a new `delta_C_Tau` candidate and does not authorize scoring.

## Source Rule

The frozen derivative source is the minimal symmetric active coupling between
the branch response coordinate and the projected morphology coordinate:

```text
D_P M_proj(B, P) =
  ( |B><P| + |P><B| ) / sqrt(2)
```

where:

```text
B = TEMPLATE_B_BRANCH_RESPONSE
P = TEMPLATE_P_MORPH_PROJECTION
```

Direct `TEMPLATE_M_PARENT_MORPHOLOGY` support remains forbidden in the reduced
object. The parent morphology axis may motivate the route, but it is not
allowed to leak into the scoreable reduced coordinate object.

## Key Diagnostics

- Frobenius norm: `{fro}`
- diagonal energy share: `{diagonal_share}`
- active `P_morph` commutator share: `{comm_share}`
- reduced-domain norm: `{reduced_norm}`
- forbidden/gauge leakage norm: `{forbidden_leakage}`
- gates passed: `{int(audit["Passed"].sum())}/{len(audit)}`

## Claim Boundary

Allowed statement:

> A target-blind `D_P M_proj` source derivative has been frozen for the next
> P-TauCov assembly attempt.

Forbidden statement:

> This derivative constructs a new covariance candidate, authorizes scoring,
> survives a Tau-specific test, or validates Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
