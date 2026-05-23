# P-TauCov Dynamical-Stability Status Reconciliation

Freeze ID: `P_TAUCOV_DYNAMICAL_STABILITY_STATUS_RECONCILIATION_v1`

Status:

`P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_ASSEMBLY_READY_PHYSICAL_STABILITY_OPEN_NO_SCORING`

## Purpose

This note separates reduced-Jacobian assembly readiness from physical
stability claims.

## Result

The response/energy split packet and the linear dynamical stability packet
jointly show that the signed response can be embedded in a linearly bounded
one-mode branch dynamics:

[`p_taucov_response_energy_split_packet.md`](p_taucov_response_energy_split_packet.md)

[`p_taucov_linear_dynamical_stability_packet.md`](p_taucov_linear_dynamical_stability_packet.md)

Therefore `DynamicalStability` no longer blocks reduced-Jacobian assembly at
the minimal linear level.

However, nonlinear stability and microscopic UV completion remain open. This
still forbids physical validation claims.

## Claim Boundary

Allowed statement:

> The minimal linear branch dynamics is stable enough for source assembly.

Forbidden statement:

> Nonlinear stability, UV completion, empirical scoring, or Tau Core validation
> has been established.
