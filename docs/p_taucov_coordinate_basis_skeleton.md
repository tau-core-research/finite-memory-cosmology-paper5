# P-TauCov Coordinate-Basis Skeleton

Status: template only / no concrete coordinate-basis packet / no frozen
`Phi_0` / no reduced domain / no metric evaluation / no scoring authorization.

This artifact derives a non-authorizing coordinate-basis skeleton from the
finite-dimensional symbolic axis map. The file is intentionally stored under
`data/p_taucov/templates/`, not at the packet path
`data/p_taucov/linear/coordinate_basis.csv`.

## Template File

```text
data/p_taucov/templates/coordinate_basis_skeleton.csv
```

The template uses the schema columns expected by the future packet, but the
numeric fields are placeholders:

```text
origin_value = TO_BE_FILLED_BY_TARGET_BLIND_PACKET
scale_value  = TO_BE_FILLED_BY_TARGET_BLIND_PACKET
```

Therefore this skeleton must not be accepted by the coordinate-basis packet
validator.

## Guardrail

The skeleton is useful only as a derivation aid. It does not authorize:

```text
coordinate-basis packet acceptance;
reference-domain selection;
matrix construction;
linear specificity metric evaluation;
P-TauCov scoring.
```

## Claim Boundary

Allowed statement:

```text
A coordinate-basis skeleton template has been derived from the symbolic axis map.
```

Forbidden statement:

```text
The concrete coordinate basis has been supplied, accepted, or frozen.
```
