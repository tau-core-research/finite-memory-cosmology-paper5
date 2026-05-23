# P-TauCov Epsilon-P3 Branch-Support Freeze

Status: `FROZEN_BRANCH_SUPPORT_NO_SCORING`.

This artifact freezes concrete branch support for the epsilon-P3 P-TauCov
candidate. The support is derived only from the frozen P3 covariance response:

```text
delta_C_tau = P3 P3^T
W_branch(i,j) = |delta_C_tau(i,j)| / sum_ab |delta_C_tau(a,b)|
q_branch = 0.8
Omega_branch = smallest W_branch-ranked set carrying at least q_branch mass
```

## Result

```text
SelectedCells: 13
SelectedMass: 0.833333333333
LabelOrConventionMass: 0
BranchSupportSource: delta_C_Tau_only
PTauCovScoringAuthorized: false
```

## Claim Boundary

Allowed statement:

```text
The epsilon-P3 branch support is frozen from delta_C_tau only.
```

Forbidden statement:

```text
This support freeze is an empirical P-TauCov score, survival result, or Tau
signal.
```
