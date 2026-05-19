# Likelihood-Native Residual Definition Contract

Status: residual definitions are explicit for preflight, but not measurement-frozen.

## Summary

- Residual contracts: 6
- Measurement-ready residual contracts: 0/6
- Resolved for locked rerun candidate: 6/6
- Measurement validation allowed: False

## Contracts

### RDEF_SN_1_OBSERVABLE

- Source: Pantheon+SH0ES
- Object: `r_SN`
- Current definition: MU_SH0ES - mu_flat_LCDM_audit
- Measurement requirement: choose public-likelihood distance-modulus residual definition and redshift column
- Blocking issue: distance modulus baseline and nuisance/marginalization policy are not frozen
- Next action: freeze SN residual as either raw public mu residual or nuisance-marginalized residual before L_SN

### RDEF_SN_2_OFFSET_POLICY

- Source: Pantheon+SH0ES
- Object: `SN_offset`
- Current definition: inverse-variance same-sample offset subtraction
- Measurement requirement: declare whether absolute magnitude/nuisance offset is externally fixed, marginalized, or projected out
- Blocking issue: same-sample offset subtraction would leak target information into the residual
- Next action: replace same-sample centering with predeclared nuisance treatment

### RDEF_SN_3_GRID_TRANSFORM

- Source: Pantheon+SH0ES
- Object: `L_SN`
- Current definition: diagonal-weighted binning to current 8-point grid
- Measurement requirement: construct L_SN from the likelihood-native SN residual vector with full covariance propagation
- Blocking issue: current grid transform is binned/diagonal proxy
- Next action: build likelihood-native L_SN after RDEF_SN_1 and RDEF_SN_2 are frozen

### RDEF_BAO_1_OBSERVABLE

- Source: DESI DR2 BAO
- Object: `r_BAO`
- Current definition: log(observed / audit_flat_LCDM_prediction) for DH/DM/DV over rs
- Measurement requirement: freeze BAO prediction vector and residual convention for each observable type
- Blocking issue: audit fiducial baseline is not the final likelihood-native baseline
- Next action: define BAO residual against the frozen external baseline before L_BAO

### RDEF_BAO_2_RS_POLICY

- Source: DESI DR2 BAO
- Object: `r_d / rs policy`
- Current definition: audit baseline rd=147.0
- Measurement requirement: predeclare whether r_d is CMB-fixed, BAO-likelihood fitted, or externally marginalized
- Blocking issue: sound-horizon/baseline policy affects BAO residual amplitude
- Next action: lock r_d/baseline policy before rerunning K1 and A2

### RDEF_BAO_3_GRID_TRANSFORM

- Source: DESI DR2 BAO
- Object: `L_BAO`
- Current definition: nearest/anchor mapping into source-split grid
- Measurement requirement: construct L_BAO from observable-level BAO residuals without post-hoc nearest-anchor choices
- Blocking issue: current BAO transform is not a final likelihood-native source-split transform
- Next action: build likelihood-native L_BAO after RDEF_BAO_1 and RDEF_BAO_2 are frozen

## Claim Boundary

This contract defines what must be frozen before measurement scoring. It does not alter A2 and does not score a new result.
