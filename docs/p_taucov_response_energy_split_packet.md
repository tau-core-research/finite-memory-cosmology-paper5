# P-TauCov Response/Energy Split Packet

Status: `P_TAUCOV_RESPONSE_ENERGY_SPLIT_PASS_NO_SCORING`.

This packet implements Route A from the stability-resolution note.
It separates the stable microscopic branch energy from the signed
effective response obtained after branch elimination.

## Minimal Route-A Form

```math
E_{\rm micro}(B;J)=\frac{1}{2}B^2 + BJ,
```

with source/projection channel

```math
J = \Phi + 2P.
```

The physical branch amplitude has positive Hessian:

```math
\partial_B^2 E_{\rm micro}=1>0.
```

Eliminating `B` gives the signed Schur response

```math
E_{\rm eff}(J)=-\frac{1}{2}J^2.
```

Thus an indefinite or negative effective response is compatible with
a positive microscopic branch energy. The active witness should
therefore be treated as a response operator, not as the energy
Hessian itself.

## Key Numbers

- minimum microscopic energy eigenvalue: `1.0`
- minimum effective response eigenvalue: `-5.0`
- maximum effective response eigenvalue: `0.0`
- gates passed: `6/6`

## Claim Boundary

Allowed: a positive branch-energy toy form can generate a signed
effective response after branch elimination.

Forbidden: this is not a full dynamical stability theorem, not a
covariance scorecard, and not measurement validation.
