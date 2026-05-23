#!/usr/bin/env python3
"""Build current reduced-Jacobian blocker rollup after latest audits."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

MEDIATED = EVIDENCE / "p_taucov_mediated_parent_forcing_chain_summary.csv"
DBM = EVIDENCE / "p_taucov_projected_morphology_derivative_summary.csv"
RESPONSE_ENERGY = EVIDENCE / "p_taucov_response_energy_split_summary.csv"
REFERENCE = EVIDENCE / "p_taucov_reference_state_candidate_spec_summary.csv"
COVARIANCE_MAP = EVIDENCE / "p_taucov_covariance_map_summary.csv"
REFERENCE_RECONCILIATION = EVIDENCE / "p_taucov_reference_state_status_reconciliation_summary.csv"

OUT = EVIDENCE / "p_taucov_reduced_jacobian_current_blocker_rollup.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_reduced_jacobian_current_blocker_rollup_summary.csv"
DOC = DOCS / "p_taucov_reduced_jacobian_current_blocker_rollup.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKER_ROLLUP_v1"
CLAIM_BOUNDARY = "reduced_jacobian_current_blocker_rollup_no_scoring"


def status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    return str(pd.read_csv(path).iloc[0]["Status"])


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    mediated_status = status(MEDIATED)
    dbm_status = status(DBM)
    response_energy_status = status(RESPONSE_ENERGY)
    reference_status = status(REFERENCE)
    covariance_map_status = status(COVARIANCE_MAP)
    reference_reconciliation = pd.read_csv(REFERENCE_RECONCILIATION).iloc[0] if REFERENCE_RECONCILIATION.exists() else None
    operational_reference_frozen = bool(reference_reconciliation["OperationalReferenceFrozen"]) if reference_reconciliation is not None else False

    rows = [
        {
            "ObjectID": "ReferenceState",
            "CurrentStatus": "OPERATIONAL_REFERENCE_DOMAIN_FROZEN",
            "Evidence": "docs/p_taucov_reference_state_status_reconciliation.md",
            "StillBlocksReducedJacobian": not operational_reference_frozen,
            "Reason": "operational reference/domain is frozen; physical stability remains a separate blocker",
        },
        {
            "ObjectID": "L_B_red",
            "CurrentStatus": "COMPUTABLE_IN_CURRENT_BRANCH_ROW",
            "Evidence": "docs/p_taucov_branch_equation_completion_audit.md",
            "StillBlocksReducedJacian": False,
            "Reason": "branch-row linearization exists, but physical interpretation remains response-level",
        },
        {
            "ObjectID": "D_Phi_F_B",
            "CurrentStatus": "RESOLVED_AS_MEDIATED_CHAIN",
            "Evidence": "docs/p_taucov_mediated_parent_forcing_chain_audit.md",
            "StillBlocksReducedJacian": False,
            "Reason": "direct forcing is zero, but Phi->P_morph->B chain is invertible and nonzero",
        },
        {
            "ObjectID": "D_B_M_proj",
            "CurrentStatus": "STRICT_LINEAR_PROVIDED",
            "Evidence": "docs/p_taucov_projected_morphology_derivative_audit.md",
            "StillBlocksReducedJacian": False,
            "Reason": "D_B M_proj = P0 A_B from frozen linear inputs",
        },
        {
            "ObjectID": "DynamicalStability",
            "CurrentStatus": "RESPONSE_ENERGY_SPLIT_PASS_FULL_DYNAMICS_OPEN",
            "Evidence": "docs/p_taucov_response_energy_split_packet.md",
            "StillBlocksReducedJacian": True,
            "Reason": "response/energy split resolves interpretation but not full dynamical stability",
        },
        {
            "ObjectID": "CovarianceMap",
            "CurrentStatus": "DECLARED_TARGET_BLIND_PSD_LIFT",
            "Evidence": "docs/p_taucov_covariance_map_declaration.md",
            "StillBlocksReducedJacian": False,
            "Reason": "D_M C map is declared and validated; complete delta_C_Tau generation remains a later assembly step",
        },
    ]
    # Keep misspelled compatibility column out of the public artifact.
    for row in rows:
        if "StillBlocksReducedJacian" in row:
            row["StillBlocksReducedJacobian"] = row.pop("StillBlocksReducedJacian")

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **row,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in rows
        ]
    )
    df.to_csv(OUT, index=False)
    blockers = int(df["StillBlocksReducedJacobian"].astype(bool).sum())
    status_value = (
        "P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKERS_REDUCED_STILL_BLOCKED_NO_SCORING"
        if blockers
        else "P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKERS_CLEAR_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status_value,
                "ObjectsTotal": len(df),
                "BlockingObjects": blockers,
                "MediatedForcingStatus": mediated_status,
                "ProjectedMorphologyDerivativeStatus": dbm_status,
                "ResponseEnergyStatus": response_energy_status,
                "ReferenceStatus": reference_status,
                "CovarianceMapStatus": covariance_map_status,
                "OperationalReferenceFrozen": operational_reference_frozen,
                "RemainingPrimaryBlockers": ";".join(
                    df.loc[df["StillBlocksReducedJacobian"].astype(bool), "ObjectID"].astype(str)
                ),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    table = "\n".join(
        f"| `{r.ObjectID}` | `{r.CurrentStatus}` | `{r.StillBlocksReducedJacobian}` | `{r.Evidence}` |"
        for r in df.itertuples()
    )
    DOC.write_text(
        f"""# P-TauCov Reduced-Jacobian Current Blocker Rollup

Freeze ID: `{FREEZE_ID}`

Status:

`{status_value}`

## Purpose

This rollup updates the reduced-Jacobian blocker state after the mediated
parent-forcing and projected morphology derivative audits. It does not build
`J_response`, does not generate `delta_C_Tau`, and does not authorize scoring.

## Current Blocker Table

| Object | Current status | Still blocks | Evidence |
|---|---|---:|---|
{table}

## Current Meaning

The previous source blockers have narrowed:

```text
D_Phi_F_B -> resolved as mediated Phi -> P_morph -> B chain
D_B_M_proj -> strict-linear provided as P0 A_B
L_B_red -> computable in the current branch row
CovarianceMap -> target-blind PSD lift declared
ReferenceState -> operational reference/domain frozen
```

The remaining primary blockers are:

```text
{';'.join(df.loc[df["StillBlocksReducedJacobian"].astype(bool), "ObjectID"].astype(str))}
```

## Claim Boundary

Allowed statement:

> The reduced-Jacobian blocker list has been narrowed, but the object is still
> not complete.

Forbidden statement:

> `J_response` or `delta_C_Tau` has been constructed, empirical scoring is
> authorized, or Tau Core has been validated.
""",
        encoding="utf-8",
    )
    print(status_value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
