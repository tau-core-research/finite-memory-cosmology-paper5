# Branch-Scatter Independent Calibration Audit

Status: independent preflight calibration only. Measurement validation remains closed.

## Summary

- Passed criteria: 11/11
- Warnings: 0
- Blocked: 0
- Reconstruction-family subset passes: 7/7
- Branch-scatter K2-best cases: 5/5
- Strongest allowed claim: branch-scatter A2 preflight bridge is independently supported by public reconstruction-family responses

## Findings

### FAMILY_SOURCE_ALLOWED

- Status: PASS
- Evidence: RF_PUBLIC_SOURCE_SPLIT_RECONSTRUCTION_FAMILIES allowed for K2 scoring
- Interpretation: independent source-split family input is available

### BRANCH_SCATTER_PREFLIGHT_REGISTERED

- Status: PASS
- Evidence: branch registration status=BRANCH_SCATTER_REGISTERED_AS_PREFLIGHT_SYSTEMATIC_BRIDGE
- Interpretation: branch-scatter route is already registered as preflight bridge

### BRANCH_SCATTER_A2_COMPETITIVE

- Status: PASS
- Evidence: K2 best branch-scatter covariance cases=5/5
- Interpretation: branch-scatter route itself remains K2-supportive

### RECON_SUBSET_ALL_POINTS

- Status: PASS
- Evidence: best=K2_SOURCE_SPLIT_A2_PRIOR_V1; DeltaAIC_A2_minus_K1=-8.215952382108654; DeltaAIC_A2_minus_unit=-4.334350272083348; A2 sign-match=1.0
- Interpretation: locked A2 is independently favored in this reconstruction-family subset

### RECON_SUBSET_LOW_DEPTH

- Status: PASS
- Evidence: best=K2_SOURCE_SPLIT_A2_PRIOR_V1; DeltaAIC_A2_minus_K1=-2.7333499094091422; DeltaAIC_A2_minus_unit=-2.2301183804244076; A2 sign-match=1.0
- Interpretation: locked A2 is independently favored in this reconstruction-family subset

### RECON_SUBSET_MID_DEPTH

- Status: PASS
- Evidence: best=K2_SOURCE_SPLIT_A2_PRIOR_V1; DeltaAIC_A2_minus_K1=-1.0531124810414094; DeltaAIC_A2_minus_unit=-0.5648071331104421; A2 sign-match=1.0
- Interpretation: locked A2 is independently favored in this reconstruction-family subset

### RECON_SUBSET_HIGH_DEPTH

- Status: PASS
- Evidence: best=K2_SOURCE_SPLIT_A2_PRIOR_V1; DeltaAIC_A2_minus_K1=-4.429489991658104; DeltaAIC_A2_minus_unit=-1.5394247585484997; A2 sign-match=1.0
- Interpretation: locked A2 is independently favored in this reconstruction-family subset

### RECON_SUBSET_MID_HIGH_DEPTH

- Status: PASS
- Evidence: best=K2_SOURCE_SPLIT_A2_PRIOR_V1; DeltaAIC_A2_minus_K1=-5.482602472699513; DeltaAIC_A2_minus_unit=-2.1042318916589418; A2 sign-match=1.0
- Interpretation: locked A2 is independently favored in this reconstruction-family subset

### RECON_SUBSET_ANTI_ALIGNED

- Status: PASS
- Evidence: best=K2_SOURCE_SPLIT_A2_PRIOR_V1; DeltaAIC_A2_minus_K1=-6.481636202408524; DeltaAIC_A2_minus_unit=-3.6021579443217924; A2 sign-match=1.0
- Interpretation: locked A2 is independently favored in this reconstruction-family subset

### RECON_SUBSET_ANTI_ALIGNED_MID_HIGH

- Status: PASS
- Evidence: best=K2_SOURCE_SPLIT_A2_PRIOR_V1; DeltaAIC_A2_minus_K1=-3.748286292999382; DeltaAIC_A2_minus_unit=-1.37203956389738; A2 sign-match=1.0
- Interpretation: locked A2 is independently favored in this reconstruction-family subset

### MEASUREMENT_VALIDATION_BOUNDARY

- Status: PASS
- Evidence: independent calibration is still preflight and covariance-limited
- Interpretation: does not authorize measurement-validation language
