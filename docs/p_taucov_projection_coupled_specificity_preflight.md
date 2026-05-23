# P-TauCov Projection-Coupled Specificity Preflight

Freeze ID: `P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_v1`

Status:

`P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_FAIL_NO_SCORING`

## Purpose

This preflight checks whether the projection-coupled reduced-Jacobian candidate
is structurally specific enough to justify any later scoring authorization. It
uses no target residuals and no score outcomes.

## Result

- diagonal energy share: `0.9493337494797258`
- active projection noncommutator share: `0.3142696805273543`
- effective-rank fraction: `0.25637661292546327`
- support entropy: `0.48472011765335926`
- projection channel energy: `0.47140452079103135`
- branch channel energy: `1.482407118236259`
- failed gates: `PCS-G3_NOT_DIAGONAL_DOMINATED;PCS-G5_EFFECTIVE_RANK_NOT_TOO_LOW`

## Interpretation

The projection-coupled assembly fixes the previous zero-morphology-channel
failure, but the PSD-lifted covariance remains too diagonal-dominated and too
low-rank to authorize scoring.

## Claim Boundary

Allowed statement:

> The projection-coupled candidate improves the branch-only artifact by adding
> an explicit active projection channel, but it still fails specificity
> preflight before scoring.

Forbidden statement:

> This candidate authorizes scoring, survived a Tau-specific test, or validates
> Tau Core.
