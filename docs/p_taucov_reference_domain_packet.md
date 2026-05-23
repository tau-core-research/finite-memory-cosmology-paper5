# P-TauCov Reference-Domain Packet

Status: concrete reference state and reduced-domain projector / no linear
matrices / no covariance response / no metric evaluation / no scoring
authorization.

This packet applies the target-blind reference-domain selection rule to the
frozen coordinate basis. `Phi_0` is the frozen coordinate-basis origin vector.
`P_null`, `P_gauge`, and `P_forbidden` are diagonal exclusion projectors built
from predeclared basis flags. `P_red` retains only the non-excluded coordinates.

## Files

```text
data/p_taucov/linear/phi_0.csv
data/p_taucov/linear/p_null.csv
data/p_taucov/linear/p_gauge.csv
data/p_taucov/linear/p_forbidden.csv
data/p_taucov/linear/p_red.csv
evidence/p_taucov_reference_domain_manifest.yaml
evidence/p_taucov_reference_domain.sha256
```

## Claim Boundary

Allowed statement:

```text
The P-TauCov reference state and reduced domain are frozen.
```

Forbidden statement:

```text
The Tau-side linear matrices, covariance response, specificity metrics, or
P-TauCov score are available.
```
