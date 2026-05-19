# Backreaction Numeric Source Availability

Status: source route identified; numeric backreaction calibration remains blocked.

This audit checks the arXiv source packages for machine-readable numeric tables that could calibrate a BACKREACTION_ONLY physical null. It does not digitize figures and does not fit amplitudes to K2.

## Result

- Sources audited: 2
- Machine-readable numeric constraint sources: 0
- Formula/figure route sources: 2
- Upstream symbolic-regression route detected: True

## Interpretation

The Koksbang addendum exposes the backreaction formula and figure route. The upstream Koksbang-Heinesen reconstruction source package exposes the symbolic-regression method and figures, plus a cp3-bench reference, but no source-native numeric reconstruction table in the arXiv source package.

Therefore the backreaction null is not yet calibrated for the measurement gate. The next legitimate route is to obtain or reproduce the D_A, H_D and derivative reconstruction table with covariance, then map it into the locked A2/K2 preflight vector without changing the K2 kernel.

## Outputs

- Availability: `evidence/backreaction_numeric_source_availability.csv`
- Summary: `evidence/backreaction_numeric_source_availability_summary.csv`
