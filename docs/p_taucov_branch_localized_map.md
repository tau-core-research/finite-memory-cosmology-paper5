# P-TauCov Branch-Localized Map

Status: `P_TAUCOV_BRANCH_LOCALIZED_MAP_FROZEN_SIGNED_NO_SCORING`.

The localized map applies the frozen support mask to the parent-action
covariance map, symmetrizes the retained support, and Frobenius
normalizes the result. It does not inspect target residuals or score
outcomes.

- map dimension: `2`
- minimum eigenvalue: `-0.05564175590369821`
- maximum eigenvalue: `0.9984507974857616`
- Frobenius norm: `1.0`

If the localized map is not PSD, it must use a signed-response
protocol rather than a covariance-deformation survival claim.
