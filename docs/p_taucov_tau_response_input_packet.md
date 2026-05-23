# P-TauCov Tau-Response Input Packet

Status: input packet / blocker decomposition / no scoring authorization.

This packet turns the blocked `delta_C_Tau` source schema into an actionable
work plan. It does not generate `delta_C_Tau`. It identifies which missing
objects are simple freeze policies and which are genuine Tau-theory blockers.

## Blocker Classes

| Class | Meaning |
| --- | --- |
| `TAU_THEORY_BLOCKER` | Requires a concrete Tau-side operator or map. |
| `POLICY_FREEZABLE` | Can be frozen by protocol choice before scoring. |
| `POLICY_AND_THEORY` | Needs both a convention and a theory-side domain. |
| `FORMULA_READY` | Formula exists, but depends on missing operators. |
| `DERIVED_AFTER_MAPS` | Becomes computable after the maps are frozen. |
| `AUDIT_REQUIRED` | Requires a leakage and provenance audit. |

## Current Scientific Bottleneck

The primary bottleneck is not statistics. It is the Tau-side response model:

```text
F_B, L_B^red, M_parent, P_morph
```

Until those four objects exist in a target-blind form, any `delta_C_Tau` matrix
would be an artificial placeholder and must not be scored.

## Object Routes

| Source object | Class | Current status |
| --- | --- | --- |
| `PhiPerturbationFamily` | `POLICY_FREEZABLE` | `ROUTE_DEFINED_NOT_FROZEN` |
| `BranchEquationFB` | `TAU_THEORY_BLOCKER` | `MISSING_CONCRETE_OPERATOR` |
| `ReducedBranchOperatorLBred` | `TAU_THEORY_BLOCKER` | `MISSING_CONCRETE_OPERATOR` |
| `BranchDomainPolicy` | `POLICY_AND_THEORY` | `ROUTE_DEFINED_NOT_FROZEN` |
| `BranchResponseRule` | `FORMULA_READY` | `FORMULA_DECLARED_OPERATOR_MISSING` |
| `ParentMorphologyMap` | `TAU_THEORY_BLOCKER` | `MISSING_CONCRETE_MAP` |
| `ProjectionMorphologyMap` | `TAU_THEORY_BLOCKER` | `MISSING_CONCRETE_PROJECTION` |
| `ProjectedMorphologyDerivativePhi` | `DERIVED_AFTER_MAPS` | `BLOCKED_BY_MAPS` |
| `ProjectedMorphologyDerivativeB` | `DERIVED_AFTER_MAPS` | `BLOCKED_BY_MAPS` |
| `CovarianceFunctionalDerivative` | `POLICY_FREEZABLE` | `ROUTE_DEFINED_NOT_FROZEN` |
| `ObservableCoordinateIndex` | `POLICY_FREEZABLE` | `ROUTE_DEFINED_NOT_FROZEN` |
| `NormalizationPolicy` | `POLICY_FREEZABLE` | `ROUTE_DEFINED_NOT_FROZEN` |
| `LeakageExclusionAudit` | `AUDIT_REQUIRED` | `NOT_RUN` |

## Reviewer-Safe Interpretation

Allowed statement:

```text
The P-TauCov program has isolated the Tau-side objects required before a
branch-localized covariance response can be tested.
```

Forbidden statement:

```text
The P-TauCov program has already produced a Tau-specific covariance response.
```

## Next Valid Step

Define a minimal target-blind Tau-side response model for:

```text
F_B
L_B^red
M_parent
P_morph
```

Once those are supplied, the derivatives and `delta_C_Tau` generator can be
constructed without borrowing the P5C v3 outcome.
