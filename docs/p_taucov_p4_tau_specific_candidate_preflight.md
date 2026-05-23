# P-TauCov P4 Tau-Specific Candidate Preflight

Status: `P_TAUCOV_P4_TAU_SPECIFIC_CANDIDATE_PREFLIGHT_FAIL_NO_SCORING`.

This is a target-blind morphology-orthogonalization preflight. It
does not run the empirical covariance scorecard and does not authorize
a survival claim.

## Key Numbers

- gates passed: `3/6`
- tau norm retained after morphology projection: `0.8309489698388166`
- support entropy P3: `0.6624895835336544`
- support entropy P4: `0.5942413953034713`
- kernel correlation with P3: `0.9424155050068755`
- kernel correlation with morphology-null: `0.8893567053441822`
- projection-null abs correlation: `0.8565316433152965`
- shuffled-support abs correlation: `0.665272141460644`
- max family energy share: `0.19882475456411108`
- max clock energy share: `0.16971387889717798`

## Interpretation

A passing preflight would authorize only the construction of a scoring
authorization artifact. A failing preflight blocks P4 scoring and means
the Tau-specific residual component is still not clean enough.
