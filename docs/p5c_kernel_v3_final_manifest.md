# P5C Kernel v3 Final Manifest

Status: `P5C_KERNEL_V3_SCORING_AUTHORIZED`

This manifest authorizes the v3 primary PSD covariance-deformation scorecard.
It does not claim survival and does not contain score results.

## Primary

- kernel: `K_BSTAR_P5C_v3_RESIDUAL_COMPLEX_ORIENTATION_PSD_PROJECTION`
- mode: `PSD_COVARIANCE_DEFORMATION`

## Diagnostic Only

- kernel: `K_BSTAR_P5C_v3_RESIDUAL_COMPLEX_ORIENTATION`
- mode: `SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY`
- survival claim allowed: `false`

## Authorization

- kernel freeze valid: `true`
- scoring mode freeze valid: `true`
- folds/nulls/covariance/df/survival/kill policies fixed: `true`
- target residual used in freeze: `false`
- score used in freeze: `false`

## Forbidden

- promoting the signed diagnostic to survival;
- switching the primary mode after scoring;
- using PSD/signed comparison after scoring to choose the final claim.

## Next Allowed Command

```bash
python3 scripts/run_p5c_kernel_covariance_scorecard_v3.py
```
