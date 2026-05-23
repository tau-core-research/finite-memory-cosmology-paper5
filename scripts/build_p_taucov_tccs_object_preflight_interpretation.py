#!/usr/bin/env python3
"""Interpret the TCCS object preflight result."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SUMMARY = EVIDENCE / "p_taucov_tccs_object_preflight_summary.csv"
GATES = EVIDENCE / "p_taucov_tccs_object_preflight_gates.csv"
OUT = EVIDENCE / "p_taucov_tccs_object_preflight_interpretation.csv"
DOC = DOCS / "p_taucov_tccs_object_preflight_interpretation.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
INTERPRETATION_ID = "P_TAUCOV_TCCS_OBJECT_PREFLIGHT_INTERPRETATION_v1"
STATUS = "TCCS_OBJECT_PREFLIGHT_NEGATIVE_COLLAPSES_UNDER_PERP_BALANCE"
CLAIM_BOUNDARY = "tccs_object_preflight_negative_no_scoring_no_survival"


def main() -> int:
    summary = pd.read_csv(SUMMARY).iloc[0]
    gates = pd.read_csv(GATES)
    failed = ";".join(gates.loc[~gates["Passed"].astype(bool), "GateID"].astype(str))
    raw_norm = float(summary["RawNorm"])
    balanced_norm = float(summary["BalancedNorm"])
    retained = float(summary["BalancedRetainedNorm"])
    orientation = float(summary["OrientationMargin"])

    interpretation = (
        "raw_commutator_nonzero_but_projection_orthogonal_balanced_object_collapses"
        if raw_norm > 1e-12 and balanced_norm < 1e-12
        else "see_gate_table"
    )
    next_step = (
        "do_not_score_current_tccs; derive a parent Hessian component whose commutator survives Pi_perp before any empirical scoring"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "InterpretationID": INTERPRETATION_ID,
                "Status": STATUS,
                "ObjectPreflightStatus": summary["Status"],
                "RawNorm": raw_norm,
                "BalancedNorm": balanced_norm,
                "BalancedRetainedNorm": retained,
                "OrientationMargin": orientation,
                "FailedGates": failed,
                "Interpretation": interpretation,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "RecommendedNextStep": next_step,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT, index=False)

    DOC.write_text(
        f"""# P-TauCov TCCS Object Preflight Interpretation

Status:

`{STATUS}`

## Result

The current TCCS construction fails before empirical scoring.

Key numbers:

| Quantity | Value |
|---|---:|
| raw commutator norm | `{raw_norm}` |
| balanced norm after `Pi_perp` and `Pi_bal` | `{balanced_norm}` |
| retained norm | `{retained}` |
| orientation margin | `{orientation}` |

Failed gates:

```text
{failed}
```

## Meaning

The parent-side commutator is nonzero, so the route is not algebraically empty.
However, the projection-orthogonal and branch-balanced filters remove almost
all of it. In plain terms: the present commutator still lives mostly in the
morphology/projection subspace that TCCS was designed to exclude.

Therefore the current TCCS object must not be scored.

## Claim Boundary

Allowed statement:

> The current TCCS object preflight is a negative structural result: the raw commutator is nonzero, but the projection-orthogonal balanced object collapses.

Forbidden statement:

> TCCS has produced a Tau signal or should proceed to empirical scoring.

## Next Step

```text
{next_step}
```
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
