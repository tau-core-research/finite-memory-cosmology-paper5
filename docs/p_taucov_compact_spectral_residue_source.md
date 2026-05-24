# P-TauCov Compact Spectral Residue Source

Status: `P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_PREFLIGHT_PASS_NO_SCORING`

This is a no-score preflight artifact for the primary microscopic
residue-source route. The source is selected from the compact clock
Laplacian restricted to the frozen `Q_range` clean subspace. No target
residuals, OOS scores, alpha behavior, or winning nulls are used.

## Key Metrics

- active eigenmodes: `31`
- selected eigenmodes: `7`
- source norm before normalization: `8.809327791696738`
- smooth PSD projection overlap: `0.04103067597687979`
- projection-null abs correlation: `0.1481514322243125`
- Q-range membership error: `1.3827537115440763e-15`
- spectral residue rank fraction: `0.6733316932044486`
- max family share: `0.25621203258596065`
- max clock share: `0.16404853850994844`
- max context share: `0.34130133805909635`
- gates passed: `7/7`

## Claim Boundary

Allowed: this source passes or fails a no-score structural preflight
for compact spectral residue admissibility.

Forbidden: this source is a Tau Core signal, a scored covariance
survivor, or measurement validation.
