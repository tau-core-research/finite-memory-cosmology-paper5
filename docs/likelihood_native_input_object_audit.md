# Likelihood-Native Input Object Audit

Status: public inputs are present; residual definitions are not measurement-frozen.

## Summary

- SN rows: 1701
- SN covariance dimension: 1701
- BAO rows: 13
- BAO covariance dimension: 13
- Preflight usable objects: 4/4
- Measurement usable objects: 0/4

## Objects

### SN_TABLE_PANTHEON_PLUS

- Class: sn_public_vector
- Artifact: `data/public_ingest/pantheon_plus/Pantheon_SH0ES.dat`
- Rows: 1701
- Shape/columns: 47 columns
- Preflight usable: True
- Measurement usable: False
- Blocking issue: SN residual definition requires frozen cosmology/nuisance centering and calibrator policy
- Next action: define r_SN and nuisance/marginalization policy before constructing L_SN

### SN_COVARIANCE_PANTHEON_PLUS

- Class: sn_public_covariance
- Artifact: `data/public_ingest/pantheon_plus/Pantheon_SH0ES_STAT_SYS.cov`
- Rows: 1701
- Shape/columns: 1701x1701
- Preflight usable: True
- Measurement usable: False
- Blocking issue: covariance is available but must be propagated through likelihood-native L_SN
- Next action: use only after SN residual transform is frozen

### BAO_VECTOR_DESI_DR2

- Class: bao_public_vector
- Artifact: `data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt`
- Rows: 13
- Shape/columns: z,value,quantity
- Preflight usable: True
- Measurement usable: False
- Blocking issue: BAO residual definition requires frozen prediction vector and no nearest-anchor transform
- Next action: define r_BAO for each observable type before constructing L_BAO

### BAO_COVARIANCE_DESI_DR2

- Class: bao_public_covariance
- Artifact: `data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt`
- Rows: 13
- Shape/columns: 13x13
- Preflight usable: True
- Measurement usable: False
- Blocking issue: covariance is available but must be propagated through likelihood-native L_BAO
- Next action: use only after BAO residual transform is frozen

## Claim Boundary

This audit only verifies local input availability and dimensional consistency. It does not construct a measurement-grade likelihood.
