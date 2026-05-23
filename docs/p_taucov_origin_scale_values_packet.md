# P-TauCov Origin/Scale Values Packet

Status: minimal target-blind unit-convention values / no coordinate-basis packet
/ no reference-domain selection / no metric evaluation / no scoring
authorization.

This packet fills the origin/scale value-source gate with the minimal convention

```text
origin_value = 0
scale_value = 1
```

for every symbolic axis in the coordinate-basis skeleton. This is a coordinate
normalization convention, not an empirical fit and not a covariance result.

## Files

```text
data/p_taucov/linear/origin_scale_values.csv
evidence/p_taucov_origin_scale_values_manifest.yaml
evidence/p_taucov_origin_scale_values.sha256
evidence/p_taucov_origin_scale_values_leakage_audit.csv
```

## Claim Boundary

Allowed statement:

```text
Minimal target-blind origin/scale values are available for future coordinate-basis construction.
```

Forbidden statement:

```text
The coordinate basis, reference domain, matrices, or P-TauCov score are available.
```
