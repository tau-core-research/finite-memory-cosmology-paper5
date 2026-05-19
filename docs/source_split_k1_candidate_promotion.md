# Source-Split K1 Candidate Promotion Gate

Status: promotion gate completed; no candidate is promoted to primary K1.

## Run

```text
python3 scripts/check_source_split_k1_candidate_promotion.py
```

It writes:

```text
evidence/source_split_k1_candidate_promotion_readiness.csv
evidence/source_split_k1_candidate_promotion_summary.csv
```

## Purpose

The candidate sensitivity audit showed that mechanically nonzero K1 responses
exist. The promotion gate asks a stricter question: can any of those candidates
become the primary source-split K1/no-memory target for locked K2 scoring?

The answer is currently no.

## Result

Current summary:

```text
PromotedPrimaryK1Count: 0
BestAICModel: K1_SN_BRANCH_RESPONSE_AS_K1
BestAICCandidatePromotionAuthorized: False
Conclusion: no_primary_k1_promoted
```

The zero-contrast K1 remains a fair no-memory null, but it is degenerate for a
multiplicative K2 operator. The common-mode mean is nonzero, but it is derived
from the same exported family responses and still lacks predeclared external
provenance. The SN and BAO branch responses are diagnostic controls, not
primary source-split no-memory targets.

## Interpretation

This gate prevents a score-based K1 rescue. A candidate cannot become primary
K1 merely because it improves AIC on the current packet. It must be nonzero,
predeclared, externally interpretable, coordinate-native, and scored under the
same covariance policy as K2 and the null comparators.

The next benchmark therefore requires either an externally derived nonzero K1
response target or a likelihood-native K1 target. Until then, the source-split
K2 result remains a weakening preflight result rather than measurement
validation.
