# P-TauCov TCCS Transfer-Curvature Preflight

Freeze ID: `P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_v1`

Status:

`P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_FAIL_NO_SCORING`

## Purpose

This artifact tests the no-go-corrected TCCS object class at pre-score level:

```text
T_transfer = Pi_perp [H,P] P
K_curv = Pi_perp [H,P] P [H,P]^T Pi_perp
```

It does not use target residuals and does not authorize empirical scoring.

## Preflight Metrics

| Quantity | Value |
|---|---:|
| transfer norm | `0.6110337150679959` |
| curvature norm | `0.37300580613878537` |
| post-Pi_perp curvature norm | `0.37300580613878537` |
| post-Pi_bal curvature norm | `0.00047223731087847354` |
| retained norm | `0.0012660320646664862` |
| max family energy share | `0.35896657810214627` |
| diagonal energy share | `0.07195526514120916` |
| symmetry error | `1.8352032675646168e-14` |
| minimum eigenvalue | `-1.0984676710837948e-13` |
| Pi_perp leakage norm | `0.9531846889181036` |

## Claim Boundary

Allowed statement:

> The no-go-corrected transfer-curvature object has been inspected at pre-score level.

Forbidden statement:

> The transfer-curvature object has survived empirical scoring or validated Tau Core.

## Interpretation

This is a negative structural result, not a failed empirical score.

The corrected object class is not empty:

```text
transfer norm = 0.6110337150679959
curvature norm = 0.37300580613878537
```

However, the object does not remain clean after the full branch/perp discipline:

```text
balanced retained norm = 0.0012660320646664862
Pi_perp leakage norm   = 0.9531846889181036
```

The parent-side transfer exists, but the present transfer-curvature object does
not place enough support into the clean projection-orthogonal, branch-balanced
subspace. The result therefore blocks scoring and sharpens the theory.

## Theory Feedback

The follow-up domain-compatibility audit shows that `Pi_perp` and `Pi_bal` are
not the primary problem as a cleaner pair. They are sufficiently compatible at
score-space level. A future candidate must therefore:

1. derive a parent-side curvature object with non-negligible energy in
   `range(Pi_bal Pi_perp Pi_bal)`; and
2. keep projection leakage low before any target score is inspected.

Cleaner audit:

[`p_taucov_domain_compatibility_audit.md`](p_taucov_domain_compatibility_audit.md)
