# P-TauCov Q-Native Route Priority Note

Freeze ID: `P_TAUCOV_Q_NATIVE_ROUTE_PRIORITY_NOTE_v1`

Status:

`P_TAUCOV_Q_NATIVE_ROUTE_PRIORITY_RECOMMENDED_NO_OBJECT_NO_SCORING`

## Purpose

This note ranks the registered Q-native parent-curvature routes after the
negative common-clean-subspace support audit. It is a theory-prioritization
artifact only. It does not construct a candidate and does not authorize scoring.

## Ranking

| Rank | Route | Reason |
|---:|---|---|
| 1 | `QN_ROUTE_4_BRANCH_RESPONSE_CURVATURE` | Closest to the original P-TauCov theory: branch response is the place where Tau backreaction should enter before morphology readout. It can be constrained by the reduced branch equation rather than by empirical covariance. |
| 2 | `QN_ROUTE_3_COMPATIBILITY_CURVATURE` | Mathematically clean and Tau-specific if `D_parent` is derived, but higher risk of becoming an abstract operator trick if `D_parent` is not fixed by parent dynamics. |
| 3 | `QN_ROUTE_2_BOUNDARY_CURVATURE` | Potentially deep if a true parent boundary/defect/domain wall exists, but currently less connected to the P-TauCov empirical branch machinery. |
| 4 | `QN_ROUTE_1_CONSTRAINED_HESSIAN_RESIDUE` | Natural continuation of old Hessian attempts, but the support audit already shows old Hessian inventory projects poorly into `Q_clean`; high risk of repeating the same failure. |

## Recommended Next Route

The next concrete derivation should start with:

```text
QN_ROUTE_4_BRANCH_RESPONSE_CURVATURE
```

Target structure:

```text
L_B^red delta B = -D_Phi F_B[delta Phi]
J_response = Q_clean D_B M_proj (L_B^red)^(-1) D_Phi F_B
K_Q = J_response J_response^T
```

The important distinction is that `Q_clean` must enter during construction of
the response operator, not only after an old object has already been built.

## Required Next Artifact

```text
docs/p_taucov_q_native_branch_response_curvature_protocol.md
scripts/build_p_taucov_q_native_branch_response_curvature_preflight.py
scripts/validate_p_taucov_q_native_branch_response_curvature_preflight.py
```

The preflight must remain target-blind and no-scoring.

## Claim Boundary

Allowed statement:

> Branch-response curvature is the recommended next Q-native route because it is closest to the Tau backreaction structure and avoids reusing failed global Hessian candidates.

Forbidden statement:

> The priority note validates Tau Core, constructs a scoreable object, or authorizes empirical scoring.
