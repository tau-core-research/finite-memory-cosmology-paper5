# P-TauCov Linear Specificity Threshold Freeze

Status: threshold freeze / no metric evaluation / no linear freeze / no
scoring authorization.

This artifact freezes the prescore thresholds for
`P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_v1`. The thresholds are declared before any
linear-specificity metric is evaluated and before any `delta_C_Tau` matrix is
generated.

## Frozen Thresholds

| Metric | Frozen threshold | Failure meaning |
| --- | --- | --- |
| `M1_NONCOMMUTATOR_SHARE` | `>=0.10` | Candidate collapses toward commuting morphology. |
| `M2_EFFECTIVE_RANK` | `0.10 <= effective_rank_fraction <= 0.85` | Candidate is rank/diagonal collapse or fully generic spread. |
| `M3_SUPPORT_ENTROPY` | `0.25 <= normalized_entropy <= 0.85` | Support is single-family proxy or uniform-noise-like. |
| `M4_LABEL_PROXY_OVERLAP` | `<=0.35` | Support is too close to known family/clock labels. |
| `M5_NULL_SEPARATION_MARGIN` | `>0` against each null and `>=0.05` against strongest null | Generic linear nulls are as specific as candidate. |
| `M6_OUTCOME_LEAKAGE_CERTIFICATE` | `must_be_true` | Outcome leakage contaminates the audit. |

## Decision Rule

The strictly linear candidate can advance to a concrete freeze only if all
thresholds pass. Failing any threshold blocks the strictly linear freeze and
routes the program to either rejection or a separately frozen minimal nonzero
term:

```text
lambda_B fixed nonzero
or epsilon_P fixed nonzero
```

## Claim Boundary

Allowed statement:

```text
The linear-specificity thresholds are frozen before metric evaluation.
```

Forbidden statement:

```text
The frozen thresholds show that the strictly linear candidate passes.
```
