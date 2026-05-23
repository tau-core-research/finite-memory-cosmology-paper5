# P-TauCov Next-Candidate Admissibility Gate

Status: `P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_PASS_NO_SCORING`.

The previous PSD and signed-response candidates failed. A next
candidate is admissible only if it is designed to avoid the observed
failure modes before any new score is computed.

## Required Design Constraints

- diagonal support must be removed or explicitly orthogonalized;
- family-balance constraints must be frozen before scoring;
- support must be held-out or parent-derived, not selected from the
  observed score failure;
- signed, projection, morphology, and generic-null discipline must be
  retained;
- unconstrained v4 score search is forbidden.

## Claim Boundary

This is a meta-gate only. It authorizes no scoring and no positive
scientific claim.
