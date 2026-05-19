# K2_SOURCE_SPLIT_A2_PRIOR_V1 Locked Prediction Status

Status: locked prediction candidate / no measurement-validation claim

## Locked prediction

```text
PredictionID = K2_SOURCE_SPLIT_A2_PRIOR_V1
K2_A2(x)    = 2 * K1(x) * (1 + 4*x^3)
```

This is not a new kernel.

```text
p   = 3
rho = 4
A_tau = 2
```

The factor `A_tau=2` is interpreted as a source-split projection prior from an
anti-aligned two-channel geometry:

```text
R_split = R_SN - R_BAO
g_SN ~= +1
g_BAO ~= -1
A_tau = g_SN - g_BAO ~= 2
```

Forbidden changes:

```text
rho > 4
p change
K1 refit
pointwise A_tau
fitted A_tau replacing the locked prior
measurement-validation claim from current packet
```

## What survived

The locked A2 prediction survived the current preflight battery:

```text
prediction lock readiness: PASS, 11/11
pointwise benchmark: A2 best in all tracked subsets
leave-one-out: A2 wins 8/8
mid-depth leave-one-out drops: A2 wins 3/3
depth transition: low < mid < high amplitude recovery
anti-alignment conditioned: stronger in anti-aligned mid/high rows
reconstruction-family branch benchmark: A2 best in all tracked subsets
rebinning stress: A2 best in all tested rebin schemes
```

## Most important numbers

Depth transition:

```text
low-depth  A2 amplitude ratio ~= 0.120
mid-depth  A2 amplitude ratio ~= 0.556
high-depth A2 amplitude ratio ~= 0.951
```

High-depth:

```text
K2 unit amplitude ratio ~= 0.476
A2 amplitude ratio      ~= 0.951
cosine                  ~= 0.990
```

Mid+high:

```text
A2 amplitude ratio ~= 0.869
```

Rebinning stress, A2 chi2 improvement over unit K2:

```text
DEPTH_THREE_BIN        ~= -4.22
PAIRWISE_ADJACENT      ~= -4.41
MEMORY_ACTIVE_VS_LOW   ~= -4.17
ANTI_ALIGNED_VS_OTHER  ~= -6.50
```

## Scientific reading

The current result supports a narrow claim:

```text
In the memory-active mid/high source-split regime, the locked cubic finite-memory
backbone combined with the predeclared A_tau=2 projection prior is compatible
with the observed residual direction and recovers much of the amplitude.
```

The claim does not say:

```text
discovery
proof
full cosmological model
measurement validation
```

## Current weakness

The current benchmark is still preflight-level:

```text
not full public covariance-aware likelihood
not independent reconstruction-family validation
not likelihood-native end-to-end source-split export
```

The A2 result is strong enough to freeze, not strong enough to declare measured.

## Next required gate

The next valid step is externalization:

```text
1. new reconstruction family,
2. new binning from public products,
3. covariance-native source-split likelihood,
4. or independent public SN+BAO diagnostic packet.
```

The locked prediction must be evaluated without:

```text
changing the kernel,
changing A_tau,
refitting K1,
or adding pointwise gains.
```

