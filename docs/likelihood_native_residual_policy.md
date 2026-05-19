# Likelihood-Native Residual Policy

Status: residual blockers are resolved for a locked rerun candidate. Measurement validation remains closed.

## Policy Summary

- Baseline: SOURCE_SPLIT_LIKELIHOOD_NATIVE_CMB_ONLY_BASELINE_V1
- H0: 67.060759
- OmegaM: 0.31779326
- rd_mpc: 147.30766
- Resolved residual contracts: 6/6
- Same-sample offset used: False
- Measurement validation allowed: False

## Policies

### SN_RAW_CMB_ONLY_NO_SAME_SAMPLE_OFFSET_V1

- Class: sn_residual_policy
- Resolves: RDEF_SN_1_OBSERVABLE;RDEF_SN_2_OFFSET_POLICY
- Definition: r_SN = MU_SH0ES - mu_CMB_only_LCDM(z)
- Rerun candidate: True
- Residual risk: SN absolute-magnitude/nuisance treatment is fixed by using the public distance-modulus table and external baseline; no same-sample centering is used
- Next action: propagate through declared L_SN and joint covariance; keep nuisance caveat in report

### BAO_LOG_CMB_ONLY_RD_FIXED_V1

- Class: bao_residual_policy
- Resolves: RDEF_BAO_1_OBSERVABLE;RDEF_BAO_2_RS_POLICY
- Definition: r_BAO = log(observed / prediction_CMB_only_LCDM) for DH/DM/DV over rs
- Rerun candidate: True
- Residual risk: BAO residual amplitude depends on externally frozen CMB-only rd policy
- Next action: propagate through declared L_BAO and joint covariance; do not refit rd

### LSN_DECLARED_LINEAR_PROJECTION_V1

- Class: sn_transform_policy
- Resolves: RDEF_SN_3_GRID_TRANSFORM
- Definition: use predeclared L_SN linear projection matrix on raw SN residual vector
- Rerun candidate: True
- Residual risk: projection matrix is declared for candidate rerun but still requires final covariance adjudication
- Next action: rerun source-split vector with this L_SN and report route as candidate only

### LBAO_DECLARED_LINEAR_PROJECTION_V1

- Class: bao_transform_policy
- Resolves: RDEF_BAO_3_GRID_TRANSFORM
- Definition: use predeclared L_BAO linear projection matrix on BAO log residual vector
- Rerun candidate: True
- Residual risk: projection matrix is declared for candidate rerun but still requires final covariance adjudication
- Next action: rerun source-split vector with this L_BAO and report route as candidate only

## Claim Boundary

The locked A2 prediction is unchanged. These policies only define the residual route for the next candidate rerun.
