# P-TauCov Coordinate/Source Basis Schema

Status: schema only / no concrete coordinate basis / no `Phi_0` / no reduced
domain / no linear packet / no metric evaluation / no scoring authorization.

The reference-domain selection rule requires a frozen coordinate/source basis.
This schema declares the fields that such a basis must contain before `Phi_0`,
`P_null`, `P_gauge`, `P_forbidden`, and `P_red` can be built.

## Required Basis Fields

| Field | Role | Forbidden source |
| --- | --- | --- |
| `coordinate_id` | Stable row identifier for a coordinate/source basis element. | score- or residual-derived identifier |
| `coordinate_family` | Predeclared family/group label for symmetry and blocked audits. | post-scoring family-gain cluster |
| `coordinate_kind` | Basis-kind tag such as parent, branch, morphology, clock, environment, or projection. | held-out residual pattern |
| `basis_axis` | Axis name used to build matrices and exclusion subspaces. | P5C v3 gain direction |
| `origin_value` | Target-blind reference value used for `Phi_0` origin or center selection. | OOS DeltaNLL optimized center |
| `scale_value` | Normalization scale for coordinate comparability. | target-residual normalization |
| `is_null_candidate` | Predeclared flag for possible exact zero-mode audit. | metric failure/success pattern |
| `is_gauge_candidate` | Predeclared flag for coordinate redundancy audit. | post-hoc covariance alignment |
| `is_forbidden_candidate` | Predeclared flag for outcome-derived or target-leaking field exclusion. | after-the-fact manual exclusion |
| `provenance` | Human-readable source and freeze note. | undocumented manual edit |

## Expected Packet Files

```text
data/p_taucov/linear/coordinate_basis.csv
evidence/p_taucov_coordinate_basis_manifest.yaml
evidence/p_taucov_coordinate_basis.sha256
evidence/p_taucov_coordinate_basis_leakage_audit.csv
```

## Minimum Freeze Conditions

The concrete coordinate-basis packet may be accepted only if:

```text
all required fields are present;
all coordinate_id values are unique;
origin_value and scale_value are finite;
scale_value is nonzero;
provenance is nonempty for every row;
no forbidden target, score, residual, or post-scoring source is used;
the leakage audit declares no outcome-derived basis columns;
the manifest and hash match the frozen packet.
```

## Claim Boundary

Allowed statement:

```text
The coordinate/source basis schema is declared.
```

Forbidden statement:

```text
A concrete P-TauCov coordinate basis or reference domain is frozen.
```
