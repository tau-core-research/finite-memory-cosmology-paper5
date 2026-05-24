# Paper 5 Tau-Specific Observable Blocker

Status: `BLOCKED_PENDING_TAU_SPECIFIC_OBSERVABLE_DEFINITION`

## Current Decision

Paper 5 should not continue as another scoring search until the Tau-side
observable is defined at theory level.

The accumulated negative and blocked branches are informative. They show that
the following are not sufficient as Tau Core signals:

- a generic shape improvement;
- a smooth covariance kernel;
- a family-localized covariance anomaly;
- a morphology-null or projection-null duplicate;
- a target-conditioned cleaner-generated object;
- a signed diagnostic promoted after a failed primary scorecard.

The current Paper 5 role is therefore:

```text
define what a Tau-specific cosmology/response signal would be,
then freeze it before any scoring.
```

## What Would Count As A Tau-Specific Observable

A future object must be target-blind and must be derived from the parent
structure before score access. At minimum it must declare:

```text
parent-side source object
projection/readout operator
orientation convention
branch/family/clock balance rule
projection-null and morphology-null orthogonalization
allowed covariance or contrast statistic
success and kill criteria
```

The currently preferred object class is not another free covariance kernel.
The theory-facing target is an oriented, projection-orthogonal,
branch-balanced parent-response object such as:

```text
T_tau = Normalize(
  Pi_bal
  Pi_perp
  Orient_+([L_B_red, P_morph]; J_tau)
  Pi_perp
  Pi_bal
)
```

This is a candidate class only. It is not a scored signal.

## Required Null Separations

Any candidate must be separated before scoring from:

- morphology-null controls;
- projection-null controls;
- smooth PSD covariance controls;
- family-localized controls;
- clock/family permutation controls;
- sign-flip controls;
- generic baseline-drift or target-convention absorbers.

If it cannot separate at pre-score level, no empirical scorecard is authorized.

## Current Evidence Boundary

Allowed statement:

```text
Paper 5 has produced disciplined negative and blocked results that narrow the
allowed class of future Tau-specific observables.
```

Forbidden statement:

```text
Paper 5 has detected a Tau Core cosmology signal.
```

## Next Valid Step

The next valid step belongs primarily in the Tau Core theory hub:

```text
derive and freeze a Tau-specific observable class,
then return to Paper 5 only with a target-blind scoring manifest.
```

The corresponding theory-level gate is:

```text
source_material/tau_core_foundations/cosmology_tau_specific_observable_gate_v01.md
```
