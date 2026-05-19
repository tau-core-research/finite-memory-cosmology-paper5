# Source-Split Likelihood-Native Parameter Source

Status: frozen parameter source available; likelihood-native K1 export is still not ready.

The source-split route now has a predeclared no-memory parameter source:

```text
data/k1/source_split_likelihood_native_parameters.yaml
```

The source is the public CMB-only best-fit preflight file:

```text
data/public_ingest/desi_dr2_bestfit/base_cmb_only/bestfit.minimum.txt
```

This is intentionally not the same-data DESI BAO best fit. The same-data DESI
file remains only a diagnostic control, because using it as the primary K1
baseline would risk tuning the no-memory side to the comparison target.

## Frozen Values

```text
H0: 67.060759
OmegaM: 0.31779326
rd_mpc: 147.30766
omega_m_h2: 0.14291625
OmegaLambda: 0.68212641
sigma8: 0.8095391
```

## Current Boundary

This artifact is a parameter source only. The baseline prediction vector and a
coordinate preflight map now exist, but they have not been promoted to
likelihood-native K1 export quality and do not authorize a new K2/null
scorecard.

The next required promotion targets are:

- `data/k1/source_split_likelihood_native_baseline_prediction.csv`
- `data/k1/source_split_likelihood_native_coordinate_map.csv`
- promoted joint covariance / nuisance policy
- likelihood-native K1 export and null scorecard

Only after those are promoted together can the likelihood-native K1 export be
validated against the locked finite-memory prediction and registered null
comparators.
