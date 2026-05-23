#!/usr/bin/env python3
"""Audit which reduced branch-Jacobian blockers are already partially resolved."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_BLOCKER_RESOLUTION_v1"
CLAIM = "reduced_branch_jacobian_blocker_resolution_no_object_no_scoring"


def exists(path: str) -> bool:
    return (ROOT / path).exists()


ROWS = [
    {
        "ObjectID": "Q_range",
        "PreviousStatus": "FROZEN_AVAILABLE",
        "ResolutionStatus": "RESOLVED_AVAILABLE",
        "Evidence": "evidence/p_taucov_q_range_projector_matrix.csv",
        "StillBlocks": False,
    },
    {
        "ObjectID": "P_red",
        "PreviousStatus": "MISSING_NULL_GAUGE_FORBIDDEN_BASIS",
        "ResolutionStatus": "PARTIALLY_RESOLVED_BY_FULL_ACTION_DOMAIN_PACKET",
        "Evidence": "evidence/p_taucov_full_action_domain_projectors.csv",
        "StillBlocks": False,
    },
    {
        "ObjectID": "ReferenceState",
        "PreviousStatus": "POLICY_DECLARED_VALUE_NOT_SOLVED",
        "ResolutionStatus": "UNRESOLVED_REFERENCE_BACKGROUND",
        "Evidence": "evidence/p_taucov_reference_domain_freeze_summary.csv",
        "StillBlocks": True,
    },
    {
        "ObjectID": "L_B_red",
        "PreviousStatus": "MISSING_CONCRETE_OPERATOR",
        "ResolutionStatus": "UNRESOLVED_DEPENDS_ON_F_B_AND_REFERENCE_STATE",
        "Evidence": "docs/p_taucov_tau_matrix_origin_route.md",
        "StillBlocks": True,
    },
    {
        "ObjectID": "D_Phi_F_B",
        "PreviousStatus": "MISSING_CONCRETE_OPERATOR",
        "ResolutionStatus": "UNRESOLVED_REQUIRES_BRANCH_EQUATION",
        "Evidence": "docs/p_taucov_tau_matrix_origin_route.md",
        "StillBlocks": True,
    },
    {
        "ObjectID": "D_B_M_proj",
        "PreviousStatus": "BLOCKED_BY_M_PARENT_AND_P_MORPH",
        "ResolutionStatus": "UNRESOLVED_REQUIRES_M_PARENT_AND_P_MORPH",
        "Evidence": "docs/p_taucov_tau_response_input_packet.md",
        "StillBlocks": True,
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    rows = []
    for row in ROWS:
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **row,
                "EvidenceExists": exists(row["Evidence"]),
                "ObjectConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(EVIDENCE / "p_taucov_reduced_branch_jacobian_blocker_resolution.csv", index=False)
    blockers = int(df["StillBlocks"].astype(bool).sum())
    status = "P_TAUCOV_REDUCED_BRANCH_JACOBIAN_BLOCKERS_REDUCED_STILL_BLOCKED_NO_SCORING"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "ObjectsAudited": len(df),
                "ResolvedOrNonBlocking": int((~df["StillBlocks"].astype(bool)).sum()),
                "RemainingBlockers": blockers,
                "RemainingBlockingObjects": ";".join(df.loc[df["StillBlocks"].astype(bool), "ObjectID"].tolist()),
                "ObjectConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_reduced_branch_jacobian_blocker_resolution_summary.csv", index=False)
    table = "\n".join(
        f"| `{r.ObjectID}` | `{r.ResolutionStatus}` | `{r.Evidence}` | `{r.StillBlocks}` |"
        for r in df.itertuples()
    )
    (DOCS / "p_taucov_reduced_branch_jacobian_blocker_resolution.md").write_text(
        f"""# P-TauCov Reduced Branch-Jacobian Blocker Resolution

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This audit updates the reduced branch-Jacobian blocker list after the Q-range
freeze and the full-action-domain null/gauge packet.

It does not construct `J_response`, does not construct `K_Q`, and does not
authorize empirical scoring.

## Blocker Status

| Object | Resolution status | Evidence | Still blocks |
|---|---|---|---|
{table}

## Key Update

`P_red` is no longer the same kind of blocker as before. The full-action-domain
packet provides a target-blind active/reduced projector. The remaining central
blockers are:

```text
ReferenceState
L_B_red
D_Phi_F_B
D_B_M_proj
```

`L_B_red` and `D_Phi_F_B` remain blocked because the branch equation `F_B` and
the reference state are not yet concrete. `D_B_M_proj` remains blocked because
`M_parent` and `P_morph` are still only route-level objects.

## Claim Boundary

Allowed statement:

> The reduced branch-Jacobian blocker list has been narrowed after reusing the frozen Q-range and full-action-domain projectors.

Forbidden statement:

> The reduced branch-Jacobian has been constructed, scored, or shown to validate Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
