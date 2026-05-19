# Source-Split Diagnostic Transform Contract

Status: contract layer added; no K2 scoring authorized.

This contract separates the current distilled SN+BAO diagnostic packet from a
future public source-split measurement gate. The current packet is useful as a
template because it already contains sign-family information. It is not enough
for measurement scoring because it is not a direct public likelihood-native or
coordinate-native target.

## Required Transform

The target transform must produce a shared diagnostic vector from public SN and
BAO products:

```text
Pantheon+SH0ES SN product
DESI DR2 BAO product
        -> source-split diagnostic vector
        -> coordinate-native x grid
        -> shared covariance or declared shrinkage covariance
        -> frozen K1/no-memory target
        -> locked K2 comparison
```

The transform must define:

- the SN residual or distance-modulus treatment;
- the BAO anchor/control role;
- the coordinate mapping used for `x`;
- the covariance propagation or shrinkage rule;
- the sign-family export policy;
- the K1/no-memory target before K2 is evaluated.

## Registered Stages

The machine-readable registry is:

```text
evidence/source_split_transform_registry.csv
```

The readiness output is:

```text
evidence/source_split_transform_readiness.csv
```

Run:

```text
python3 scripts/check_source_split_transform_contract.py
```

## Current Decision

The current source-split branch is promising because public SN and BAO inputs
are available and the distilled packet already shows where sign-stable and
sign-unstable rows separate. The scoring gate remains closed because the
coordinate-native K1/no-memory target is missing.

This is not a negative result for the finite-memory projection hypothesis. It
is a boundary condition on the next empirical test: K2 should not be scored
until the no-memory target and covariance are defined in the same public
diagnostic space.

