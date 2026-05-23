# P5C Kernel v3 Closeout

Status: `P5C_V3_STRONG_LOCAL_COVARIANCE_SIGNAL_BUT_NO_GLOBAL_SURVIVAL`

The v3 PSD covariance-deformation scorecard produced a strong positive primary OOS signal, but it did not satisfy the frozen global survival gates.

## Scorecard Result

- primary OOS DeltaNLL: 118.95867815449658
- gates passed: 8/10
- failed gates: `BEATS_FAMILY_PERMUTED`, `NO_SINGLE_FAMILY_DOMINANCE`
- family-permuted null DeltaNLL: 127.48310006083611
- v3 DeltaNLL: 118.95867815449658

## Family Localization

The positive gain is strongly localized:

- dominant family: `REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY`
- dominant positive-family gain share: 0.9725229318494162

This is why the result cannot be promoted to global survival.

## Claim Boundary

Allowed claim:

```text
P5C v3 shows a strong local covariance signal under the frozen PSD covariance-deformation scorecard.
```

Forbidden claim:

```text
P5C v3 globally survives, validates Tau Core, or establishes an empirical detection.
```

## Decision

Do not build v4 from this outcome alone. A v4 attempt would require an independent theoretical reason for either:

1. a global orientation correction; or
2. a branch-localized claim boundary declared before scoring.

The signed operator-contrast remains diagnostic only.
