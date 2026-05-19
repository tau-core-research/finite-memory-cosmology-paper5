# Tau-Core Projection Gain Prior

Status: derivation candidate / not a fitted measurement result

## Purpose

The high-depth source-split check suggests:

```text
A_tau_high ~= 2.08
```

This note asks whether a gain near 2 can be motivated from tau-core projection
geometry before treating it as a measurement parameter.

## Source-split projector form

Let the same finite-memory tau source enter two observational channels:

```text
R_SN  = B_SN  + g_SN  * M_tau
R_BAO = B_BAO + g_BAO * M_tau
```

The source-split observable is:

```text
R_split = R_SN - R_BAO
```

so:

```text
R_split_tau = (g_SN - g_BAO) * M_tau
```

The projection gain is:

```text
A_tau = g_SN - g_BAO
```

## Natural gain near 2

If the two channels are approximately opposite projections of the same
tau-memory mode:

```text
g_SN  ~= +1
g_BAO ~= -1
```

then:

```text
A_tau ~= 2
```

This is the simplest source-coherent differencing gain. It does not require a
new memory kernel. It says that the source-split observable doubles an
anti-aligned common mode.

The observed high-depth value:

```text
A_tau_high ~= 2.08
```

is close to this natural symmetric limit:

```text
A_tau_sym = 2
relative deviation ~= 4%
```

## Why the sign is compatible

The current source-split response and locked K2 have matching signs in all
tested rows. Therefore the high-depth gain does not require a sign flip:

```text
A_tau_high > 0
```

That is consistent with:

```text
g_SN - g_BAO > 0
```

and with an anti-aligned pair such as:

```text
g_SN  > 0
g_BAO < 0
```

## Why this should be high-depth only

The finite-memory increment is:

```text
W(x) - 1 = 4*x^3
```

The projection gain can only be cleanly read where the memory response is
large enough. In low depth, K2 is intentionally weak and the source-split target
is baseline dominated. Therefore the low-depth implied gain is not a valid
prior estimator.

## Proposed locked prior for future tests

For preflight checks, the least flexible tau-core prior is:

```text
A_tau_prior = 2
```

Interpretation:

```text
anti-aligned unit projection in a source-split observable
```

Allowed diagnostic tolerance:

```text
A_tau_high may be compared to 2, but not fitted pointwise.
```

Recommended next test:

```text
Compare A_tau = 1, A_tau = 2, and A_tau = A_tau_high_diagnostic
against the current source-split target.
```

The important question:

```text
Does the predeclared A_tau = 2 prior already recover the high-depth amplitude?
```

If yes, the 2.08 value can be treated as a consistency observation rather than
a fitted parameter.

