# Source-Split Likelihood-Native Coordinate Map

Status: coordinate preflight map available; not primary likelihood-native map.

The coordinate map has been exported to:

```text
data/k1/source_split_likelihood_native_coordinate_map.csv
evidence/source_split_likelihood_native_coordinate_map_summary.csv
```

It uses a flat-LCDM comoving-distance-normalized coordinate with the frozen
CMB-only `OmegaM` value:

```text
CoordinateMapID: SOURCE_SPLIT_CMB_CHI_COORDINATE_PREFLIGHT_V1
OmegaM: 0.31779326
Rows: 7
XMin: 0.38793451852076766
XMax: 1.0
FrozenBeforeK2Scoring: True
LikelihoodNative: False
AllowedForK1Export: False
```

This freezes the depth ordering needed by the locked finite-memory operator,
but it is still a preflight coordinate because the joint vector and covariance
policy have not been promoted together.

The next step is to define the nuisance/covariance promotion rule before any
likelihood-native K1 export is used for locked K2/null scoring.
