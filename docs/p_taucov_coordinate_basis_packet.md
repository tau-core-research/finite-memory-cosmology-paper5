# P-TauCov Coordinate-Basis Packet

Status: concrete target-blind coordinate basis / no matrices / no linear packet
/ no metric evaluation / no scoring authorization.

This packet combines the non-authorizing coordinate-basis skeleton with the
validated minimal origin/scale values packet. It supplies the first concrete
`coordinate_basis.csv` required for reference-domain selection.

## Files

```text
data/p_taucov/linear/coordinate_basis.csv
evidence/p_taucov_coordinate_basis_manifest.yaml
evidence/p_taucov_coordinate_basis.sha256
evidence/p_taucov_coordinate_basis_leakage_audit.csv
```

## Claim Boundary

Allowed statement:

```text
A target-blind coordinate basis is frozen for reference-domain construction.
```

Forbidden statement:

```text
P_red, linear matrices, covariance response, metric evaluation, or P-TauCov
scoring are available.
```
