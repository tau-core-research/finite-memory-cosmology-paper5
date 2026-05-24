# P-TauCov Domain-Metric Candidate Audit

Freeze ID: `P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_v1`

Status: `P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_NO_PASSING_METRIC_NO_SCORING`

## Purpose

This target-blind audit tests a fixed set of domain-metric candidates
derived from coordinate convention and the projection-essential parent
action Hessian. It does not use target residuals, score outcomes, fitted
alpha behavior, or winning nulls.

The audit asks only whether any candidate metric gives active branch
coordinates enough support in the frozen common clean subspace before
empirical scoring.

## Candidate Results

| Metric candidate | min branch support | max branch support | projection support | support gate |
|---|---:|---:|---:|---:|
| `PARENT_HESSIAN_ABS_COUPLING_METRIC` | `0.04705494041373014` | `0.051593557794545664` | `0.05318703611945719` | `False` |
| `ACTIVE_SECTOR_ABS_COUPLING_METRIC` | `0.04705494041373014` | `0.051593557794545664` | `0.05318703611945719` | `False` |
| `PARENT_HESSIAN_PSD_SQUARE_METRIC` | `0.010791558780921445` | `0.01787140563793571` | `0.08566937761057605` | `False` |
| `ACTIVE_SECTOR_PSD_SQUARE_METRIC` | `0.010791558780921445` | `0.01787140563793571` | `0.08566937761057605` | `False` |
| `IDENTITY_UNIT_DOMAIN_METRIC` | `3.2553021195279366e-16` | `6.914594610948657e-16` | `0.08715747582432105` | `False` |

## Interpretation

Best candidate: `PARENT_HESSIAN_ABS_COUPLING_METRIC` with minimum active-branch support `0.04705494041373014`.

If no candidate passes, the current coordinate/domain inventory is too
poor to produce a parent-domain curvature source by metric update alone.
A richer parent-domain embedding or new admissible coordinate source is
then required before any scorecard.

## Claim Boundary

Allowed statement:

> Target-blind metric candidates have been audited for Q-clean active-branch support.

Forbidden statement:

> A metric is frozen, a Tau signal is constructed, or empirical scoring is authorized.
