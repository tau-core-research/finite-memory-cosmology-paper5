# Source-Split K1 Target Plan

Status: zero-contrast coordinate-native K1 control exported; no K2 scoring
target selected.

The source-split branch now has public SN and BAO inputs, residual preflight
rows, a standardized branch comparison, and a sign-tension diagnosis. The
remaining blocker is the K1/no-memory target: the object that K2 would multiply
must be defined in the same coordinate-native source-split space before K2 is
scored.

## Why This Matters

K2 is a multiplicative finite-memory correction:

```text
K2(x) = W(x) * K1(x)
```

If `K1(x)` is not fixed before scoring, then the measurement gate can
accidentally absorb the desired effect into the baseline. That would make the
finite-memory comparison meaningless.

## Registered Candidates

The registry is:

```text
evidence/source_split_k1_target_registry.csv
```

The readiness output is:

```text
evidence/source_split_k1_target_readiness.csv
```

Run:

```text
python3 scripts/check_source_split_k1_target.py
```

## Current Decision

No candidate is currently allowed for K2 scoring.

- The current distilled K1 is useful for method-note provenance only.
- The SN-only centered residual uses a same-sample offset and does not include
  BAO.
- The BAO-only CMB candidate is a control and was not competitive with the
  zero-response null.
- The standardized zero-response object is a fair null/control, not a K1
  target.
- The coordinate-native source-split zero-contrast control is exported, but it
  is not allowed for K2 scoring until joint covariance and public sign-family
  exports exist.
- The likelihood-native source-split target is planned but not exported.

## Next Required Object

The exported coordinate-native control is:

```text
SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET
```

Its current no-memory definition is:

```text
K1NoMemoryResponse = 0
```

meaning zero standardized SN-minus-BAO branch contrast before finite-memory
correction. It uses no same-data amplitude fit.

For scoring, the branch still needs:

- a declared joint covariance or shrinkage covariance;
- a sign-family export policy.

Until those objects exist, source-split K2 scoring remains closed.
