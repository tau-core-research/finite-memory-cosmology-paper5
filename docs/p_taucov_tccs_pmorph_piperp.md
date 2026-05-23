# P-TauCov TCCS P_morph And Pi_perp Freeze

Freeze ID: `P_TAUCOV_TCCS_PMORPH_PIPERP_v1`

Status:

`P_TAUCOV_TCCS_PMORPH_PIPERP_FROZEN_NO_OBJECT_NO_SCORING`

## P_morph Convention

The morphology/projection readout operator is frozen as the parent-coordinate
projector onto:

```text
M_PARENT_MORPHOLOGY
P_MORPH_PROJECTION
```

This is a convention freeze, not a score result.

## Pi_perp Convention

`Pi_perp` is the 36-row orthogonal complement to the embedded morphology and
projection columns under the frozen TCCS parent-to-score embedding.

## Diagnostics

| Quantity | Value |
|---|---:|
| parent P_morph symmetry error | `0.0` |
| parent P_morph idempotence error | `0.0` |
| Pi_perp symmetry error | `0.0` |
| Pi_perp idempotence error | `5.551115123125783e-16` |
| Pi_perp rank | `34` |
| nuisance leakage norm | `5.592547263369759e-16` |

## Claim Boundary

Allowed statement:

> The TCCS morphology operator convention and projection/morphology-orthogonal complement have been frozen without score access.

Forbidden statement:

> These matrices construct a TCCS object, authorize scoring, or produce a Tau signal.
