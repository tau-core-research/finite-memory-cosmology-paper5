# P-TauCov Diagonal-Orthogonal Candidate Spec

Status: `P_TAUCOV_DIAGONAL_ORTHOGONAL_CANDIDATE_SPEC_PASS_NO_SCORING`.

This candidate removes the diagonal component from the failed
branch-localized signed map before any new scoring. It directly
addresses the diagonal-control failure mode observed in the signed
scorecard.

Construction:

```text
K_signed -> K_signed with diagonal set to zero -> Frobenius normalize
```

- raw diagonal norm: `0.9428090415820634`
- final diagonal norm: `0.0`
- minimum eigenvalue: `-0.7071067811865476`
- maximum eigenvalue: `0.7071067811865476`

This is a candidate specification only. It does not authorize scoring.
