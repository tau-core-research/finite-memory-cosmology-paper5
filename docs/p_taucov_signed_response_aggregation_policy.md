# P-TauCov Signed-Response Aggregation Policy

Status: `P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FROZEN_NO_SCORING`.

A future signed-response score must pass both family and clock
blocked aggregation. It must rank above required signed nulls, must
not be dominated by one family, and family/clock signs must agree.

The dominance cap is frozen at `0.5` for the largest positive family
contribution share.

Diagnostic family-by-clock and diagonal controls are report-only and
cannot rescue a failed primary signed result.
