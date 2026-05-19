# Source-Native Surrogate Bridge Shape Diagnosis

Status: surrogate mismatch diagnosed; source-native bridge still missing.

This diagnostic separates amplitude, sign, and shape mismatch modes. Best-scale values are explicitly forbidden for claims and are used only to understand the failure mode.

## Result

- Cases: 10
- K2-like shape cases: 1
- Amplitude-dominated target mismatch cases: 1
- Sign/shape mismatch cases: 4
- Median corr(surrogate,K2): 0.504
- Median corr(surrogate,target): 0.087

## Outputs

- Diagnosis: `evidence/source_native_surrogate_bridge_shape_diagnosis.csv`
- Summary: `evidence/source_native_surrogate_bridge_shape_summary.csv`
