# P-TauCov PB Interaction Object Preflight

Freeze ID: `P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_v1`

Status: `P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_BLOCKED_NO_SCORING`

## Purpose

This packet tests whether the frozen `P*B` interaction coordinate can
support a later covariance-object freeze without becoming a diagonal,
single-family, or cleaner-generated shortcut.

It does not authorize empirical scoring.

## Candidate Results

| Object candidate | class | Q-clean matrix support | max family block share | diagonal share | parent source allowed | overall preflight |
|---|---|---:|---:|---:|---:|---:|
| `PB_QCLEAN_RESTRICTED_OUTER_PRODUCT` | `CLEANED_DIAGNOSTIC_ONLY` | `0.9998091089743355` | `0.15536750291678883` | `0.09782163368415354` | `False` | `False` |
| `PB_OUTER_PRODUCT_PSD` | `PSD_COVARIANCE_CANDIDATE` | `0.18011059272762248` | `0.1111111111111111` | `0.05728160390053828` | `True` | `False` |

## Interpretation

Best candidate: `PB_QCLEAN_RESTRICTED_OUTER_PRODUCT` with Q-clean matrix support `0.9998091089743355`.

The cleaned diagnostic is reported to quantify clean-subspace retention,
but it is explicitly not an admissible parent source by itself. Only an
uncleaned parent-derived object can be promoted in a later freeze packet.

## Links

- [`p_taucov_pb_interaction_coordinate_freeze.md`](p_taucov_pb_interaction_coordinate_freeze.md)
- [`p_taucov_admissible_source_coordinate_extension.md`](p_taucov_admissible_source_coordinate_extension.md)

## Claim Boundary

Allowed statement:

> A frozen `P*B` coordinate has been tested for object-construction readiness.

Forbidden statement:

> A covariance object is frozen, scoring is authorized, or Tau Core is validated.
