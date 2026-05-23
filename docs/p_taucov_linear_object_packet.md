# P-TauCov Linear-Object Packet

Status: derived target-blind linear objects / no metric evaluation / no scoring
authorization.

This packet deterministically derives the linear objects from the frozen
minimal source packet:

```text
L0_B  = K_B + Gamma_B
R_B   = -D_Phi_J_B
A_Phi = G_Phi
A_B   = G_B
P0    = P0_SOURCE
```

Under the current minimal baseline source packet this gives:

```text
L0_B  = P_red
R_B   = -P_red
A_Phi = P_red
A_B   = P_red
P0    = P_red
```

These are derived baseline linear objects, not empirical evidence and not a
positive P-TauCov result.

## Claim Boundary

Allowed statement:

```text
Target-blind baseline linear objects are frozen.
```

Forbidden statement:

```text
Metric evaluation, covariance response, or P-TauCov scoring is authorized.
```
