# Physical Null Alpha Scoring Authorization

Status: alpha physical-null scorecard remains closed.

This guard consolidates the non-scoring alpha transform, sign-convention, and
covariance-preview artifacts. It answers one question: may alpha-derived optical
controls enter a physical-null scorecard?

Current answer: no.

Outputs:

- `evidence/physical_null_alpha_scoring_authorization.csv`;
- `evidence/physical_null_alpha_scoring_authorization_summary.csv`.

## Required Before Scoring

The current branch still requires:

- an externally frozen optical sign convention;
- source-native covariance or a registered covariance propagation route;
- explicit authorization that the alpha-derived optical branch is a fair
  physical null for the source-split benchmark rather than a sensitivity
  preview.

## Boundary

This guard does not score K2, does not compare models, does not choose a sign by
performance, and does not create measurement-validation language.
