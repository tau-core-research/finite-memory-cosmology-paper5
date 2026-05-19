# Source-Split Future Rerun Protocol

Status: protocol added; no current rerun is authorized.

This protocol defines how the source-split K2 comparison may be rerun in the
future without turning the K1 baseline into a post-hoc rescue.

## Run

```text
python3 scripts/build_source_split_future_rerun_protocol.py
```

It writes:

```text
evidence/source_split_future_rerun_protocol.csv
evidence/source_split_future_rerun_protocol_summary.csv
```

## Current Decision

```text
AllowedCurrentRerunCount: 0
PreferredProtocol: SSRERUN_LIKELIHOOD_NATIVE_K1_V1
SecondaryProtocol: SSRERUN_FAMILY_MEAN_EQUAL_WEIGHT_V1
ForbiddenProtocol: SSRERUN_FORBIDDEN_CURRENT_SCORECARD_RESCUE
```

## Allowed Future Routes

The preferred route is a likelihood-native joint SN+BAO K1/no-memory baseline
with frozen parameters and covariance.

The secondary preflight route is an equal-weight signed reconstruction-family
mean, but only if the policy is frozen before rerunning the scorecard. It
cannot be used retroactively for the current result.

## Forbidden Route

The forbidden route is any K1 generated from the current K2 residuals or tuned
to improve the present scorecard. Such a path invalidates the measurement-gate
interpretation.

## Locked Rules

- K2 kernel stays `W(x)=1+rho*x^3`.
- `rho > 4` is not allowed.
- The K1 export must exist before the rerun.
- Null comparators must be reported under the same covariance.
- Sign-stability warning rows must remain visible.

## Interpretation

The current branch remains in preflight status. The protocol is valuable
because it defines the next valid comparison before the next comparison is
run.
