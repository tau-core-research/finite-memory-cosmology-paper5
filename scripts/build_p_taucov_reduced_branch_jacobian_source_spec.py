#!/usr/bin/env python3
"""Build the reduced branch-Jacobian source specification."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_v1"
CLAIM = "reduced_branch_jacobian_source_spec_no_object_no_scoring"


ROWS = [
    {
        "ObjectID": "Q_range",
        "Role": "orthogonal clean-subspace projector",
        "RequiredExpression": "Q_range = U_active U_active^T from spectrum(Q_clean)",
        "CurrentSource": "evidence/p_taucov_q_range_projector_matrix.csv",
        "CurrentStatus": "FROZEN_AVAILABLE",
        "BlocksJacobian": False,
    },
    {
        "ObjectID": "L_B_red",
        "Role": "invertible reduced branch response operator",
        "RequiredExpression": "L_B_red = P_red D_B F_B|_(Phi0,B*) P_red",
        "CurrentSource": "route only: docs/p_taucov_tau_matrix_origin_route.md",
        "CurrentStatus": "MISSING_CONCRETE_OPERATOR",
        "BlocksJacobian": True,
    },
    {
        "ObjectID": "D_Phi_F_B",
        "Role": "parent perturbation forcing of branch equation",
        "RequiredExpression": "D_Phi_F_B = D_Phi F_B|_(Phi0,B*)",
        "CurrentSource": "route only: docs/p_taucov_tau_matrix_origin_route.md",
        "CurrentStatus": "MISSING_CONCRETE_OPERATOR",
        "BlocksJacobian": True,
    },
    {
        "ObjectID": "D_B_M_proj",
        "Role": "branch-to-projected-morphology derivative",
        "RequiredExpression": "D_B_M_proj = D_B(P_morph M_parent)|_(Phi0,B*)",
        "CurrentSource": "route only: docs/p_taucov_tau_response_input_packet.md",
        "CurrentStatus": "BLOCKED_BY_M_PARENT_AND_P_MORPH",
        "BlocksJacobian": True,
    },
    {
        "ObjectID": "P_red",
        "Role": "reduced admissible branch domain",
        "RequiredExpression": "P_red = I - P_null - P_gauge - P_forbidden",
        "CurrentSource": "route only: docs/p_taucov_tau_matrix_origin_route.md",
        "CurrentStatus": "MISSING_NULL_GAUGE_FORBIDDEN_BASIS",
        "BlocksJacobian": True,
    },
    {
        "ObjectID": "ReferenceState",
        "Role": "target-blind expansion point",
        "RequiredExpression": "(Phi0,B*(Phi0)) with F_B(Phi0,B*)=0",
        "CurrentSource": "evidence/p_taucov_reference_domain_freeze.csv",
        "CurrentStatus": "POLICY_DECLARED_VALUE_NOT_SOLVED",
        "BlocksJacobian": True,
    },
    {
        "ObjectID": "ForbiddenCoordinateContrast",
        "Role": "blocked shortcut",
        "RequiredExpression": "v_branch != B_BRANCH_RESPONSE - PHI_PARENT_SOURCE",
        "CurrentSource": "docs/p_taucov_q_range_branch_response_preflight.md",
        "CurrentStatus": "FORBIDDEN_BY_QRANGE_RETENTION_FAIL",
        "BlocksJacobian": False,
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **row,
                "ObjectConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for row in ROWS
        ]
    )
    out_csv = EVIDENCE / "p_taucov_reduced_branch_jacobian_source_spec.csv"
    out_summary = EVIDENCE / "p_taucov_reduced_branch_jacobian_source_spec_summary.csv"
    df.to_csv(out_csv, index=False)
    blockers = int(df["BlocksJacobian"].astype(bool).sum())
    status = (
        "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_BLOCKED_NO_OBJECT_NO_SCORING"
        if blockers
        else "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_READY_NO_OBJECT_NO_SCORING"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "SourceObjects": len(df),
                "BlockingObjects": blockers,
                "FrozenAvailableObjects": int((df["CurrentStatus"] == "FROZEN_AVAILABLE").sum()),
                "ObjectConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "PrimaryBlockingObjects": ";".join(df.loc[df["BlocksJacobian"].astype(bool), "ObjectID"].tolist()),
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(out_summary, index=False)
    table = "\n".join(
        f"| `{r.ObjectID}` | `{r.CurrentStatus}` | `{r.RequiredExpression}` | `{r.BlocksJacobian}` |"
        for r in df.itertuples()
    )
    (DOCS / "p_taucov_reduced_branch_jacobian_source_spec.md").write_text(
        f"""# P-TauCov Reduced Branch-Jacobian Source Spec

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This source spec records the operators required before a true Q-native
branch-response Jacobian can be constructed:

```text
J_response = Q_range D_B M_proj (L_B^red)^(-1) D_Phi F_B
```

It does not construct `J_response`, does not build `K_Q`, and does not
authorize empirical scoring.

## Source Objects

| Object | Status | Required expression | Blocks Jacobian |
|---|---|---|---|
{table}

## Key Result

`Q_range` is now frozen and available, but the actual reduced branch-Jacobian
sources remain blocked:

```text
L_B_red
D_Phi_F_B
D_B_M_proj
P_red
ReferenceState
```

The shortcut:

```text
B_BRANCH_RESPONSE - PHI_PARENT_SOURCE
```

is explicitly forbidden by the Q-range retention failure.

## Claim Boundary

Allowed statement:

> The required source objects for a reduced branch-Jacobian have been enumerated after the Q-range failure.

Forbidden statement:

> The reduced branch-Jacobian has been constructed, scored, or shown to validate Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
