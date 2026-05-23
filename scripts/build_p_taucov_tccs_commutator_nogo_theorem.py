#!/usr/bin/env python3
"""Record the TCCS double-sided projection no-go theorem."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT = EVIDENCE / "p_taucov_tccs_commutator_nogo_theorem.csv"
DOC = DOCS / "p_taucov_tccs_commutator_nogo_theorem.md"

THEOREM_ID = "P_TAUCOV_TCCS_COMMUTATOR_NOGO_THEOREM_v1"
STATUS = "TCCS_DOUBLE_SIDED_PERP_COMMUTATOR_NOGO_PROVEN"
CLAIM_BOUNDARY = "tccs_commutator_nogo_theorem_no_scoring"


def main() -> int:
    rows = [
        {
            "TheoremID": THEOREM_ID,
            "Status": STATUS,
            "AssumptionID": "A1",
            "Assumption": "P is an idempotent morphology/projection projector",
            "Expression": "P^2 = P",
            "PassedFromCurrentFreeze": True,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "TheoremID": THEOREM_ID,
            "Status": STATUS,
            "AssumptionID": "A2",
            "Assumption": "Pi_perp is the orthogonal complement of P",
            "Expression": "Pi_perp P = P Pi_perp = 0",
            "PassedFromCurrentFreeze": True,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "TheoremID": THEOREM_ID,
            "Status": STATUS,
            "AssumptionID": "R1",
            "Assumption": "For any reduced parent Hessian H, the double-sided projected commutator vanishes",
            "Expression": "Pi_perp [H,P] Pi_perp = 0",
            "PassedFromCurrentFreeze": True,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "TheoremID": THEOREM_ID,
            "Status": STATUS,
            "AssumptionID": "C1",
            "Assumption": "The failed TCCS preflight is therefore structural, not empirical",
            "Expression": "current_TCCS_form_is_not_scoreable",
            "PassedFromCurrentFreeze": True,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
    ]
    pd.DataFrame(rows).to_csv(OUT, index=False)
    DOC.write_text(
        """# P-TauCov TCCS Commutator No-Go Theorem

Status:

`TCCS_DOUBLE_SIDED_PERP_COMMUTATOR_NOGO_PROVEN`

## Statement

Let `P` be an idempotent morphology/projection projector:

```text
P^2 = P
```

Let `Pi_perp` be its orthogonal complement:

```text
Pi_perp = I - P
```

Then for any parent-side reduced Hessian or response operator `H`,

```text
Pi_perp [H, P] Pi_perp = 0
```

where:

```text
[H, P] = H P - P H
```

## Proof

Using `Pi_perp P = 0` and `P Pi_perp = 0`:

```text
Pi_perp [H,P] Pi_perp
= Pi_perp H P Pi_perp - Pi_perp P H Pi_perp
= Pi_perp H (P Pi_perp) - (Pi_perp P) H Pi_perp
= 0 - 0
= 0.
```

## Meaning For TCCS

The negative object preflight is not merely a failed candidate. The original
double-sided form

```text
Pi_perp [H, P_morph] Pi_perp
```

is structurally unable to retain a nonzero commutator signal when `P_morph` is
a true projector and `Pi_perp` is its complement.

Therefore the current TCCS object must not be scored.

## Corrected Object Class

The Tau-specific information, if present, must live in the off-diagonal transfer
between the morphology/projection subspace and its complement. The next
candidate class should therefore use one of:

```text
K_transfer = Pi_perp [H,P] P
```

or a covariance-safe squared transfer:

```text
K_curv = Pi_perp [H,P] P [H,P]^T Pi_perp
```

These are not score-authorized here. They are only the theorem-implied next
object class.

## Claim Boundary

Allowed statement:

> The original double-sided TCCS commutator form is mathematically blocked; a transfer-curvature form is required before any scoring.

Forbidden statement:

> The no-go theorem establishes an empirical Tau signal.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
