# P-TauCov Origin/Scale Rule Freeze

Status: origin/scale rule freeze / no concrete origin values / no concrete
scale values / no coordinate-basis packet / no metric evaluation / no scoring
authorization.

This artifact freezes how future coordinate-basis rows may receive
`origin_value` and `scale_value`. It does not fill the values. The purpose is to
prevent post-hoc normalization choices after residual or score inspection.

## Frozen Rules By Axis Kind

| Axis kind | Origin rule | Scale rule |
| --- | --- | --- |
| `parent` | theory-declared zero | theory-declared unit or predeclared finite unit |
| `branch` | stationary branch reference zero before solving `B_*` | theory-declared branch unit or predeclared finite unit |
| `morphology` | predeclared morphology baseline zero or center | predeclared morphology unit |
| `projection` | identity-projection reference | unit projection norm |
| `reference` | coordinate-basis origin if declared, otherwise coordinate center | unit reference scale |
| `scale` | zero log/additive scale reference | declared unit scale |
| `family` | categorical reference baseline declared before scoring | unit indicator scale |
| `context` | external context baseline declared before scoring | published unit or unit indicator scale |

## Forbidden Inputs

The origin and scale rules must not use:

```text
held-out residuals;
P5C v3 gains;
OOS DeltaNLL;
family-localized covariance score;
linear specificity pass/fail;
post-hoc support localization.
```

## Claim Boundary

Allowed statement:

```text
The origin/scale selection rules are frozen.
```

Forbidden statement:

```text
Concrete origin/scale values or a coordinate-basis packet are frozen.
```
