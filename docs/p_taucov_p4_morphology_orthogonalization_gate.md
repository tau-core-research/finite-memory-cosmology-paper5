# P-TauCov P4 Morphology-Orthogonalization Gate

Status: design gate only / no P4 kernel freeze / no scoring authorization.

The epsilon-P3 primary covariance response was strongly positive, but it did
not survive the declared null suite. The decisive failure was the
`MORPHOLOGY_NULL` comparator:

```text
primary OOS DeltaNLL         = 100.19382563738316
morphology-null OOS DeltaNLL = 141.52376290434955
kernel correlation           = 0.9087206104563529
dominant failure family      = REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY
```

This means the next P-TauCov step must not be a score-tuned v4. It must first
define a Tau-specific response component that is not reducible to generic
morphology covariance.

## Required P4 Construction Principle

A future P4 candidate must decompose the projected covariance response into:

```text
delta C_Tau = delta C_morphology_shared + delta C_tau_specific
```

where `delta C_tau_specific` is declared before scoring and is constructed from
Tau-side structure, not from the empirical residual score.

The minimal admissible route is:

```text
delta C_tau_specific
  = delta C_Tau
    - Proj_morph(delta C_Tau)
```

where `Proj_morph` must be defined from frozen morphology-basis operators only.
The projection basis may use the declared morphology axes and their symmetric
covariance closure, but it may not use:

- target residuals;
- fold-level score outcomes;
- the identity of the dominant positive family;
- post-score alpha behavior;
- any P3-vs-null score margin.

## Pre-Scoring Specificity Requirements

Before any P4 scoring is allowed, the candidate must pass all of the following
target-blind gates:

| Gate | Requirement | Purpose |
| --- | --- | --- |
| P4-G1 | nonzero residual Tau component after morphology projection | avoids pure morphology-null duplication |
| P4-G2 | primary-vs-morphology-null kernel correlation below `0.75` | requires structural separation from the failed P3 null |
| P4-G3 | branch support entropy at least as broad as P3 | avoids single-family rescue |
| P4-G4 | no declared family or clock block may carry more than `0.60` of pre-score kernel energy | blocks family-localized tuning |
| P4-G5 | projection-null and shuffled-support correlations remain below `0.60` | preserves projection/branch specificity |
| P4-G6 | all thresholds, basis choices, and hashes frozen before scorecard execution | blocks after-the-fact model selection |

If any gate fails, P4 remains a design note and cannot be promoted to a scoring
candidate.

## Allowed And Forbidden Claims

Allowed statement:

```text
P3 produced a strong local covariance anomaly, but the morphology-null
dominance forces the next Tau-specific route to remove morphology-shared
covariance before scoring.
```

Forbidden statement:

```text
P3 validated Tau Core, and P4 should be tuned until it beats the morphology
null.
```

## Next Artifact

The next legitimate artifact is a frozen morphology-basis packet:

```text
docs/p_taucov_p4_morphology_basis_packet.md
evidence/p_taucov_p4_morphology_basis.csv
scripts/build_p_taucov_p4_morphology_basis_packet.py
scripts/validate_p_taucov_p4_morphology_basis_packet.py
```

Only after that packet passes target-blind validation can a P4
Tau-specific covariance candidate be constructed.
