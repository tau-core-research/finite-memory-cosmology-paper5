# Source-Split Likelihood-Native Cross-Covariance Sensitivity

Status: cross-covariance sensitivity complete.

This audit tests the weakest assumption in the first public covariance proxy:
the zero SN-BAO cross-covariance assumption. It introduces a row-aligned
cross-covariance proxy controlled by `rho_cross`.

```text
script: scripts/run_likelihood_native_cross_covariance_sensitivity.py
detail: evidence/source_split_likelihood_native_cross_covariance_sensitivity.csv
summary: evidence/source_split_likelihood_native_cross_covariance_summary.csv
```

## Result

Across the positive-definite tested range, K2 continues to improve over
K1/no-memory, but it does not beat the best polynomial control.

```text
K2 improves over K1/no-memory: true across valid rho_cross values
K2 beats best polynomial control: false across valid rho_cross values
```

The row-aligned cross-covariance proxy therefore does not move the public
covariance proxy into the stronger branch-scatter result.

## Interpretation

This is a useful weakening/diagnostic result:

- The K2 direction remains nontrivial because it improves over K1/no-memory.
- The public covariance proxy remains less supportive than the branch-scatter
  benchmark.
- The next improvement must come from a better covariance transform or a
  declared reconstruction-family/systematic scatter model, not from changing the
  K2 operator.

This audit remains preflight-only and does not constitute measurement
validation.
