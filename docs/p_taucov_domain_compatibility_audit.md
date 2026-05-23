# P-TauCov Domain-Compatibility Audit

Freeze ID: `P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_v1`

Status:

`P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_PASS_NO_SCORING`

## Purpose

This target-blind audit checks whether the frozen projection-orthogonal cleaner
`Pi_perp` and the frozen branch/family balance cleaner `Pi_bal` behave as
compatible operators in the same score-space geometry.

It does not inspect target residual scores and does not authorize empirical
scoring.

## Metrics

| Quantity | Value |
|---|---:|
| rows | `36` |
| rank `Pi_perp` | `34` |
| rank `Pi_bal` | `31` |
| rank common cleaner `Pi_bal Pi_perp Pi_bal` | `31` |
| trace common cleaner | `30.091438948812087` |
| relative commutator norm | `0.012555596849346958` |
| relative order-difference norm | `0.011250508343623337` |
| passed gates | `7 / 7` |

## Interpretation

If this audit fails, a future TCCS/P-TauCov object must not treat projection
orthogonality and branch balance as independent post-processing filters. The
operators must either be derived from a common parent domain, or their
non-commutation must be frozen as the observable itself before scoring.

## Claim Boundary

Allowed statement:

> The compatibility of the frozen cleaning operators has been audited without target residual scoring.

Forbidden statement:

> This audit validates a Tau signal, authorizes scoring, or proves physical domain compatibility.
