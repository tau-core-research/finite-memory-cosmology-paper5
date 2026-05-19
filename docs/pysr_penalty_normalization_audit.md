# PySR Penalty Normalization Audit

Status: PYSR_PENALTY_NORMALIZATION_REQUIRED_BEFORE_SOURCE_NATIVE_SCORING.

The structured smoke run shows that raw penalty-one criteria selects a constant on the current standardized loss scale, while much lower-loss nonconstant candidates are present.

## Key Numbers

- Strict penalty-one selects constant: True
- Best nonconstant equation: `((x0 + 0.10858442) + (-0.058773473 / x0)) * log((x0 * 1.0989125) + -0.3808641)`
- Constant loss: 0.7890149
- Best nonconstant loss: 0.0026790514
- Break-even penalty: 0.06048737296923076
- Strict original weighted MSE: 245.7639199705603
- Best nonconstant original weighted MSE: 0.7715048225994042

## Boundary

This does not select a replacement source-native null. It only records that the penalty convention must be governed before bootstrap-scale scoring.

## Next Action

Pre-register a source-native normalized criteria-set-3 selector or obtain the upstream authors' exact loss-scale convention.
