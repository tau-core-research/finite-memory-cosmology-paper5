# P-TauCov Expanded Parent-Operator Source Packet

Freeze ID: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_PACKET_v1`

Status:

`P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_READY_NO_SCORING`

## Purpose

This packet freezes the first target-blind parent-side operator/source rule on
the expanded five-coordinate active domain. It does not construct a covariance
candidate and does not authorize scoring.

## Source Rule

The core `Phi/B/P` block inherits the local projection-essential parent-action
normal form:

```text
Phi -- P : -1
B   -- P : -2
B diagonal counterterm : -1/2
```

The two new non-outcome axes enter by role:

```text
SCALE_CONTEXT:
  SCALE -- Phi : +1
  SCALE -- B   : +1
  SCALE -- P   : +1

OBSERVING_CONTEXT:
  CONTEXT -- Phi : +1
  CONTEXT -- P   : -1
```

The source-family axis and direct parent-morphology axis remain excluded.

## Diagnostics

- active coordinate support count: `5`
- nonzero entries: `15`
- source Frobenius norm: `4.5`
- forbidden leakage norm: `0.0`
- gates passed: `7/7`

## Claim Boundary

Allowed statement:

> A target-blind expanded parent-side operator/source rule has been frozen.

Forbidden statement:

> This packet constructs a covariance object, authorizes scoring, or validates
> Tau Core.
