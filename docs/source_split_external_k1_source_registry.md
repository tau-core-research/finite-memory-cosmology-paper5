# Source-Split External K1 Source Registry

Status: source registry added; no external K1 source is currently authorized.

The source-split branch needs an externally derived, nonzero K1/no-memory
response before locked K2 can be tested as a distinct response. This registry
lists the possible source routes and separates usable future paths from
controls and forbidden rescue paths.

## Run

```text
python3 scripts/build_source_split_external_k1_source_registry.py
```

It writes:

```text
evidence/source_split_external_k1_source_registry.csv
evidence/source_split_external_k1_source_readiness.csv
```

## Current Source Routes

Potential future routes:

- `K1SRC_LIKELIHOOD_NATIVE_JOINT_BASELINE`
- `K1SRC_EXTERNAL_RECONSTRUCTION_FAMILY_MEAN`
- `K1SRC_INDEPENDENT_PUBLIC_MODEL_RESPONSE`
- `K1SRC_EXTERNAL_PUBLIC_RESPONSE_OPERATOR`

Control or forbidden routes:

- `K1SRC_CURRENT_ZERO_CONTRAST_CONTROL`
- `K1SRC_SINGLE_BRANCH_RESPONSE_CONTROL`
- `K1SRC_SAME_DATA_AMPLITUDE_RESCUE`

## Current Decision

No route is currently authorized for external K1 export.

The most direct future route is a likelihood-native joint SN+BAO no-memory
baseline with frozen parameters and covariance. A family-mean route is also
possible, but only if the averaging and amplitude policy are declared before
K2 scoring and not chosen from K2 residual improvement.

## Interpretation

This registry does not add a new result. It prevents the measurement gate from
silently turning a diagnostic control into a primary K1 target. The next input
must fill:

```text
data/k1/source_split_external_k1_response.csv
```

using one of the allowed provenance classes in the external K1 schema.
