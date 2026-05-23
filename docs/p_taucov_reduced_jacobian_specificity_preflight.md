# P-TauCov Reduced-Jacobian Specificity Preflight

Freeze ID: `P_TAUCOV_REDUCED_JACOBIAN_SPECIFICITY_PREFLIGHT_v1`

Status:

`P_TAUCOV_REDUCED_JACOBIAN_SPECIFICITY_PREFLIGHT_FAIL_NO_SCORING`

## Purpose

This preflight checks whether the assembled strict branch-only `delta_C_Tau`
candidate is structurally specific enough to justify any later scoring
authorization. It uses no target residuals and no score outcomes.

## Result

The candidate is clean but too simple:

- diagonal energy share: `1.0`
- noncommutator share versus `P_morph`: `0.0`
- effective-rank fraction: `0.25`
- support entropy: `0.33333333333333337`
- morphology energy share: `0.0`
- failed gates: `RJS-G3_NOT_DIAGONAL_ONLY;RJS-G4_NONCOMMUTING_WITH_PMORPH;RJS-G5_EFFECTIVE_RANK_NOT_TOO_LOW;RJS-G7_MORPHOLOGY_CHANNEL_PRESENT`

## Interpretation

The strict branch-only assembly is a valid source-assembly artifact, but it is
not yet a Tau-specific score candidate. It is diagonal, low-support, and does
not carry an explicit morphology/projection noncommutative signature.

## Claim Boundary

Allowed statement:

> The first reduced-Jacobian candidate was assembled and then rejected at
> specificity preflight before scoring.

Forbidden statement:

> This candidate authorizes scoring, survived a Tau-specific test, or validates
> Tau Core.
