# P-TauCov P3 Balanced Final Manifest

Manifest ID: `P_TAUCOV_P3_BALANCED_FINAL_MANIFEST_v1`

Status:

`P_TAUCOV_P3_BALANCED_OBJECT_FROZEN_NO_SCORING_AUTHORIZATION`

## Scope

This manifest freezes the balanced P3 preflight object and its supporting
balance-projector/readiness artifacts.

It does not authorize empirical scoring.

## Frozen Object

```text
FrozenObject = P3_BALANCED_PREFLIGHT_OFFDIAGONAL_OBJECT
AuthorizedScope = frozen_balanced_object_package_only_no_scoring
ObjectFrozen = True
```

## Claim Boundary

Allowed statement:

> A target-blind, clock/family-balanced P3 parent-side object has been frozen for future protocol work.

Forbidden statement:

> The frozen P3 balanced object has produced a Tau signal, passed empirical scoring, or validated Tau Core.
