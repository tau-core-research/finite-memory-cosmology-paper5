# P-TauCov Parent-Operator Source Expansion Gate

Freeze ID: `P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_v1`

Status:

`P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_READY_NO_OBJECT_NO_SCORING`

## Purpose

The active-triad PSD ceiling audit shows that the current reduced coordinate
triad is structurally too narrow for the PSD covariance route. This gate
freezes what a broader parent-side operator/source packet must provide before
any new covariance object can be assembled.

## Why Expansion Is Required

The current active reduced domain has `3` active coordinates. The
existing `Phi/B/P` triad cannot pass the diagonal-energy and effective-rank
specificity gates under target-blind PSD lifting.

Therefore the next PSD route must not tune `Phi/B/P` weights. It must expand
the parent-side source space using allowed, non-outcome source classes.

## Allowed Source Classes

The only allowed expansion sources are:

- `TauSideSymbolicDefinition`
- `CoordinateConventionOnly`
- `PublishedExternalMetadata`

Forbidden sources remain:

- `ExistingP5CKernelV3Gains`
- `HeldOutResidualsOrTargets`
- `PostHocFamilyLocalization`
- `GenericSmoothNullTemplates`

## Next-Packet Requirements

A future expanded parent-operator packet must:

1. declare at least `5` active reduced coordinates;
2. add at least `2` non-outcome axes beyond the current `Phi/B/P` triad;
3. justify each new axis by an allowed source class;
4. define a parent-side operator/source rule before covariance lifting;
5. include a leakage audit against target residuals, score outcomes, P5C gains,
   and post-hoc family localization;
6. keep scoring blocked until an object-specific preflight passes.

## Claim Boundary

Allowed statement:

> The next PSD covariance route requires a broader target-blind parent-operator
> source space than the current active triad.

Forbidden statement:

> This gate constructs an expanded object, authorizes scoring, or validates Tau
> Core.
