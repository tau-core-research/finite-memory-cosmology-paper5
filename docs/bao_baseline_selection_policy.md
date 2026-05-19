# BAO Baseline Selection Policy

Status: active pre-K2 policy.

The BAO baseline scorecard now contains several baseline classes:

- audit flat-LCDM plumbing baseline;
- same-data `rd` offset sensitivity;
- same-data DESI BAO best-fit baseline;
- CMB-only public best-fit baseline.

These baselines answer different questions. The policy below prevents the
finite-memory measurement gate from selecting the most favorable baseline after
seeing the scores.

## Policy

Machine-readable policy:

```text
evidence/bao_baseline_selection_policy.csv
```

Core rules:

- same-data BAO best-fit baselines cannot be the primary K2 scoring baseline;
- same-data `rd` offset absorption is sensitivity-only;
- at least one external or independent baseline must be scored before K2
  interpretation;
- K2 and all null comparators must use the same residual vector and covariance;
- K2 remains locked to `p=3` and `rho<=4`;
- all baseline brackets must be reported side by side;
- the measurement gate remains closed until a K2/null protocol is registered.

## Outcome Language

Supportive:

- K2 remains competitive against fair nulls on an independent baseline;
- compatibility does not require `rho>4` or kernel changes;
- same-data baselines and independent baselines tell a consistent story.

Weakening:

- K2 looks viable only on same-data baselines;
- K2 is worse than no-memory or smooth nulls on CMB-only or other independent
  baselines;
- K2 requires bounded grid selection while fixed locked prediction is weak.

Invalid for measurement:

- K2 is evaluated on a same-data posterior maximum only;
- the covariance or residual target changes between K2 and nulls;
- compatibility requires changing the kernel or exceeding `rho<=4`;
- the baseline was selected after seeing K2 scores.

## Next Step

Create a K2 protocol registry for BAO residual scoring. The registry should
state which baseline brackets are used, which nulls are required, and what
counts as supportive, weakening, or strong negative before running any K2 score.

The BAO K1/no-memory response policy is tracked separately in:

```text
docs/bao_k1_response_policy.md
evidence/bao_k1_response_registry.csv
evidence/bao_k1_response_readiness.csv
```

The current readiness state has no K1 response allowed for K2 scoring. This is
the remaining blocker before even a diagnostic K2 score should be attempted.
