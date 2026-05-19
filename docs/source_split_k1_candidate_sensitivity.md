# Source-Split K1 Candidate Sensitivity

Status: sensitivity audit completed; no nonzero candidate is promoted to
primary K1.

## Run

```text
python3 scripts/build_source_split_k1_response_candidate_audit.py
python3 scripts/run_source_split_k1_candidate_sensitivity.py
```

It writes:

```text
evidence/source_split_k1_response_candidate_audit.csv
evidence/source_split_k1_response_candidate_summary.csv
evidence/source_split_k1_candidate_sensitivity.csv
evidence/source_split_k1_candidate_sensitivity_summary.csv
```

## Candidates

The audit checks:

- `K1_ZERO_CONTRAST_CURRENT`: fair no-memory null, but degenerate for
  multiplicative K2.
- `K1_FAMILY_COMMON_MODE_MEAN`: nonzero family mean sensitivity candidate.
- `K1_SN_BRANCH_RESPONSE`: single-branch diagnostic control.
- `K1_BAO_BRANCH_RESPONSE`: single-branch diagnostic control.

Only the zero-contrast candidate is currently allowed as a primary K1. The
nonzero candidates are sensitivity controls until their provenance is
predeclared.

## Result

Current sensitivity summary:

```text
BestAICModel: K1_SN_BRANCH_RESPONSE_AS_K1
BestAICCandidateAllowedAsPrimaryK1: False
NonzeroCandidateCount: 3
```

The family common-mode candidate is nonzero on all eight usable rows, but its
locked K2 rho=4 response is worse than its own K1 response under the current
preflight scorecard. The best AIC model is the SN branch used directly as K1,
but that is a single-branch diagnostic control and is not a valid primary
source-split no-memory target.

## Interpretation

The sensitivity audit does not rescue K2. It shows that source-split K2 needs a
nonzero K1 response with an external, predeclared interpretation. A nonzero
array alone is not enough.
