# P-TauCov Expanded Parent-Operator Domain Packet

Freeze ID: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_PACKET_v1`

Status:

`P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_READY_NO_OBJECT_NO_SCORING`

## Purpose

The active `Phi/B/P` triad is structurally too narrow for the PSD covariance
route. This packet freezes an expanded reduced parent-operator domain before
any new object construction or scoring.

## Expanded Active Domain

Core active axes retained:

```text
TEMPLATE_PHI_PARENT_SOURCE
TEMPLATE_B_BRANCH_RESPONSE
TEMPLATE_P_MORPH_PROJECTION
```

New active non-outcome axes:

```text
TEMPLATE_COORD_SCALE_UNIT
TEMPLATE_EXT_OBSERVING_CONTEXT
```

The two new axes are admitted because their source classes are allowed by the
source-candidate audit:

```text
CoordinateConventionOnly
PublishedExternalMetadata
```

## Still Excluded

```text
TEMPLATE_M_PARENT_MORPHOLOGY
TEMPLATE_EXT_SOURCE_FAMILY
```

`TEMPLATE_M_PARENT_MORPHOLOGY` remains excluded because direct morphology
support would collapse the route back into a morphology-null duplicate.
`TEMPLATE_EXT_SOURCE_FAMILY` remains excluded in this first expanded packet
because previous failures were family-dominated.

## Claim Boundary

Allowed statement:

> An expanded target-blind parent-operator domain has been frozen for future
> no-scoring object construction.

Forbidden statement:

> This packet constructs a covariance object, authorizes scoring, or validates
> Tau Core.
