# P-TauCov Common-Clean-Subspace Support Audit

Freeze ID: `P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_v1`

Status:

`P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_NO_PASSING_CANDIDATE_NO_SCORING`

## Purpose

This target-blind audit tests whether existing parent-derived candidate
matrices have non-negligible support in the frozen common clean subspace:

```text
Q_clean = Pi_bal Pi_perp Pi_bal
K_clean = Q_clean K_parent Q_clean
```

It does not inspect target residual scores and does not authorize empirical
scoring.

## Candidate Results

| Candidate | Status | Support retention | Projection leakage | Max family share | Diagonal share | Gates |
|---|---|---:|---:|---:|---:|---:|
| `PROJECTION_ESSENTIALITY_HESSIAN` | `CANDIDATE_SUPPORT_FAIL_NO_SCORING` | `9.35244340279955e-17` | `0.4793118655380942` | `0.1592371108597318` | `0.0609727295490827` | `3 / 5` |
| `MINIMAL_GLOBAL_PARENT_ACTION_HESSIAN` | `CANDIDATE_SUPPORT_FAIL_NO_SCORING` | `9.35244340279955e-17` | `0.4793118655380942` | `0.1592371108597318` | `0.0609727295490827` | `3 / 5` |
| `PARENT_HESSIAN_COMMUTATOR_OBJECT` | `CANDIDATE_SUPPORT_FAIL_NO_SCORING` | `6.850185161725854e-17` | `0.37535976849268027` | `0.16378343062892498` | `0.03645102335448647` | `3 / 5` |
| `S_REST_NO_LEAKAGE_HESSIAN` | `CANDIDATE_SUPPORT_FAIL_NO_SCORING` | `3.83614836657147e-31` | `0.4481361930201937` | `0.2970682976101406` | `0.1265565130511457` | `2 / 5` |
| `TCCS_TRANSFER_CURVATURE` | `CANDIDATE_SUPPORT_FAIL_NO_SCORING` | `0.00836108135986166` | `0.9531846889181018` | `0.35896657810231236` | `0.0719552651423933` | `3 / 5` |

## Interpretation

Passing this audit would only mean that a candidate is worth considering for a
future frozen scoring manifest. It would not be a Tau validation claim.

If no candidate passes, the current parent-curvature inventory does not yet
provide a clean Tau-specific support object.

## Claim Boundary

Allowed statement:

> Existing parent-derived candidates have been audited for common-clean-subspace support without target residual scoring.

Forbidden statement:

> This audit validates Tau Core, authorizes empirical scoring, or establishes empirical survival.
