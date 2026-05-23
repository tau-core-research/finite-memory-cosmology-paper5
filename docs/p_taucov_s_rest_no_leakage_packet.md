# P-TauCov S_rest No-Leakage Packet

Status: rest-sector embedding packet / no empirical scorecard / no survival
claim.

The minimal active scaffold leaves `S_rest` unspecified. This packet declares a
minimal rest-sector completion that stabilizes the inactive complement and does
not leak forbidden coordinates into the projection-essential witness sector.

## Rest Sector

The finite parent cell is split into:

```text
active:    Phi, B, P
gauge:     coordinate-origin, coordinate-scale
forbidden: M, external-family, external-observing-context
```

The rest sector is:

```math
S_{\rm rest}
=
\frac{\mu_g}{2}\left(G_1^2+G_2^2\right)
+
\frac{\mu_f}{2}\left(M^2+F^2+C^2\right),
```

with fixed positive unit masses:

```text
mu_g = 1
mu_f = 1
```

There are no cross terms between active and inactive coordinates. Therefore the
active scaffold Hessian is preserved and the forbidden sector cannot re-enter
the witness.

## What This Resolves

Resolved:

```text
S_REST
NO_FORBIDDEN_REST_SECTOR_LEAKAGE
```

Not resolved:

```text
REFERENCE_BACKGROUND_STABILITY
COVARIANCE_MAP
```

The active witness sector is not claimed to be a complete positive-energy
sector. The rest packet only stabilizes the inactive complement and prevents
leakage.

## Claim Boundary

Allowed:

```text
S_rest is declared as a no-leakage positive quadratic complement.
```

Forbidden:

```text
The full Tau Core action is stable, complete, or empirically validated.
```
