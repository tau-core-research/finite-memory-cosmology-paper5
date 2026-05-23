# P-TauCov Coordinate-Basis Source Candidates

Status: source-candidate audit / no concrete basis rows / no coordinate-basis
packet / no reference-domain selection / no metric evaluation / no scoring
authorization.

The coordinate-basis packet gate says what a concrete basis must contain. This
audit says which source classes may feed that basis.

## Allowed Source Classes

| Source | Use | Condition |
| --- | --- | --- |
| Tau-side symbolic definition | Defines abstract `Phi`, `B`, morphology, and projection axes. | Must be converted into a finite-dimensional axis map before use. |
| Coordinate convention only | Defines origin, center, units, and scale conventions. | Must be declared before residual or score inspection. |
| Published external metadata | Defines citable non-outcome families or observing-context tags. | Must not be selected from P5C v3 score behavior. |

## Forbidden Source Classes

| Source | Why forbidden |
| --- | --- |
| Existing P5C v3 gains | Would leak scored anomaly structure into the Tau candidate basis. |
| Held-out residuals or targets | Direct outcome leakage. |
| Post-hoc family localization | Turns branch localization into hidden model selection. |
| Generic smooth null templates | Allowed as null comparators only, not Tau candidate basis. |

## Consequence

The next artifact must be a finite-dimensional symbolic axis map built from the
allowed source classes only. It may describe candidate axes, but it still must
not create matrices, evaluate metrics, or authorize scoring.

## Claim Boundary

Allowed statement:

```text
Allowed and forbidden source classes for the coordinate basis are declared.
```

Forbidden statement:

```text
A concrete coordinate-basis packet has been built or accepted.
```
