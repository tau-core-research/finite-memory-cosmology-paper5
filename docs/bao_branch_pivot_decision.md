# BAO Branch Pivot Decision

Status: preflight branch documented; BAO K2 scoring remains closed.

This note records the current BAO branch decision for the measurement-gate
program. It does not weaken the value of the BAO work: the branch successfully
solved public-data access, covariance plumbing, baseline export, and residual
transform preflight. It does mean that the BAO path is not yet the right place
to claim a locked finite-memory response.

## What Survives

- DESI DR2 and DESI DR1 BAO mean/covariance products are locally available.
- Pantheon+SH0ES products are locally available for later source-split work.
- The raw public-observable preflight and input inventory run reproducibly.
- The BAO log-residual transform runs with propagated covariance.
- DESI same-data and CMB-only public best-fit baseline exports are parsed and
  scored.
- The K2 protocol gate correctly prevents premature scoring.

## What Weakens The BAO Route

The BAO residual layer is currently dominated by baseline choice. Under the
audit flat-LCDM residual transform, a constant-offset control is preferred. The
offset diagnosis maps this to an approximately 1.5 percent BAO scale shift,
which is a baseline-calibration warning rather than evidence for the
finite-memory projection hypothesis.

The same-data DESI best-fit baseline is useful for validating the evaluator,
but it cannot be the primary K2 baseline because it is optimized on the same
BAO vector. The CMB-only baseline is more independent, but it is less
BAO-compatible.

The CMB-only unit-covariance-norm K1 response candidate is normalizable, but it
does not beat the zero-response null under the current scorecard. Therefore it
is not selected as a locked BAO K1 response target.

## Decision

BAO measurement-gate scoring remains closed.

The BAO branch should be frozen as a documented preflight and control branch
until one of the following exists:

- a likelihood-native or coordinate-native BAO diagnostic transform;
- an independent locked K1 response target that is competitive with fair nulls;
- a public covariance-aware benchmark where K2 and null comparators share the
  same residual vector and covariance.

## Recommended Pivot

The next primary empirical branch should move to SN+BAO/source-split response
structure or another coordinate-native diagnostic where a locked K1/no-memory
target can be defined without using the tested BAO vector to set the response
amplitude.

BAO should remain in the paper as:

- a public-data ingestion success;
- a baseline-sensitivity warning;
- a preflight control branch;
- an example of the measurement gate refusing to overclaim.

It should not be presented as measurement validation.

