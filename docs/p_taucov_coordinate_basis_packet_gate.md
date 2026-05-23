# P-TauCov Coordinate-Basis Packet Gate

Status: packet gate / no concrete coordinate basis / no reference-domain
selection / no linear packet / no metric evaluation / no scoring authorization.

This artifact defines the acceptance gate for the concrete coordinate/source
basis packet required by the P-TauCov reference-domain selection rule.

## Required Files

| File | Purpose |
| --- | --- |
| `data/p_taucov/linear/coordinate_basis.csv` | Concrete coordinate/source basis rows. |
| `evidence/p_taucov_coordinate_basis_manifest.yaml` | Provenance, source policy, freeze timestamp, and no-outcome declaration. |
| `evidence/p_taucov_coordinate_basis.sha256` | SHA256 digest of `coordinate_basis.csv`. |
| `evidence/p_taucov_coordinate_basis_leakage_audit.csv` | Leakage audit proving no target/residual/score-derived basis fields. |

## Packet Acceptance Checks

The packet validator must reject the packet unless:

```text
all required files exist;
all schema fields are present in coordinate_basis.csv;
coordinate_id values are unique;
origin_value values are finite;
scale_value values are finite and nonzero;
provenance is nonempty for every row;
manifest declares OutcomeInformationUsed=false;
manifest declares ResidualInformationUsed=false;
manifest declares ScoreInformationUsed=false;
manifest declares PostScoringLocalizationUsed=false;
sha256 file matches coordinate_basis.csv;
leakage audit contains no failing required checks.
```

## Claim Boundary

Allowed statement:

```text
The coordinate-basis packet acceptance gate is declared.
```

Forbidden statement:

```text
The concrete coordinate-basis packet has been accepted or frozen.
```
