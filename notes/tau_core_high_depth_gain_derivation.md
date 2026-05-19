# Tau-Core High-Depth Gain Derivation

Status: working tau-core derivation / no measurement-validation claim

## Result to explain

The current source-split decomposition finds:

```text
high-depth A_tau ~= 2.08
high-depth cosine(target, A_tau*K2) ~= 0.99
high-depth point gains ~= 1.85, 2.44, 2.51
```

This is the cleanest memory-active region. Low depth is not a stable gain
estimator because the finite-memory increment is intentionally weak there.

## Tau-core interpretation

The locked K2 term is the unit memory backbone:

```text
M_tau_unit(x) = K1(x) * (1 + 4*x^3)
```

The source-split observable is a channel difference:

```text
R_split = R_SN - R_BAO
```

If both channels are responding to the same tau-memory source, but with
different projectors:

```text
R_SN  = B_SN  + g_SN  * M_tau_unit
R_BAO = B_BAO + g_BAO * M_tau_unit
```

then the observed tau part is:

```text
R_split_tau = (g_SN - g_BAO) * M_tau_unit
```

Define:

```text
A_tau = g_SN - g_BAO
```

The high-depth result suggests:

```text
A_tau_high ~= 2.1
```

This can arise without changing K2 if the two measurement projectors are
partially anti-aligned in the source-split channel. For example:

```text
g_SN  ~=  1.1
g_BAO ~= -1.0
A_tau ~=  2.1
```

or:

```text
g_SN  ~=  1.3
g_BAO ~= -0.8
A_tau ~=  2.1
```

The factor is therefore a projection/difference gain, not a new memory kernel.

## Why this is not arbitrary fitting

The gain is not pointwise and is not used to change:

```text
p
rho
K1
W(x)
```

It is only meaningful if a single high-depth gain predicts the high-depth
points together and gives a controlled degradation toward mid/low depth.

The required check is:

```text
take A_tau_high from the high-depth subset
apply it to all depth zones
ask where the prediction remains coherent
```

Expected tau-core behavior:

```text
high-depth: coherent
mid-depth: transitional / partial
low-depth: weak or baseline-dominated
```

## Falsification-relevant readings

Supportive:

```text
A_tau_high is stable across high-depth points and does not require sign flips.
```

Weakening:

```text
The same high-depth gain fails immediately in the neighboring mid-depth
memory-active region.
```

Strong negative:

```text
Explaining high-depth requires pointwise gain, rho>4, kernel change, or K1 refit.
```

