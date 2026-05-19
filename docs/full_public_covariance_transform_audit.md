# Full Public Covariance Transform Audit

Status: public covariance inputs are available, but measurement validation remains blocked.

## Summary

- Passed checks: 5/8
- Warnings: 2
- Blocked: 1
- Measurement blockers: 3
- Zero-cross preflight covariance usable: True
- Full public covariance transform ready: False

## Findings

### FPCOV_1_PUBLIC_SN_VECTOR_AND_COVARIANCE

- Status: PASS
- Evidence: Pantheon rows=1701; covariance shape=(1701, 1701)
- Interpretation: public SN covariance input is locally available

### FPCOV_2_PUBLIC_BAO_VECTOR_AND_COVARIANCE

- Status: PASS
- Evidence: DESI mean rows=13; covariance shape=(13, 13)
- Interpretation: public BAO covariance input is locally available

### FPCOV_3_TRANSFORM_MATRICES_AVAILABLE

- Status: PASS
- Evidence: L_SN shape=(8, 1701); L_BAO shape=(8, 13); aligned_grid=True
- Interpretation: SN and BAO transform matrices are exported and row-aligned

### FPCOV_4_ZERO_CROSS_COVARIANCE_POSITIVE_DEFINITE

- Status: PASS
- Evidence: zero-cross propagated covariance eig_min=0.9081925216647435; eig_max=2934.683845944501
- Interpretation: the propagated zero-cross covariance is numerically usable as preflight covariance

### FPCOV_5_PUBLIC_PROXY_SCORECARD_STATUS

- Status: WARNING
- Evidence: K2 improves over K1=True; K2 beats best polynomial=False; best model=POLY_DEG2
- Interpretation: public covariance route remains mixed because polynomial controls dominate in proxy scorecard

### FPCOV_6_CROSS_COVARIANCE_ROUTE

- Status: WARNING
- Evidence: cross-cov sensitivity K2 improves over K1=27/27; K2 beats polynomial=0/27
- Interpretation: SN-BAO cross-covariance is not likelihood-native and cannot be tuned into a validation route

### FPCOV_7_FULL_LIKELIHOOD_NATIVE_TRANSFORM

- Status: BLOCKED
- Evidence: current transform is binned/anchored diagnostic transform, not full SN+BAO likelihood-native joint transform
- Interpretation: full measurement route is still missing

### FPCOV_8_CLAIM_BOUNDARY

- Status: PASS
- Evidence: support ladder measurement status=BLOCKED
- Interpretation: claim remains bounded to preflight support
