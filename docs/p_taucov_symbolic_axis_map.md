# P-TauCov Finite-Dimensional Symbolic Axis Map

Status: symbolic axis map / no numeric basis rows / no matrices / no reference
domain / no metric evaluation / no scoring authorization.

This artifact converts the allowed source classes into a finite-dimensional
symbolic axis map. It declares the kinds of axes a later coordinate-basis packet
may instantiate, but it does not yet provide numerical `origin_value`,
`scale_value`, matrix elements, or a concrete `Phi_0`.

## Symbolic Axes

| Axis | Role | Allowed source class |
| --- | --- | --- |
| `PHI_PARENT_SOURCE` | Parent perturbation coordinate `delta Phi`. | Tau-side symbolic definition |
| `B_BRANCH_RESPONSE` | Relaxed branch response coordinate `B_*(Phi)`. | Tau-side symbolic definition |
| `M_PARENT_MORPHOLOGY` | Parent morphology carrier `M_parent(Phi,B)`. | Tau-side symbolic definition |
| `P_MORPH_PROJECTION` | Fixed morphology projection map `P_morph`. | Tau-side symbolic definition |
| `COORD_ORIGIN_CENTER` | Origin or center convention for `Phi_0` selection. | Coordinate convention only |
| `COORD_SCALE_UNIT` | Target-blind unit or normalization convention. | Coordinate convention only |
| `EXT_SOURCE_FAMILY` | Citable external source-family or observing-context tag. | Published external metadata |
| `EXT_OBSERVING_CONTEXT` | Citable target-blind observing-context descriptor. | Published external metadata |

## Guardrails

This map must not use:

```text
P5C v3 gains;
held-out residuals;
OOS DeltaNLL;
post-hoc family localization;
metric pass/fail outcomes.
```

## What This Enables

The next artifact may derive concrete `coordinate_basis.csv` rows from this map.
That future packet still requires provenance, hashes, a leakage audit, finite
origin and scale values, and manifest flags declaring no outcome, residual,
score, or post-scoring localization use.

## Claim Boundary

Allowed statement:

```text
A finite-dimensional symbolic axis map is declared.
```

Forbidden statement:

```text
The concrete coordinate basis, matrices, or P-TauCov covariance response are
available.
```
