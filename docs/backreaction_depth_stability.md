# Backreaction Depth Stability

Status: leave-one-depth preflight sensitivity audit; no measurement validation.

This audit recomputes the K2/backreaction projection after removing one depth row from the mid/high and high-depth subsets. It tests whether the component split is dominated by a single row. It does not change locked K2 and does not fit a new K1.

## Outputs

- Row audit: `evidence/backreaction_depth_stability_row.csv`
- Summary: `evidence/backreaction_depth_stability_summary.csv`
