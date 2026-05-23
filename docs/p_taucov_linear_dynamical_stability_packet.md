# P-TauCov Linear Dynamical Stability Packet

Status: `P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_PASS_NO_SCORING`.

This packet supplies the minimal linear dynamics needed to interpret
the signed reduced response as compatible with a stable microscopic
branch mode.

## Minimal Dynamics

```math
L = \frac{1}{2}\dot B^2 - \frac{1}{2}B^2 - BJ.
```

At the stationary branch value `B_*=-J`, the fluctuation `b=B-B_*`
obeys

```math
\ddot b + b = 0.
```

Thus the microscopic branch fluctuation is linearly bounded while
the static elimination still gives the signed response
`E_eff(J)=-J^2/2`.

## Key Numbers

- minimum kinetic eigenvalue: `1.0`
- minimum stiffness eigenvalue: `1.0`
- minimum omega squared: `1.0`
- gates passed: `6/6`

## Claim Boundary

Allowed: the minimal branch response can be embedded in a linearly
stable one-mode microscopic dynamics.

Forbidden: this is not nonlinear stability, not a UV completion, not
a covariance scorecard, and not measurement validation.
