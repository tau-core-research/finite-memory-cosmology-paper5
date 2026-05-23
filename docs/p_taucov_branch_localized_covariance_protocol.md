# P-TauCov: A Predeclared Branch-Localized Covariance Response Protocol

Status: protocol draft / no scoring authorization.

Protocol ID:

```text
P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1
```

This protocol is the Tau-specific continuation of the P5C v3 closeout. It is
not a v4 scoring attempt. It defines what must be frozen before testing whether
a branch-localized covariance response is predicted by the Tau Core mechanism
rather than discovered post hoc from the P5C v3 outcome.

## Abstract

P5C v3 produced a strong local covariance anomaly but failed global survival
because the effect was too localized and was beaten by a family-permuted
control. P-TauCov converts that failure mode into a stricter prospective test:
the branch support, covariance-response direction, alignment statistic,
controls, and success/failure gates must be derived from a Tau branch-response
calculation before any new scoring. The protocol therefore asks whether Tau
Core predicts where a covariance anomaly should live, not merely whether a
post-hoc covariance kernel can be made to fit.

This document is a protocol and claim-boundary artifact. It authorizes no score,
no v4 kernel, and no Tau Core validation claim.
It is not a full Tau Core validation.

## 1. Motivation From P5C v3

The P5C v3 PSD covariance-deformation scorecard ended in the status:

```text
P5C_V3_STRONG_LOCAL_COVARIANCE_SIGNAL_BUT_NO_GLOBAL_SURVIVAL
```

The result was strong but localized:

- primary OOS DeltaNLL: `118.95867815449658`;
- gates passed: `8/10`;
- failed gates: `BEATS_FAMILY_PERMUTED`, `NO_SINGLE_FAMILY_DOMINANCE`;
- dominant positive family: `REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY`;
- dominant positive-family gain share: `0.9725229318494162`.

This is not a Tau Core validation. It is an anomaly candidate. P-TauCov asks a
new, stricter question: can Tau Core predict a localized covariance-response
support before scoring?

## 2. Parent Branch Equation

Let the branch variable be determined by a reduced branch equation

```math
B = B_*(\Phi),
```

with linear response

```math
\delta B_*
=
- (L_B^{\rm red})^{-1} D_\Phi F_B[\delta \Phi].
```

Here:

- `Phi` is the parent perturbation direction;
- `B` is the reduced branch state;
- `F_B` is the reduced branch equation;
- `L_B^{red}` is the reduced branch linearization;
- the inverse is allowed only on the declared reduced branch domain.

## 3. Projected Morphology

The projected morphology is defined as

```math
M_{\rm proj}(\Phi,B)
=
P_{\rm morph}(\Phi,B) M_{\rm parent}(\Phi,B).
```

This separates the parent morphology from the observational/projection map.
`P_morph` must be declared before scoring. It cannot be chosen from the
observed covariance residual.

## 4. Tau Morphology Response

The Tau morphology response is

```math
T_{\tau}
=
D_\Phi M_{\rm proj}
-
D_B M_{\rm proj} (L_B^{\rm red})^{-1} D_\Phi F_B.
```

Interpretation:

- the first term is the direct parent morphology response;
- the second term is the reduced-branch relaxation correction;
- the subtraction is not optional, because the branch state follows `B_*(Phi)`.

If the branch relaxation term is omitted, the protocol becomes a generic
morphology test and fails P-TauCov admissibility.

## 5. Predicted Covariance Response

The predicted Tau covariance response is

```math
\delta C_{\tau}
=
D_M C[T_{\tau}\delta\Phi].
```

`delta C_Tau` is the only object allowed to select branch support. In this
document `delta C_Tau` denotes the matrix or bilinear covariance-response
object represented by the displayed `\delta C_{\tau}` formula.

Forbidden:

```text
choose branch support from P5C v3 gains;
choose branch support from family labels after scoring;
choose branch support from observed covariance residuals;
choose branch support from the signed diagnostic if PSD primary fails.
```

## 6. Branch Support Rule

Before scoring, define a support object:

```text
W_branch or Omega_branch
```

using only `delta C_Tau`.

The default continuous branch weight is

```math
W_{\rm branch}(i,j)
=
\frac{|\delta C_{\tau}(i,j)|}
{\sum_{a,b}|\delta C_{\tau}(a,b)|}.
```

The default binary branch support is fixed by a predeclared mass fraction
`q_branch`:

```math
\Omega_{\rm branch}
=
\left\{(i,j): W_{\rm branch}(i,j) \text{ lies inside the smallest set carrying }
q_{\rm branch} \text{ of total predicted response mass}\right\}.
```

Allowed variants:

```text
top-q support of |delta C_Tau| with q fixed before scoring;
connected support of a thresholded delta C_Tau graph;
branch-domain support selected by the declared reduced operator L_B^red;
family/clock support predicted by T_tau before outcome inspection.
```

Not allowed:

```text
the branch that produced the largest P5C v3 gain;
the family-permuted null failure pattern;
the LOSS_COMPLEXITY family unless independently derived from delta C_Tau;
any support chosen after the P-TauCov score is known.
```

## 7. Alignment Statistic

Let `S_obs` be the held-out whitened covariance residual statistic under the
declared baseline. Let `Pi_branch` be the branch-support projector derived only
from `delta C_Tau`.

The primary alignment statistic is a normalized Frobenius alignment:

```math
S_{\tau}
=
\frac{
\langle
\Pi_{\rm branch} S_{\rm obs} \Pi_{\rm branch},
\Pi_{\rm branch} \delta C_{\tau} \Pi_{\rm branch}
\rangle_F
}{
\|\Pi_{\rm branch} S_{\rm obs} \Pi_{\rm branch}\|_F
\|\Pi_{\rm branch}\delta C_{\tau}\Pi_{\rm branch}\|_F
}.
```

The exact whitening convention, baseline covariance, folds, and branch support
threshold must be frozen before scoring.

If the denominator is zero on a held-out fold, that fold is scored as invalid
and the protocol fails unless the zero-denominator condition was itself
predeclared as an exclusion before any target score was seen.

## 8. Controls

P-TauCov survival requires the primary alignment to beat all declared controls.

### Outside-Branch Control

Score the complement:

The same statistic is evaluated on the complement of `Omega_branch`.

Requirement:

```text
inside branch alignment > outside branch alignment by the frozen margin
```

### Shuffled Control

Shuffle branch support while preserving support size and family/clock counts
where applicable.

Requirement:

```text
inside branch alignment beats the frozen shuffled-support null distribution
```

### Morphology-Null Control

Replace `T_tau` with a morphology-null response that preserves smoothness or
energy but destroys the Tau branch-relaxation structure.

Requirement:

```text
T_tau alignment beats morphology-null alignment
```

### Projection-Null Control

Replace `P_morph` with a projection-null map that preserves observable support
size but breaks the parent-projection coupling.

Requirement:

```text
T_tau alignment beats projection-null alignment
```

### Generic Baseline Control

Compare against generic covariance operators:

```text
random smooth PSD;
family-permuted support;
diagonal variance inflation;
wrong-clock support;
phase-shift support.
```

Requirement:

```text
P-TauCov beats the strongest declared generic baseline.
```

## 9. Success Criteria

P-TauCov passes only if all of the following are true:

1. `delta C_Tau` is generated without target residuals or P5C v3 gains.
2. `W_branch` or `Omega_branch` is derived only from `delta C_Tau`.
3. Primary inside-branch `S_Tau` is positive on held-out folds.
4. Inside-branch alignment beats outside-branch alignment.
5. Inside-branch alignment beats shuffled support.
6. Inside-branch alignment beats morphology-null response.
7. Inside-branch alignment beats projection-null response.
8. Inside-branch alignment beats generic covariance baselines.
9. No single fold supplies more than `60%` of the positive alignment gain unless
   that localization was explicitly predicted by `delta C_Tau` before scoring.
10. The signed diagnostic, if computed, remains diagnostic only unless a
    separate signed protocol is frozen.
11. The same claim boundary is used regardless of whether the result is
    positive, negative, or mixed.

## 10. Failure Criteria

P-TauCov fails if any of the following occur:

```text
branch support chosen from v3 outcome;
delta C_Tau built using held-out residuals;
inside-branch alignment does not beat outside-branch alignment;
family-permuted or shuffled support beats Tau support;
morphology-null or projection-null beats Tau response;
generic smooth PSD explains the effect equally well;
claim relies on signed diagnostic after PSD primary fails;
branch localization is explained only by the P5C v3 family-gain pattern.
```

## 11. Relationship To P5C v3

P5C v3 remains:

```text
anomaly candidate only
```

Allowed statement:

```text
P5C v3 motivates a Tau-specific branch-localized covariance protocol because it
showed a strong local covariance signal without global survival.
```

Forbidden statement:

```text
P5C v3 already establishes a Tau Core branch-localized response.
```

P-TauCov is the required bridge between those statements.

P5C v3 inputs that may be reused:

```text
frozen folds;
baseline covariance policy;
declared null comparator classes;
closeout status and negative gates.
```

P5C v3 inputs that may not be reused for support selection:

```text
family-localized gain pattern;
dominant positive family;
observed OOS DeltaNLL pattern;
signed diagnostic advantage;
failed family-permutation gate.
```

## 12. Required Freeze Artifacts

Before any P-TauCov score is run, create:

```text
freeze_p_taucov_branch_support.py
validate_p_taucov_branch_support.py
build_p_taucov_final_manifest.py
validate_p_taucov_scoring_authorization.py
run_p_taucov_alignment_scorecard.py
```

Required outputs:

```text
evidence/p_taucov_branch_support_freeze.csv
evidence/p_taucov_branch_support_freeze.yaml
evidence/p_taucov_control_registry.csv
evidence/p_taucov_success_failure_gates.csv
evidence/p_taucov_final_manifest.yaml
docs/p_taucov_branch_support_freeze.md
docs/p_taucov_final_manifest.md
```

The final manifest must explicitly state:

```text
ScoringAuthorized: true or false
BranchSupportSource: delta_C_Tau_only
V4KernelAuthorized: false unless P-TauCov branch support is frozen
P5Cv3Status: anomaly_candidate_only
SurvivalClaimAllowedBeforeScore: false
```

## 13. Claim Boundary

Until P-TauCov passes:

```text
P5C v3 is a constrained positive anomaly, not a Tau-specific covariance proof.
```

If P-TauCov passes, the allowed claim becomes:

```text
A predeclared Tau-derived branch-localized covariance response aligns with
held-out covariance residual structure beyond outside-branch, shuffled,
morphology-null, projection-null, and generic covariance baselines.
```

Even then, it remains a branch-localized covariance-response result, not a full
Tau Core validation.
