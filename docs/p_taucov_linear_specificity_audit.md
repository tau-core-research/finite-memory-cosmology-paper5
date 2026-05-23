# P-TauCov Linear Specificity Audit

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
