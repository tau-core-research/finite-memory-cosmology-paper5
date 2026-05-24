# P-TauCov Active-Triad PSD Ceiling Audit

Freeze ID: `P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_AUDIT_v1`

Status:

`P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_BLOCKS_SCORING_NO_SCORING`

## Purpose

The projection-coupled reduced-Jacobian candidate fixed the missing projection
channel, but failed because its PSD lift remained diagonal-dominated and
low-rank. This audit asks whether that failure is an accident of the chosen
minimal weights or a structural ceiling of the current active reduced triad.

The active triad is:

```text
Phi = TEMPLATE_PHI_PARENT_SOURCE
B   = TEMPLATE_B_BRANCH_RESPONSE
P   = TEMPLATE_P_MORPH_PROJECTION
```

## Target-Blind Scan

The audit scans deterministic off-diagonal triad source shapes:

```text
J = a |Phi><B| + b |Phi><P| + c |B><P| + transpose
```

with `a`, `b`, and `c` selected from a fixed no-score grid. The PSD lift is:

```text
C = J J^T / ||J J^T||_F
```

This is a structural ceiling audit only. It uses no target residuals, no score
outcomes, and no family gains.

## Result

- scanned rows: `216`
- joint pass rows for diagonal share `<= 0.80` and effective-rank fraction
  `>= 0.30`: `0`
- best diagonal energy share found: `0.8164965809277261`
- effective-rank fraction at best diagonal case:
  `0.29763769724403744`
- best effective-rank fraction found:
  `0.29763769724403744`
- diagonal energy share at best-rank case:
  `0.8164965809277261`

## Interpretation

Within the current three-coordinate active triad, a PSD-lifted covariance
candidate is structurally pushed toward diagonal dominance and marginal rank.
The next Tau-side route should therefore not merely retune the `Phi/B/P`
weights. It must either:

1. introduce a broader parent-side curvature/operator source with additional
   target-blind active support; or
2. open a separately frozen signed-operator-contrast protocol whose claim is
   not PSD covariance survival.

## Claim Boundary

Allowed statement:

> The current active triad is too narrow for the PSD covariance route under the
> existing specificity gates.

Forbidden statement:

> This audit authorizes scoring, tunes a new candidate, or validates Tau Core.
