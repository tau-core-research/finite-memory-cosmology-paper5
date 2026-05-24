# P-TauCov Domain-Metric Update Rule

Rule ID: `P_TAUCOV_DOMAIN_METRIC_UPDATE_RULE_v1`

Status: `P_TAUCOV_DOMAIN_METRIC_UPDATE_RULE_DEFINED_NO_METRIC_NO_SCORING`

## Motivation

The embedding/Q-clean audit showed that the current parent-to-score
embedding places the active branch coordinates almost entirely outside
the frozen common clean subspace. This blocks parent-domain curvature
source construction before any empirical score is inspected.

The remedy cannot be an arbitrary metric chosen to make the support
large. The metric update must be a declared parent-domain object with
target-blind provenance.

## Rule Table

| Requirement | Policy | Definition |
|---|---:|---|
| `DMR-R1_PARENT_METRIC_ORIGIN` | `required` | Any metric update must be derived from declared parent-domain structure: coordinate provenance, source covariance declared before target residuals, self-adjoint-domain pairing, or symmetry/constraint algebra. |
| `DMR-R2_NO_TARGET_OUTCOME_INPUT` | `forbidden` | The metric may not use held-out residuals, OOS DeltaNLL, fitted alpha behavior, winning nulls, or post-score family/context localization. |
| `DMR-R3_BRANCH_SUPPORT_GATE` | `>=0.20` | Before scoring, active branch coordinates must have non-negligible support in the common clean subspace under the updated metric/embedding. |
| `DMR-R4_METRIC_POSITIVE_AND_BOUNDED` | `required` | The domain metric must be symmetric positive semidefinite or explicitly indefinite with a declared Krein/signature convention; condition number policy must be frozen. |
| `DMR-R5_NO_QCLEAN_AS_SOURCE` | `forbidden_shortcut` | Q_clean may audit the metric-induced embedding but must not be used as the definition of the metric source. |
| `DMR-R6_NULL_GAUGE_COMPATIBILITY` | `required` | The updated metric must preserve the frozen null/gauge/forbidden exclusions or explicitly declare a new target-blind reference-domain packet. |
| `DMR-R7_COMPARATOR_FREEZE_REQUIRED` | `required` | Any metric-induced candidate must face morphology-null, projection-null, shuffled-support, generic smooth, and diagonal comparators frozen before scoring. |

## Forbidden Shortcut

The following move is not allowed:

```text
choose G_domain so that Q_clean E(G_domain) branch is large
```

unless `G_domain` has an independent parent-domain derivation or a
target-blind provenance source that was declared before scoring.

## Next Gate

A future artifact may define a concrete `G_domain` or revised embedding
only if it also declares:

- parent-domain source of the metric;
- null/gauge compatibility;
- positivity or signature convention;
- condition-number policy;
- target-blind support audit command;
- forbidden inputs certificate.

## First Candidate Audit

The first target-blind candidate audit tested identity, parent-Hessian absolute
coupling, parent-Hessian PSD-square, and active-sector variants:

[`p_taucov_domain_metric_candidate_audit.md`](p_taucov_domain_metric_candidate_audit.md)

No candidate passed. The best parent-Hessian absolute-coupling metric raised
the minimum active-branch `Q_clean` support only to about `0.047`, below the
frozen `0.20` threshold. This indicates that the current finite coordinate
inventory is likely too poor for metric update alone; a richer admissible
embedding coordinate or parent-domain source is required.

## Claim Boundary

Allowed statement:

> A target-blind rule now constrains how a parent-domain metric or embedding may be revised after the Q-clean support failure.

Forbidden statement:

> This rule defines a metric, constructs a Tau signal, or authorizes empirical scoring.
