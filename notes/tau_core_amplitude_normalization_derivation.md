# Tau-Core Amplitude Normalization Derivation

Status: working derivation / no measurement-validation claim

## Problem

The locked finite-memory response

```text
K2_locked(x) = K1(x) * W(x)
W(x) = 1 + 4*x^3
```

captures the source-split direction and strengthens with depth, but its raw
amplitude is still low:

```text
all-points scale need: about 2.9
mid-depth scale need: about 3.4
high-depth scale need: about 2.1
low-depth scale need: about 16, not physically stable
```

The task is not to fit this scale. The task is to ask whether tau-core
projection logic can naturally produce an effective mid/high-depth gain of
order 2-3 while keeping the low-depth response weak.

## Observable

The source-split target is not a direct one-channel observable. It is a
difference observable:

```text
R_split = R_SN - R_BAO
```

Tau-core projection therefore enters through two measurement channels:

```text
R_SN  = B_SN  + g_SN(x)  * M_tau(x)
R_BAO = B_BAO + g_BAO(x) * M_tau(x)
```

where:

```text
B_SN, B_BAO  = channel baselines / non-tau residual pieces
M_tau(x)     = finite-memory tau response
g_SN, g_BAO  = channel projection gains
```

So:

```text
R_split = (B_SN - B_BAO) + (g_SN(x) - g_BAO(x)) * M_tau(x)
```

The locked K2 curve is best interpreted as a unit-gain memory backbone:

```text
K2_locked(x) ~= M_tau_unit(x)
```

The measured source-split response can therefore require an additional
projection gain:

```text
R_split_tau(x) ~= A_tau(x) * K2_locked(x)
A_tau(x)       = g_SN(x) - g_BAO(x)
```

This is not a new kernel. It is the observable projection gain of the same
finite-memory backbone into a difference measurement.

## Why A_tau can be order 2-3

In a difference observable, two channel responses can add rather than cancel.
If the SN and BAO projectors respond with opposite effective sign to the same
tau-memory source, then:

```text
g_SN - g_BAO ~= g_SN + |g_BAO|
```

A conservative channel-level example:

```text
g_SN  ~= 1.2
g_BAO ~= -1.0
A_tau ~= 2.2
```

or:

```text
g_SN  ~= 1.5
g_BAO ~= -1.3
A_tau ~= 2.8
```

This produces the observed kind of 2-3x gain without changing:

```text
W(x)
p = 3
rho <= 4
K1
```

The gain belongs to the measurement projection, not the finite-memory kernel.

## Why low-depth remains weak

The finite-memory part is still gated by:

```text
W(x) - 1 = 4*x^3
```

At low depth this is small:

```text
x ~= 0.35-0.47
4*x^3 ~= 0.16-0.41
W ~= 1.16-1.41
```

At high depth:

```text
x ~= 0.82-1.00
4*x^3 ~= 2.24-4.00
W ~= 3.24-5.00
```

Therefore even if the projection gain is order 2-3, the memory-specific
increment is naturally much more visible at mid/high depth than at low depth.

The low-depth scale estimate around 16 should not be interpreted as a physical
amplitude normalization. It is a warning that the low-depth source-split target
is dominated by non-memory baseline/source terms while K2 is intentionally
weak there.

## Minimal tau-core amplitude form

A cautious tau-core form is:

```text
R_split(x) = B_split(x) + A_tau(x) * K1(x) * (1 + 4*x^3)
```

with the restriction:

```text
A_tau(x) is not fitted freely in this note.
```

For the current evidence, the viable testable hypothesis is narrower:

```text
A_tau(x) is approximately stable only in the memory-active regime:
mid/high depth.
```

Operationally:

```text
A_tau_mid_high ~= 2-3
A_tau_low      is not identifiable from K2 because the memory gate is weak
```

## Why this is tau-core compatible

Tau-core projection principles predict that an observed residual is not the raw
tau response itself. It is the response after:

```text
1. finite-memory gating,
2. observer/channel projection,
3. source-split differencing,
4. covariance/standardization of the measurement space.
```

The locked K2 operator covers step 1. The 2-3x factor can arise from steps 2-4,
especially source-coherent differencing:

```text
same tau source -> two different projectors -> difference observable
```

That is why the amplitude gap should be treated as a projection-normalization
problem before changing the kernel.

## Current decision

Most viable next direction:

```text
derive or externally constrain A_tau for the memory-active mid/high-depth
regime, without fitting K1 or changing W(x).
```

Falsification-relevant outcomes:

```text
supportive:
  A_tau_mid_high is stable around 2-3 and low-depth remains memory-weak.

weakening:
  A_tau varies wildly inside mid/high depth or requires sign flips.

strong negative:
  explaining the signal requires changing p, rho>4, refitting K1, or using a
  free pointwise A_tau.
```

