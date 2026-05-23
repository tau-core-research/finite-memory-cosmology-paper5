# P-TauCov Reference-State Status Reconciliation

Freeze ID: `P_TAUCOV_REFERENCE_STATE_STATUS_RECONCILIATION_v1`

Status:

`P_TAUCOV_OPERATIONAL_REFERENCE_STATE_FROZEN_PHYSICAL_STABILITY_OPEN_NO_SCORING`

## Purpose

This note separates two meanings that had been conflated in the blocker list:

1. operational reference/domain freeze for reduced-Jacobian assembly;
2. physical/dynamical stability of the parent background.

## Result

The operational reference state and reduced domain are frozen by:

[`p_taucov_reference_domain_packet.md`](p_taucov_reference_domain_packet.md)

Therefore `ReferenceState` no longer blocks reduced-Jacobian assembly at the
operational level.

However, the physical background stability gate remains open:

[`p_taucov_reference_background_stability_diagnostic.md`](p_taucov_reference_background_stability_diagnostic.md)

and the response/energy split packet only supports a response-operator
interpretation:

[`p_taucov_response_energy_split_packet.md`](p_taucov_response_energy_split_packet.md)

## Claim Boundary

Allowed statement:

> The operational reference/domain package is frozen for source assembly.

Forbidden statement:

> The parent background is physically stable, empirical scoring is authorized,
> or Tau Core has been validated.
