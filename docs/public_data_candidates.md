# Public Data Candidates

Status: candidate files downloaded for preflight. No public likelihood ingestion
or finite-memory diagnostic transform has been performed.

## DESI BAO

Primary candidate:

- `DESI_DR2_BAO_ALL_GAUSSIAN`
- mean vector: `https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt`
- covariance: `https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt`
- source documentation: `https://cobaya.readthedocs.io/en/devel/likelihood_bao.html`

Fallback candidate:

- `DESI_DR1_BAO_ALL_GAUSSIAN`
- mean vector: `https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_2024_gaussian_bao_ALL_GCcomb_mean.txt`
- covariance: `https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_2024_gaussian_bao_ALL_GCcomb_cov.txt`
- source documentation: `https://data.desi.lbl.gov/doc/releases/dr1/vac/bao-cosmo-params/`

The DESI products are suitable as BAO-only covariance-aware candidates, but the
finite-memory diagnostic transform and coordinate-native mapping still need to
be defined.

Local preflight files:

- `data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt`
- `data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt`
- `data/public_ingest/desi_dr1/desi_2024_gaussian_bao_ALL_GCcomb_mean.txt`
- `data/public_ingest/desi_dr1/desi_2024_gaussian_bao_ALL_GCcomb_cov.txt`

## Pantheon+

Candidate:

- `PANTHEON_PLUS_SH0ES_SN`
- data vector: `https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat`
- covariance: `https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov`
- source repository: `https://github.com/PantheonPlusSH0ES/DataRelease`

This is a SN likelihood input candidate. It does not by itself define the
finite-memory diagnostic vector. A SN+BAO transform must be specified before it
can be used in the measurement gate.

Local preflight files:

- `data/public_ingest/pantheon_plus/Pantheon_SH0ES.dat`
- `data/public_ingest/pantheon_plus/Pantheon_SH0ES_STAT_SYS.cov`
