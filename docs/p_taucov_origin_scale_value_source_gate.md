# P-TauCov Origin/Scale Value-Source Gate

Status: value-source gate / no concrete origin values / no concrete scale
values / no coordinate-basis packet / no metric evaluation / no scoring
authorization.

The origin/scale rule freeze states how values may be selected. This artifact
defines the packet required before those placeholders can be filled in the
coordinate-basis skeleton.

## Required Files

| File | Purpose |
| --- | --- |
| `data/p_taucov/linear/origin_scale_values.csv` | Target-blind concrete `origin_value` and `scale_value` rows keyed by `basis_axis`. |
| `evidence/p_taucov_origin_scale_values_manifest.yaml` | Provenance, rule conformance, and no-outcome declaration. |
| `evidence/p_taucov_origin_scale_values.sha256` | SHA256 digest of `origin_scale_values.csv`. |
| `evidence/p_taucov_origin_scale_values_leakage_audit.csv` | Leakage audit proving no residual, score, or post-scoring source was used. |

## Expected CSV Columns

```text
basis_axis
origin_value
scale_value
origin_rule
scale_rule
value_source
provenance
```

## Hard Acceptance Conditions

The value-source packet may be accepted only if:

```text
all required files exist;
all expected columns are present;
all basis_axis values are unique;
origin_value and scale_value are finite;
scale_value is nonzero;
origin_rule and scale_rule match the frozen axis-kind rules;
manifest declares OutcomeInformationUsed=false;
manifest declares ResidualInformationUsed=false;
manifest declares ScoreInformationUsed=false;
manifest declares PostScoringLocalizationUsed=false;
sha256 file matches origin_scale_values.csv;
leakage audit contains no failing required checks.
```

## Claim Boundary

Allowed statement:

```text
The origin/scale value-source acceptance gate is declared.
```

Forbidden statement:

```text
Concrete origin/scale values or a coordinate-basis packet are available.
```
