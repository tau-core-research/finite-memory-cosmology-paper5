# P-TauCov Covariance Map Declaration

Status: `P_TAUCOV_COVARIANCE_MAP_DECLARED_PASS_NO_SCORING`.

This packet declares the target-blind map that turns a Tau response
object into a covariance-deformation candidate. It is a protocol
declaration only; it does not run an empirical scorecard.

## Declared Map

For a frozen response object `T`, define

```math
D_M C[T] = \frac{TT^{\mathsf T}}{\|TT^{\mathsf T}\|_F}.
```

This makes the covariance deformation symmetric and positive
semidefinite by construction. The map is declared before scoring and
does not use target residuals, likelihood improvements, alpha
behavior, or dominant-family information.

## Key Numbers

- map dimension: `2`
- minimum eigenvalue: `-1.3322676295501878e-17`
- maximum eigenvalue: `1.0`
- Frobenius norm: `1.0`
- gates passed: `6/6`

## Claim Boundary

Allowed: a reproducible target-blind covariance-map rule has been
declared.

Forbidden: this is not a covariance scorecard, not survival, and not
measurement validation.
