# Backreaction-36 Covariance Treatment

Status: covariance policy frozen; scoring is not authorized by this artifact.

- Primary: `C0_PRIMARY` diagonal/equal-weight chi2.
- Robustness: `C1_ROBUSTNESS` family-block aggregate weighting.
- Robustness: `C2_ROBUSTNESS` shrinkage covariance if target-blind or training-fold-only.

Forbidden:

- full-target covariance fitted before scoring;
- covariance choice based on score.
