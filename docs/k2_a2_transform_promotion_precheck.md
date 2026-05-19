# K2 A2 Transform Promotion Precheck

Status: scorecard-rerun precheck; no measurement-validation claim.

This file freezes the SN/BAO transform policy needed to rerun the locked A2 scorecard.
It does not change the K2 kernel, does not allow rho>4, and does not refit K1.

## Frozen Vector Policy

```text
r_SN  = D_SN * B_SN * (I - 1*w_SN^T) * (mu_obs - mu_CMB_baseline)
r_BAO = log(q_obs / q_CMB_baseline)
y_split = L_SN*r_SN - L_BAO*r_BAO
```

## Boundary

The transform can support a scorecard rerun if all rows pass. It still cannot be used as a measurement-validation claim until the rerun and public benchmark interpretation are completed.
