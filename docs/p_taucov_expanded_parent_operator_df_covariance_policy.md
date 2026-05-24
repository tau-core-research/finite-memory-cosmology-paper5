# P-TauCov Expanded Parent-Operator DF/Covariance Policy

Status: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING`.

The future primary scorecard, if authorized, is a one-parameter covariance
deformation test:

```math
C = C_0 + \alpha K_{\rm expanded}.
```

The scale/context axes are frozen source axes, not fitted parameters, so
information-criterion accounting remains `df=1`. This policy does not
authorize scoring.
