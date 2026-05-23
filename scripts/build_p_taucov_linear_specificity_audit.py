#!/usr/bin/env python3
"""Build the P-TauCov linear specificity audit definition.

The audit is target-blind and pre-scoring. It determines whether the strictly
linear candidate is specific enough to freeze, or whether it is too generic and
must be replaced by a predeclared nonzero branch/projection term.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_linear_specificity_audit.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_specificity_audit.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_specificity_audit_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_v1"
CLAIM_BOUNDARY = "linear_specificity_audit_no_freeze_no_scoring_authorization"


ROWS = [
    {
        "GateID": "LSA1",
        "GateName": "TARGET_BLIND_INPUTS_ONLY",
        "Requirement": "linear specificity metrics use only candidate matrices/operators and declared coordinate basis",
        "FailureMeaning": "audit leaks target residuals or P5C v3 outcome",
    },
    {
        "GateID": "LSA2",
        "GateName": "NOT_GENERIC_LOW_RANK",
        "Requirement": "linear response is not reducible to a generic low-rank covariance mode",
        "FailureMeaning": "strict linear candidate is generic covariance factorization",
    },
    {
        "GateID": "LSA3",
        "GateName": "BRANCH_PROJECTION_NONCOMMUTATIVITY",
        "Requirement": "branch relaxation and projection structure do not commute trivially",
        "FailureMeaning": "Tau term collapses to ordinary morphology projection",
    },
    {
        "GateID": "LSA4",
        "GateName": "SUPPORT_NOT_FAMILY_LABEL_PROXY",
        "Requirement": "predicted support is not equivalent to preexisting family labels or v3 dominant family",
        "FailureMeaning": "support is an inherited label proxy",
    },
    {
        "GateID": "LSA5",
        "GateName": "BEATS_GENERIC_LINEAR_NULLS_PRESCORE",
        "Requirement": "target-blind structural metrics separate candidate from shuffled/projection/random linear nulls",
        "FailureMeaning": "strict linear candidate is not Tau-specific before scoring",
    },
    {
        "GateID": "LSA6",
        "GateName": "NO_SCORING_AUTHORIZATION",
        "Requirement": "audit result cannot authorize P-TauCov scoring without a later concrete freeze manifest",
        "FailureMeaning": "audit is over-promoted into scoring",
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "GateID": row["GateID"],
                "GateName": row["GateName"],
                "Requirement": row["Requirement"],
                "RequiredBeforeLinearFreeze": True,
                "ScoringAuthorized": False,
                "FailureMeaning": row["FailureMeaning"],
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "GatesDeclared": len(df),
                "LinearCandidateFrozen": False,
                "DeltaCTauGenerated": False,
                "PTauCovScoringAuthorized": False,
                "PossibleOutcomes": "freeze_strict_linear_if_passes;reject_linear_as_too_generic_if_fails",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Linear Specificity Audit

Status: required pre-freeze audit / no linear freeze / no scoring
authorization.

The strictly linear candidate is:

```text
lambda_B = 0
epsilon_P = 0
```

It must not be frozen automatically. This audit asks whether the linear model
already carries a Tau-specific branch/projection/covariance signature, or
whether it is merely a generic linear covariance-response template.

## Required Gates

| Gate | Meaning |
| --- | --- |
| `LSA1 TARGET_BLIND_INPUTS_ONLY` | Use only candidate matrices/operators and declared coordinates. |
| `LSA2 NOT_GENERIC_LOW_RANK` | Do not accept an ordinary low-rank covariance factorization as Tau-specific. |
| `LSA3 BRANCH_PROJECTION_NONCOMMUTATIVITY` | Branch relaxation and projection must not collapse into a trivial commuting morphology map. |
| `LSA4 SUPPORT_NOT_FAMILY_LABEL_PROXY` | Predicted support must not simply reproduce v3 family localization or existing labels. |
| `LSA5 BEATS_GENERIC_LINEAR_NULLS_PRESCORE` | Prescore structural metrics must separate the candidate from shuffled/projection/random linear nulls. |
| `LSA6 NO_SCORING_AUTHORIZATION` | Passing this audit still does not authorize scoring without a later freeze manifest. |

## Decision Rule

If the audit passes:

```text
strictly linear candidate may be frozen as the first P-TauCov response model
```

If the audit fails:

```text
strictly linear candidate is too generic;
move to a predeclared minimal nonzero term:
lambda_B fixed nonzero
or epsilon_P fixed nonzero
```

## Claim Boundary

Allowed statement:

```text
The strictly linear candidate has a declared specificity audit before freezing.
```

Forbidden statement:

```text
The strictly linear candidate is already a Tau-specific covariance model.
```
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
