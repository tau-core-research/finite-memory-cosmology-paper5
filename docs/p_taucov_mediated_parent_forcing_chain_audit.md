# P-TauCov Mediated Parent-Forcing Chain Audit

Freeze ID: `P_TAUCOV_MEDIATED_PARENT_FORCING_CHAIN_AUDIT_v1`

Status:

`P_TAUCOV_MEDIATED_PARENT_FORCING_CHAIN_PASS_STABILITY_OPEN_NO_SCORING`

## Purpose

The previous branch-equation audit found that the direct branch forcing
`D_Phi F_B` is zero in the active scaffold. This audit tests the target-blind
alternative allowed by the same action: a mediated chain

```text
Phi -> P_morph -> B
```

It does not authorize scoring and does not claim physical validation.

## Branch Solve

Use the two-coordinate branch vector:

```text
X = (B, P_morph)
```

and solve the linear branch equation:

```text
L_X delta X + D_Phi F_X delta Phi = 0
```

with:

```text
delta X = - L_X^-1 D_Phi F_X delta Phi
```

## Key Numbers

- `D_Phi F_B = 0.0`
- `D_P F_B = -0.6030226891555273`
- `D_Phi F_P = -0.3015113445777636`
- `det(L_X) = -0.36363636363636365`
- `min eig(L_X) = -0.7723372327969429`
- `delta B / delta Phi = -0.4999999999999999`
- `delta P / delta Phi = 0.24999999999999992`

## Interpretation

The direct `Phi -> B` forcing is zero, but the mediated chain is nonzero and
invertible in the current two-coordinate branch block:

```text
delta B / delta Phi = -0.4999999999999999
```

This resolves the branch-forcing route only at the algebraic, target-blind
scaffold level. It does not prove active stability, does not construct
`D_B M_proj`, and does not authorize empirical scoring.

The stability interpretation is handled by the response/energy split packet:

[`p_taucov_response_energy_split_packet.md`](p_taucov_response_energy_split_packet.md)

That packet supports the interpretation that the active witness is a signed
effective response operator rather than the microscopic positive energy
Hessian itself. Full dynamical stability remains open.

## Claim Boundary

Allowed statement:

> The current action scaffold contains a target-blind mediated parent-forcing
> chain from `Phi` through `P_morph` into `B`.

Forbidden statement:

> The full reduced branch-Jacobian is complete, the branch block is physically
> stable, empirical scoring is authorized, or Tau Core has been validated.
