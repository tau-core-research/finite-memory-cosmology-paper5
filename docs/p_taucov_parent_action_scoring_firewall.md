# P-TauCov Parent-Action Scoring Firewall

Status: `P_TAUCOV_PARENT_ACTION_SCORING_BLOCKED_FREEZE_REQUIRED`.

The parent-action packet now passes its no-scoring embedding gates,
but that does not authorize empirical scoring. This firewall records
what must be frozen before any parent-action P-TauCov scorecard can
be run.

## Current State

- parent-action packet pass: `True`
- satisfied firewall items: `2/8`
- scoring authorized: `False`
- missing items: `PRIMARY_SCORECARD_SCRIPT_FROZEN;FOLD_POLICY_FROZEN;NULL_COMPARATOR_POLICY_FROZEN;SURVIVAL_AND_KILL_GATES_FROZEN;DF_AND_COVARIANCE_POLICY_FROZEN;HASH_MANIFEST_READY`

## Required Before Scoring

- primary scorecard script hash
- fold policy
- null comparator policy
- survival and kill gates
- degrees-of-freedom and covariance policy
- final SHA256 manifest

## Claim Boundary

Allowed: the parent-action side is ready for a future freeze packet.

Forbidden: no empirical scoring, no survival claim, and no measurement
validation are authorized by this packet.
