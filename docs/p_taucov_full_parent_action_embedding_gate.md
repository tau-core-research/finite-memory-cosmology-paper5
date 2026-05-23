# P-TauCov Full Parent-Action Embedding Gate

Status: embedding gate / no full action / no empirical scorecard / no survival
claim.

The minimal scaffold proves that a three-term active sector can generate the
projection-essential witness:

```math
S_{\rm scaffold}^{\rm active}
=
\int d\mu_\tau
\left[
-\frac{1}{2}B^2
-2PB
-P\Phi
\right].
```

The remaining problem is that `S_rest` is not yet specified. This document
defines the gate that must be passed before the scaffold can be promoted from a
local parent-action scaffold to a full parent-action candidate.

## Required Embedding Conditions

| Gate | Requirement |
| --- | --- |
| EMB-G1 | declared parent domain: compact-cell or continuum configuration space |
| EMB-G2 | declared measure `dmu_tau` and normalization convention |
| EMB-G3 | declared null/gauge modes and reduced branch domain |
| EMB-G4 | stable reference background `Psi_0` or equivalent stationary state |
| EMB-G5 | active sector Hessian remains unchanged after embedding |
| EMB-G6 | `S_rest` does not reintroduce forbidden `P^2`, `Phi^2`, `M`, target, or score terms into the witness sector |
| EMB-G7 | covariance map `D_M C` is declared independently of empirical score outcomes |
| EMB-G8 | no target residuals, OOS scores, alpha behavior, or dominant-family identity |

## Promotion Rule

The scaffold may be promoted only if all embedding gates pass. Passing the
embedding gates would authorize a full parent-action candidate packet, not an
empirical scorecard.

## Claim Boundary

Allowed:

```text
The full-action embedding requirements are declared.
```

Forbidden:

```text
The scaffold is already embedded in a final Tau Core action or has produced a
Tau-specific empirical signal.
```

## Next Artifact

The next valid artifact is:

```text
docs/p_taucov_candidate_full_parent_action_packet.md
```

It must instantiate all EMB-G1 to EMB-G8 fields before any new covariance
candidate or score authorization is considered.
