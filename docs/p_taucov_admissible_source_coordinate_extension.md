# P-TauCov Admissible Source-Coordinate Extension

Freeze ID: `P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_v1`

Status: `P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_HAS_PREFLIGHT_COORDINATE_NO_SCORING`

## Why This Gate Exists

The domain-metric audit showed that changing the metric on the current
eight-coordinate embedding is not enough. The next admissible route must
therefore add a richer parent-domain/source coordinate before any new
P-TauCov object can be frozen.

This packet defines which coordinate extensions are admissible and audits
a first small set of target-blind nonlinear candidates derived from the
already declared parent action/source structure.

## Admissibility Rule

- The coordinate must have parent-domain provenance.
- It must not use target residuals, score outcomes, fitted alpha behavior, or winning nulls.
- It must not be a direct family, morphology, or projection-null label proxy.
- It must pass Q-clean support, family-balance, and diagonal-control preflight before any scoring packet.
- This packet never authorizes empirical scoring by itself.

## Candidate Preflight

| Candidate | class | Q-clean support | max family energy share | diagonal share if outer product | support gate | family gate | diagonal gate | overall preflight |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `COORD_PB_INTERACTION` | `INTERACTION_COORDINATE` | `0.42439438347794184` | `0.3333333333333333` | `0.05728160390053826` | `True` | `True` | `True` | `True` |
| `COORD_P_BRANCH_SOURCE_CONTRAST` | `CURVATURE_COORDINATE` | `0.3740746004550841` | `0.9998014499626684` | `0.17041705713619937` | `True` | `False` | `False` | `False` |
| `COORD_PPHI_INTERACTION` | `INTERACTION_COORDINATE` | `0.08716180113820325` | `0.33359801416405344` | `0.05669138734173317` | `False` | `True` | `True` | `False` |
| `COORD_B2_BRANCH_COUNTERTERM` | `INTERACTION_COORDINATE` | `3.838406449890678e-16` | `0.3333333333333333` | `0.027777777777777776` | `False` | `True` | `True` | `False` |
| `COORD_SCALE_OBSERVER_CONTEXT` | `SOURCE_CONTEXT_COORDINATE` | `0.0` | `1.0` | `1.0` | `False` | `False` | `False` | `False` |

## Interpretation

Best candidate: `COORD_PB_INTERACTION` with Q-clean support `0.42439438347794184`.

A passing candidate would only become a candidate for a later coordinate
freeze packet. It would not establish a signal and would not authorize a
survival claim.

## Links

- [`p_taucov_parent_domain_curvature_source_requirement.md`](p_taucov_parent_domain_curvature_source_requirement.md)
- [`p_taucov_domain_metric_update_rule.md`](p_taucov_domain_metric_update_rule.md)
- [`p_taucov_domain_metric_candidate_audit.md`](p_taucov_domain_metric_candidate_audit.md)

## Claim Boundary

Allowed statement:

> Target-blind parent-derived coordinate extensions have been screened for Q-clean support.

Forbidden statement:

> A new Tau covariance object is frozen, scoring is authorized, or Tau Core is validated.
