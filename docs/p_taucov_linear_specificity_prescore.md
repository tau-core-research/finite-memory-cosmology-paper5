# P-TauCov Linear Specificity Prescore

Status: blocked / no metric evaluation / no linear freeze / no scoring
authorization.

The prescore evaluator was invoked, but it did not evaluate the linear
specificity metrics.

## Block Reason

```text
missing_target_blind_linear_model_packet
```

## Required Missing Artifact

```text
evidence/p_taucov_linear_model_packet.yaml
```

That packet must contain concrete target-blind matrices/operators for the
strictly linear candidate:

```text
L0_B
R_B
P_red
A_Phi
A_B
P0
observable coordinate basis
input provenance hashes
```

## Current Boundary

```text
LinearCandidateFrozen: false
DeltaCTauGenerated: false
PTauCovScoringAuthorized: false
```

Allowed statement:

```text
The prescore evaluator exists and correctly blocks without a target-blind linear
model packet.
```

Forbidden statement:

```text
The strictly linear candidate passed the specificity audit.
```
