# PySR Criteria-Set-3 Structured Smoke

Status: STRICT_CRITERIA3_SELECTS_CONSTANT_NONCONSTANT_SHAPE_AVAILABLE.

This run keeps the strict criteria-set-3 rule intact while separately auditing nonconstant candidates. It is a shape-diagnosis smoke run, not measurement validation.

## Strict Selection

- Equation: `-0.23905218`
- Complexity: 1
- Loss: 0.7890149
- Original weighted MSE: 245.7639199705603

## Best Nonconstant Diagnostic Candidate

- Equation: `((x0 + 0.10858442) + (-0.058773473 / x0)) * log((x0 * 1.0989125) + -0.3808641)`
- Complexity: 14
- Loss: 0.0026790514
- Original weighted MSE: 0.7715048225994042

## Interpretation Boundary

The nonconstant candidate is diagnostic only. It is not a replacement for the strict criteria-set-3 selection and does not authorize measurement language.

## Next Action

Run bootstrap-scale criteria-set-3 or resolve whether the upstream penalty convention must be normalized before source-native scoring.
