#!/usr/bin/env python3
"""Build a no-scoring registry for Q-native parent-curvature routes."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_v1"
CLAIM = "q_native_route_registry_no_object_no_scoring"


ROUTES = [
    {
        "RouteID": "QN_ROUTE_1_CONSTRAINED_HESSIAN_RESIDUE",
        "SourceExpression": "R_parent = Hessian(S_parent)_reduced - Proj_forbidden(Hessian(S_parent)_reduced)",
        "CurrentStatus": "ROUTE_DEFINED_SOURCE_NOT_DERIVED",
        "MainOpenGate": "derive forbidden projection and reduced Hessian from parent action before scoring",
    },
    {
        "RouteID": "QN_ROUTE_2_BOUNDARY_CURVATURE",
        "SourceExpression": "R_parent = B_boundary^T B_boundary",
        "CurrentStatus": "ROUTE_DEFINED_SOURCE_NOT_DERIVED",
        "MainOpenGate": "derive boundary operator from parent domain, defect, or quotient sector",
    },
    {
        "RouteID": "QN_ROUTE_3_COMPATIBILITY_CURVATURE",
        "SourceExpression": "R_parent = [D_parent,Q_clean]^T [D_parent,Q_clean]",
        "CurrentStatus": "ROUTE_DEFINED_SOURCE_NOT_DERIVED",
        "MainOpenGate": "freeze D_parent from parent-domain operator, not empirical covariance",
    },
    {
        "RouteID": "QN_ROUTE_4_BRANCH_RESPONSE_CURVATURE",
        "SourceExpression": "R_parent = J_response^T J_response",
        "CurrentStatus": "ROUTE_DEFINED_SOURCE_NOT_DERIVED",
        "MainOpenGate": "derive J_response from reduced branch equation and map it into Q_clean",
    },
]


def main() -> None:
    EVIDENCE.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    rows = []
    for route in ROUTES:
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **route,
                "ObjectConstructed": False,
                "SupportAuditAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        )
    pd.DataFrame(rows).to_csv(EVIDENCE / "p_taucov_q_native_route_registry.csv", index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_DEFINED_NO_OBJECT_NO_SCORING",
                "RoutesDefined": len(rows),
                "ObjectsConstructed": 0,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_native_route_registry_summary.csv", index=False)

    table = "\n".join(
        f"| `{r['RouteID']}` | `{r['SourceExpression']}` | `{r['MainOpenGate']}` |"
        for r in rows
    )
    (DOCS / "p_taucov_q_native_route_registry.md").write_text(
        f"""# P-TauCov Q-Native Route Registry

Freeze ID: `{FREEZE_ID}`

Status:

`P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_DEFINED_NO_OBJECT_NO_SCORING`

## Purpose

This registry converts the Q-native parent-curvature derivation gate into a
machine-readable route list. It defines possible source routes only. It does
not construct an object, authorize support audit, or authorize scoring.

## Routes

| Route | Source expression | Main open gate |
|---|---|---|
{table}

## Claim Boundary

Allowed statement:

> Four Q-native parent-curvature source routes have been registered as no-scoring derivation options.

Forbidden statement:

> Any registered route has produced a Tau signal, a scoreable object, or empirical survival.
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_DEFINED_NO_OBJECT_NO_SCORING")


if __name__ == "__main__":
    main()
