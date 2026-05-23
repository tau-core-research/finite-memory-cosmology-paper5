# P-TauCov Family-Balance Policy

Status: `P_TAUCOV_FAMILY_BALANCE_POLICY_FROZEN_NO_SCORING`.

A future candidate cannot pass if its positive signed/alignment
contribution is effectively carried by one family.

Frozen requirements:

- at least `2` positive contributing families;
- largest positive family contribution share must be `<= 0.5`;
- leave-one-family-out folds remain primary;
- clock-block folds remain primary.

This policy uses only family labels and row counts, not target
residuals or score outcomes.
