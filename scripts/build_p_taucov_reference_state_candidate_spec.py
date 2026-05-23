#!/usr/bin/env python3
"""Build target-blind reference-state candidate specification."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REFERENCE_STATE_CANDIDATE_SPEC_v1"
CLAIM = "reference_state_candidate_spec_no_solution_no_scoring"


ROWS = [
    {
        "CandidateID": "RS_ORIGIN_ACTIVE_SCAFFOLD",
        "CandidateExpression": "Phi0=0; P0=0; B0=0",
        "Route": "active scaffold stationary origin",
        "Evidence": "docs/p_taucov_reference_background_stationarity_packet.md",
        "StationarityStatus": "STATIONARY_IN_ACTIVE_SCAFFOLD",
        "StabilityStatus": "FULL_STABILITY_NOT_PROVEN",
        "BranchEquationStatus": "F_B_NOT_CONCRETE_FULL_BRANCH",
        "ReferenceStateFrozen": False,
        "CanBuildJacobian": False,
    },
    {
        "CandidateID": "RS_SOLVED_BRANCH_EQUATION",
        "CandidateExpression": "(Phi0,B*) such that F_B(Phi0,B*)=0",
        "Route": "solve declared full branch equation after F_B exists",
        "Evidence": "docs/p_taucov_reference_domain_freeze.md",
        "StationarityStatus": "ROUTE_DEFINED_NOT_SOLVED",
        "StabilityStatus": "UNKNOWN_UNTIL_F_B_EXISTS",
        "BranchEquationStatus": "F_B_REQUIRED",
        "ReferenceStateFrozen": False,
        "CanBuildJacobian": False,
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
                "UsesTargetResiduals": False,
                "UsesScoreOutcomes": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for row in ROWS
        ]
    )
    df.to_csv(EVIDENCE / "p_taucov_reference_state_candidate_spec.csv", index=False)
    status = "P_TAUCOV_REFERENCE_STATE_CANDIDATE_SPEC_DEFINED_BLOCKED_NO_SCORING"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "CandidatesDefined": len(df),
                "ReferenceStatesFrozen": int(df["ReferenceStateFrozen"].astype(bool).sum()),
                "JacobianBuildAuthorized": bool(df["CanBuildJacobian"].astype(bool).any()),
                "PrimaryCandidate": "RS_ORIGIN_ACTIVE_SCAFFOLD",
                "PrimaryBlocker": "full branch equation and stability not proven",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_reference_state_candidate_spec_summary.csv", index=False)
    table = "\n".join(
        f"| `{r.CandidateID}` | `{r.CandidateExpression}` | `{r.StationarityStatus}` | `{r.StabilityStatus}` | `{r.BranchEquationStatus}` |"
        for r in df.itertuples()
    )
    (DOCS / "p_taucov_reference_state_candidate_spec.md").write_text(
        f"""# P-TauCov Reference-State Candidate Spec

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This artifact defines target-blind reference-state candidate routes for the
reduced branch-Jacobian program. It does not freeze a final reference state,
does not solve the full branch equation, and does not authorize scoring.

## Candidates

| Candidate | Expression | Stationarity | Stability | Branch equation |
|---|---|---|---|---|
{table}

## Interpretation

The active scaffold origin:

```text
Phi0=0; P0=0; B0=0
```

is the current best target-blind candidate because the active scaffold has a
stationary origin. However, it is not yet a full reference state for the
reduced branch-Jacobian because:

1. full stability still depends on the missing `S_rest` completion; and
2. the full branch equation `F_B` has not yet been declared.

## Claim Boundary

Allowed statement:

> A target-blind reference-state candidate route has been specified, with the active scaffold origin as the current primary candidate.

Forbidden statement:

> The reference state is frozen, the branch equation is solved, or empirical scoring is authorized.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
