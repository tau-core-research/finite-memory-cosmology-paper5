# Source-Split Likelihood-Native Rho Requirement

Status: bounded-rho diagnosis complete; no rho rescue is allowed.

The amplitude-gap diagnosis is now followed by a bounded-rho audit:

```text
evidence/source_split_likelihood_native_rho_requirement_audit.csv
evidence/source_split_likelihood_native_bounded_rho_scan.csv
evidence/source_split_likelihood_native_rho_requirement_summary.csv
```

## Result

```text
Rows: 8
RowsExactMatchWithinRhoBound: 0
RowsRhoExceedsBound: 8
RowsRhoNegativeOrSignConflict: 0
BestBoundedRho: 4.0
BestBoundedRhoChi2: 136480.7438339473
K1NoMemoryChi2: 139789.55908762495
```

The bounded scan prefers the upper endpoint `rho=4`, and this improves over
K1/no-memory. However, every row would require `rho>4` to match the target
amplitude exactly.

Example required values:

```text
Grid 0: rho_required = 586.9819746167004
Grid 1: rho_required = 169.8132276263624
Grid 4: rho_required = 17.310763163574638
Grid 8: rho_required = 11.54368664332265
```

## Interpretation

This is not a reason to increase `rho`. The passive bound is part of the locked
operator discipline. The result says that the current likelihood-native
source-split target scale is much larger than the bounded finite-memory
multiplier can absorb.

The next work should examine:

- whether the source-split target scale is the right object for K2 scoring;
- whether the covariance proxy overweights low-depth amplitude residuals;
- whether an independently declared amplitude normalization is needed;
- whether the locked cubic operator is too weak for this branch.

No post-hoc K1 rescaling or `rho>4` rescue is authorized.

A follow-up scale/covariance sensitivity shows that K2's relative status depends
strongly on the error model. K2 improves over K1 in all tested cases, but beats
the best polynomial control only under a 25 percent target-fraction error floor.
That is a useful diagnostic, not a measurement claim.
