# Diagnostic Transform Contract

Status: Phase II preflight contract.

This document separates downloaded public observables from finite-memory
diagnostic vectors. The current repository contains public DESI/Pantheon+
inputs and a raw-observable preflight table. It does not yet contain a
measurement-validation transform.

## Boundary

The public files may be used for:

- validating data-vector and covariance dimensions;
- constructing audit coordinates;
- designing a registered diagnostic transform;
- testing null-comparator plumbing.

They may not yet be used to claim:

- measurement validation of the finite-memory projection hypothesis;
- discovery of a finite-memory effect;
- rejection of public cosmological alternatives;
- likelihood preference for K2.

## Required Transform Properties

A transform becomes eligible for the measurement gate only if it defines:

- the input public product IDs;
- the observable-to-diagnostic mapping;
- the coordinate mapping used by `W(x)`;
- covariance propagation from the public covariance;
- the frozen K1 baseline or likelihood-native baseline export;
- null comparators evaluated on the same diagnostic vector;
- falsification criteria that remain fixed before scoring.

## Current Registry

The machine-readable registry is:

```text
evidence/diagnostic_transform_registry.csv
```

The currently available preflight transforms are:

- `T0_RAW_OBSERVABLE_PREFLIGHT`, which standardizes public BAO/SN rows but is
  explicitly not a K2 diagnostic vector;
- `T1_BAO_DISTANCE_RATIO_RESIDUAL`, which builds DESI BAO log residuals against
  a fixed audit-fiducial baseline and propagates the public covariance.

Planned transforms:

- `T2_SN_DISTANCE_MODULUS_RESIDUAL`
- `T3_SN_BAO_JOINT_RECONSTRUCTION`
- `T4_LIKELIHOOD_NATIVE_GATE`

No transform is currently allowed for measurement-gate scoring. `T1` remains
blocked because its baseline is audit-fiducial rather than likelihood-native,
and because no coordinate-native K1 export or null benchmark has been run on
the residual vector.

## Next Technical Step

Run a BAO residual null benchmark on `T1_BAO_DISTANCE_RATIO_RESIDUAL`. It is
the narrowest public benchmark candidate because DESI already supplies a compact
mean vector and covariance matrix. The transform should still be treated as a
diagnostic preflight until it is compared against registered null comparators
under the same covariance-aware scoring rule.

The first T1 null benchmark has now been run. It shows that a simple constant
offset control is preferred under the audit-fiducial residual baseline. This is
a useful warning: the next benchmark should export a likelihood-native or
coordinate-native BAO baseline before any K2 comparison is attempted.
