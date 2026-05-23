# P-TauCov TCCS Operator Assembly Preflight

Freeze ID: `P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_v1`

Status:

`P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_BLOCKED_BY_OPERATOR_CONVENTION_AND_PI_PERP`

## Purpose

This preflight asks whether the ingredients for

```text
T_tau = Normalize(Pi_bal Pi_perp Orient_+([L_B_red, P_morph]; J_tau) Pi_perp Pi_bal)
```

can be assembled without score access.

## Result

The source pieces now exist for object-construction preflight.

The orientation anchor and parent-to-score embedding are no longer the main blockers. A target-blind `J_tau`
candidate and a target-blind parent-to-score embedding are now frozen.

```text
J_tau: frozen parent-coordinate skew orientation
embedding: frozen 8-coordinate to 36-row bridge
```

The remaining step is not scoring. It is an object-construction preflight that
checks whether the assembled commutator is nonzero and whether it survives the
pre-score TCCS gates.

## Blocking Items

| Item | Status |
|---|---|
| `P_morph` | frozen |
| `Pi_perp` | frozen |
| parent-to-score embedding | frozen |

## Next Gate

```text
run TCCS object-construction preflight without scoring
```

This must remain pre-score. It may use coordinate definitions, declared null
policies, and source geometry. It may not use target residuals, score outcomes,
dominant-family identity, or previous gain signs.

## Claim Boundary

Allowed statement:

> The TCCS operator assembly is blocked by a concrete parent-to-score embedding and orthogonalization gate.

Forbidden statement:

> A TCCS object has been constructed, score-authorized, or shown to carry a Tau signal.
