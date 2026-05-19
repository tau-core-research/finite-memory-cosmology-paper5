# Finite-Memory Projection Corrections In Cosmological Consistency Diagnostics

Working manuscript draft. Current claim level: theory-method diagnostic.

## Abstract

We introduce a bounded finite-memory projection operator for diagnostic
cosmological consistency tests. The operator is formulated as an effective
projection response over normalized depth, $W(x)=1+\rho x^3$, with a passive
memory-budget bound $\rho \leq 4$. The construction is not presented as a complete
cosmological model or a direct measurement claim. It is instead a disciplined
diagnostic module for comparing projected response shapes against
backreaction-aware distance consistency reconstructions. In a BAO-only
diagnostic reconstruction, the locked K2 window overlaps the full target
envelope. In an SN+BAO source-split stress test, strict median-sign matching
exhibits a localized tension; a reconstruction-aware sign-stability gate
keeps this tension classified as non-violating without widening the K2 window.
The result motivates a future full-likelihood comparison while preserving
explicit claim boundaries.

## 1. Introduction

Modern cosmological consistency tests increasingly distinguish background
expansion, light-propagation effects, curvature consistency, and cosmic
backreaction. A residual relative to a homogeneous FLRW reference model is
therefore not automatically evidence for new physics: it may arise from optical
sampling, reconstruction convention, averaging, or the choice of observable
combination.

Heinesen and Clifton recently emphasized that broad classes of cosmological
models can be separated by how they violate FLRW curvature-consistency tests
[1].
They isolate two especially relevant routes: deviations in optical properties
and deviations in large-scale expansion. This is naturally adjacent to the
older Dyer-Roeder optical-distance tradition, where light propagation through
clumpy matter distributions is treated separately from the homogeneous
background distance law [3,4]. Koksbang then applied this kind of
observable logic to constrain cosmic backreaction over an extended redshift
range, finding consistency with vanishing backreaction at one standard
deviation while also emphasizing that significant backreaction is not yet ruled
out [2]. These papers are useful here because they make the main methodological
lesson sharp: a projected cosmological residual must be tested against optical,
geometrical, and reconstruction degeneracies before it is interpreted.

This note develops a deliberately narrow finite-memory projection diagnostic
that can be placed alongside such tests. The objective is not to validate a full
physical model. Instead, we ask whether a predeclared, bounded
projection-memory operator can define a reproducible diagnostic window and
survive basic source-split stress tests.

The contribution is therefore threefold. First, we define a finite-memory
operator whose amplitude is bounded before comparison with reconstructed
diagnostics. Second, we give an explicit shape-selection rule that fixes the
cubic kernel from a small power-kernel family. Third, we state a sign-stability
policy for interpreting reconstructed diagnostic points whose median sign is
method-sensitive.

## 2. Relation To Existing Diagnostic Ideas

The present construction is closest in spirit to a consistency diagnostic, not
to a replacement background cosmology. In a standard FLRW interpretation,
distances, expansion rates, and curvature relations are locked together by the
assumed homogeneous geometry. A violation of one of these relations can point
to several different mechanisms: altered large-scale expansion, altered light
propagation, averaging effects, or reconstruction artifacts. This is why the
same residual pattern can be read very differently depending on whether one is
testing optical propagation, backreaction, or modified dynamics.

The finite-memory operator introduced here is designed to sit at this
interface. It does not start by changing the background Friedmann equations.
Instead, it asks whether a projected diagnostic response can carry a bounded
memory of accumulated depth. This makes it naturally comparable to
Dyer-Roeder-type optical reasoning, where light propagation through clumpy
matter is separated from the homogeneous reference law, and to modern
backreaction tests, where averaged expansion and observed distance relations
need not encode the same effective geometry.

The important difference is that the operator below is not an additional
free-form fitting function. Its amplitude and shape are constrained before the
diagnostic comparison. This is the main methodological point: the operator is
allowed to be phenomenological, but it is not allowed to become arbitrarily
elastic after seeing the reconstructed envelope.

For this reason, the most important object in the paper is not the specific
cubic formula by itself. The stronger contribution is the combination of a
bounded response window, a predeclared admissibility rule, and a
reconstruction-stability-aware interpretation policy.

## 3. Effective Diagnostic Module

Only the effective module needed for this note is used. We assume that an
observed consistency residual can be represented as a projected response over a
normalized depth coordinate,

$$
0 \leq x \leq 1 .
$$

The variable `x` should be read operationally: it orders the accumulated
projected response along the diagnostic light-path/reconstruction depth. In the
point-level diagnostic table below, the public packet uses the frozen
operational mapping

$$
x = z/z_{\max}
$$

over the tested SN+BAO redshift grid. This is a redshift-ordered diagnostic
coordinate, not a final physical identification of `x` with redshift and not a
new cosmological observable.

The finite-memory correction is a multiplicative response operator acting on a
baseline projected shape:

$$
K_2(x) = W(x)K_1(x).
$$

This note studies the locked K2 form

$$
W(x) = 1 + \rho x^3 .
$$

The form is intentionally simple. Its purpose is to test whether a bounded,
delayed, monotone memory response can be made reproducible before comparison
with diagnostic envelopes.

### Robustness And Coordinate Dependence

The present note is coordinate-explicit. Its numerical tables use

$$
x = z/z_{\max}
$$

as the current frozen operational diagnostic mapping. This choice is useful
because it is simple, reproducible, and tied directly to the public redshift
grid. It is not claimed to be a coordinate-invariant or physically final
description of cosmological depth.

Two natural robustness mappings are left for the next stage:

$$
x = \chi(z)/\chi(z_{\max}),
$$

where $\chi$ is a comoving-distance coordinate under a frozen reference
cosmology, and an optical-depth-like coordinate in which the depth variable is
weighted by foreground or visibility information. A likelihood-native mapping,
using the reconstruction grid or likelihood coordinate directly, is the Phase II
target. Until such mappings are implemented, the method note should be read as
a coordinate-explicit diagnostic proposal only.

### K1 Baseline Provenance

The baseline shape $K_1(x)$ is a frozen diagnostic baseline imported from the
distilled reconstruction packet. It is not fitted in this note. The comparison
is organized around whether the locked multiplicative memory factor can keep
the projected K2 response inside the reconstructed diagnostic envelope under
the predeclared amplitude and shape rules.

The present manuscript therefore tests the finite-memory multiplier on top of a
fixed diagnostic baseline. It does not establish that $K_1(x)$ is unique,
physically final, or likelihood-preferred.

Several assumptions are therefore intentionally modest:

- the coordinate $x$ is a diagnostic ordering variable, not a new directly
  measured cosmological coordinate;
- the operator $W(x)$ is an effective response, not a complete field equation;
- the reconstructed envelopes are treated as diagnostic targets, not as final
  likelihood surfaces;
- the public module does not require the reader to accept any broader
  background theory.

These restrictions make the paper weaker than a full theory paper, but stronger
as a falsifiable method note. A reader can reject or test the effective module
without needing to adjudicate any larger research program.

## 4. Passive Memory Bound

The passive memory-budget condition requires the accumulated tail response not
to exceed the unit local response budget. For the cubic operator,

$$
E_{\mathrm{tail}} = \int_0^1 \rho x^3\,dx = \frac{\rho}{4}.
$$

The unit baseline budget is

$$
E_0 = \int_0^1 1\,dx = 1.
$$

Passivity requires

$$
E_{\mathrm{tail}} \leq E_0,\qquad
\frac{\rho}{4} \leq 1,\qquad
\rho \leq 4 .
$$

This is the key discipline of the construction: the memory depth is bounded
before the diagnostic comparison. The bound is not chosen by looking for the
best residual fit.

The word "passive" is used in this limited sense only. It means that the memory
tail does not carry more integrated response budget than the local baseline
term over the normalized interval. It does not mean that the underlying
cosmology is static, nor that no physical energy exchange is possible in a
deeper model. For this paper, passivity is simply a guard against an
uncontrolled late-depth amplification.

This bound also gives an immediate falsification handle. If a diagnostic
comparison requires $\rho > 4$ in order to remain compatible with the target
envelope, the locked passive operator is not supported in its present form. The
model is not then rescued by expanding the allowed amplitude range.

## 5. Kernel-Shape Selection

The cubic kernel is selected from the power-kernel family

$$
W_p(x) = 1 + \rho x^p .
$$

For this family, the passive memory rule generalizes to

$$
\int_0^1 \rho x^p\,dx \leq \int_0^1 1\,dx,\qquad
\frac{\rho}{p+1} \leq 1,\qquad
\rho \leq p+1 .
$$

Two additional effective-operator rules select the usable shape:

$$
\Delta W_p(0.25) = (p+1)0.25^p \leq 0.10 ,
$$

$$
\int_{0.75}^{1} (p+1)x^p\,dx \leq 0.75 .
$$

The first rule rejects kernels that disturb the already locked low-depth
response too early. The second rejects kernels whose memory budget collapses
too sharply onto the last quarter of the path. In the present audit, `p=1` and
`p=2` are too visible at low depth, while `p>=4` is too endpoint-concentrated.
The cubic `p=3` case is the remaining admissible power-kernel representative.

The locked diagnostic window is therefore

$$
W(x) = 1 + \rho x^3,\qquad
\eta \in [0.25,0.50],\qquad
\rho \in [3.00,4.00].
$$

The two shape rules encode a compromise. A linear or quadratic memory term
becomes visible too early and risks contaminating the low-depth regime where
the baseline diagnostic response should remain dominant. Higher powers delay
the response more strongly, but at the cost of concentrating the correction too
close to the endpoint. The cubic term is therefore not claimed to be uniquely
fundamental; it is the lowest simple power that is late enough at low depth
while not being too endpoint-like.

This distinction matters for interpretation. The paper does not say that
cosmology "must" use a cubic memory law. It says that, inside this deliberately
small power-kernel audit, the cubic law is the locked representative that
survives the predeclared admissibility rules.

The numerical thresholds in these two rules should also be read conservatively.
They are method thresholds for the present diagnostic packet, not universal
constants. A later likelihood paper should report threshold-sensitivity runs
showing whether the cubic representative remains selected when the low-depth
visibility and endpoint-concentration cuts are varied within a reasonable
predeclared range.

The current threshold-sensitivity policy is summarized as follows:

| Threshold set | Low-depth limit | Endpoint budget | Admissible simple kernels | Interpretation |
|---|---|---|---|---|
| baseline | $\Delta W_p(0.25)\leq 0.10$ | endpoint $\leq 0.75$ | $p=3$ | cubic is the current audit-selected representative |
| relaxed low-depth | $\Delta W_p(0.25)\leq 0.15$ | endpoint $\leq 0.75$ | $p=2,3$ | more low-depth visibility broadens the set |
| strict low-depth | $\Delta W_p(0.25)\leq 0.075$ | endpoint $\leq 0.75$ | $p=3$ | cubic remains in this simple scan |
| relaxed endpoint | $\Delta W_p(0.25)\leq 0.10$ | endpoint $\leq 0.85$ | $p=3,4$ | endpoint relaxation admits a later kernel |
| strict endpoint | $\Delta W_p(0.25)\leq 0.10$ | endpoint $\leq 0.60$ | none | the simple power-kernel family can be emptied |

This means the cubic kernel is not a fundamental cosmological law. It is the
baseline representative selected by the current audit thresholds. Relaxing or
tightening those thresholds can broaden, shift, or empty the admissible simple
power-kernel set.

## 6. Diagnostic Targets And Gate Policy

The targets used here are reconstructed diagnostic envelopes rather than direct
published likelihoods. The comparison is therefore deliberately separated into
three levels:

```text
sign-stable reconstructed point   -> exact sign gate
sign-unstable reconstructed point -> envelope / diagonal residual gate
controls and extrapolations       -> stress diagnostics only
```

Operationally, let $y_i$ denote the reconstructed diagnostic median at the
tested point $i$, and let $[L_i,U_i]$ denote the corresponding reconstructed
diagnostic envelope. A locked prediction $\hat y_i$ is envelope-compatible
when

$$
L_i \leq \hat y_i \leq U_i .
$$

If a diagonal diagnostic width $\sigma_i$ is available, the normalized residual
gate is

$$
\left|\hat y_i-y_i\right|/\sigma_i \leq 1 .
$$

A reconstructed point is sign-stable only when the relevant method/degree
families agree on the sign of the diagnostic median. If the reconstruction
sign is method-sensitive, the median sign is not used as a hard falsifier.
Instead, the locked K2 prediction must remain inside the diagnostic envelope
and have a normalized residual not exceeding one standard diagnostic width.

This policy is not a substitute for a full likelihood. It is a triage rule that
prevents a method-sensitive reconstructed median from being overinterpreted.

This distinction is important for the SN+BAO stress test below. A strict
median-sign gate asks whether the prediction follows the sign of one
reconstructed median. The sign-stability gate asks a weaker but better-posed
question: whether the prediction violates a sign that is stable across
reconstruction choices. Only the second question is used as a paper-level
diagnostic violation/non-violation rule here.

## 7. Source-Split Interpretation

The BAO-only and SN+BAO diagnostics are not interchangeable. BAO-only
reconstructions are comparatively closer to a distance-scale consistency test,
while SN+BAO combinations mix distance ladder information and reconstruction
choices in a way that can sharpen or destabilize local features. A finite
memory operator should therefore not be judged only by whether it follows a
single reconstructed median. It should also be judged by whether a claimed
tension is robust across reconstruction families.

In the present packet, this is exactly where the localized SN+BAO warning
appears. The strict median-sign comparison identifies a point near `z=1.1925`
where the median sign is negative while the locked K2 response does not follow
that sign. The reconstruction audit, however, indicates that this sign is not
stable across the tested method/degree families. Lower-degree reconstructions
favor the opposite sign, while higher-degree reconstructions pull the median
negative.

The sign-stability policy is intended to prevent this point from being used in
either direction too aggressively. It should not be hidden, because it is a
real stress point for the diagnostic. It should also not be promoted to a hard
falsification, because the sign being tested is reconstruction-sensitive. The
paper-level statement is therefore deliberately asymmetric: the point remains a
warning, but not a locked diagnostic violation under the envelope and
normalized-residual gate.

## 8. Results

The minimal result summary is:

| Diagnostic | Result | Interpretation |
|---|---:|---|
| BAO-only window overlap | 1.0000000000 | Locked K2 overlaps the BAO-only diagnostic envelope at all tested points. |
| BAO-only best curve overlap | 1.0000000000 | The best locked K2 BAO-only curve remains inside the envelope. |
| SN+BAO sign-stable non-violation fraction | 1.0000000000 | All sign-stable SN+BAO points are non-violating under exact sign matching. |
| SN+BAO sign-unstable compatibility fraction | 1.0000000000 | All sign-unstable SN+BAO points remain envelope-compatible under diagonal residual handling. |

The strict SN+BAO median-sign test exhibits a localized tension near
`z=1.1925`. The diagnostic audit shows that this point is method-degree
sensitive: lower-degree reconstructions are positive, while higher-degree
reconstructions pull the median negative. The locked K2 prediction does not
follow the negative median sign at that point, but it remains inside the broad
diagnostic envelope with a small normalized residual. Under the sign-stability
gate, this is treated as an envelope-compatible warning rather than a hard
sign violation.

The current status is therefore:

```text
BAO-only: diagnostic compatibility
SN+BAO strict median-sign: localized warning
SN+BAO sign-stability-aware gate: non-violating diagnostic status
claim level: theory-method diagnostic, not measurement validation
```

The point-level SN+BAO audit makes the gate policy more explicit. The source
for all rows is the no-degree-4 robust SN+BAO envelope, and the `x` column uses
the provisional mapping $x=z/z_{\max}$ over this grid.

| z | x | median | envelope | K2 | signs all/no4/d2 | stable? | residual/sigma | decision |
|---:|---:|---:|---|---:|---|---|---:|---|
| 0.5100 | 0.2189 | 0.7758 | [-1.9013, 2.7631] | 2.0829 | +/+/+ | yes | -0.0350 | NONVIOLATING_SIGN_STABLE |
| 0.7375 | 0.3165 | 0.5350 | [-1.5846, 1.2890] | 1.3251 | +/+/+ | yes | -0.0565 | NONVIOLATING_SIGN_STABLE |
| 0.9650 | 0.4142 | 0.0906 | [-1.1023, 0.8498] | 0.7717 | +/+/+ | yes | 0.1417 | NONVIOLATING_SIGN_STABLE |
| 1.1925 | 0.5118 | -0.0762 | [-0.6967, 0.6401] | 0.3938 | -/-/+ | no | 0.1971 | COMPATIBLE_SIGN_UNSTABLE |
| 1.4200 | 0.6094 | 0.1560 | [-0.1773, 0.2784] | 0.2554 | +/+/+ | yes | 0.0421 | NONVIOLATING_SIGN_STABLE |
| 1.6475 | 0.7071 | 0.0445 | [-0.1959, 0.9010] | 0.4717 | +/+/+ | yes | 0.2289 | NONVIOLATING_SIGN_STABLE |
| 1.8750 | 0.8047 | 0.9081 | [-0.7426, 2.1026] | 1.1769 | +/+/- | no | -0.1356 | COMPATIBLE_SIGN_UNSTABLE |
| 2.1025 | 0.9024 | 1.4662 | [-1.3295, 3.9935] | 2.5013 | +/+/- | no | -0.0636 | COMPATIBLE_SIGN_UNSTABLE |
| 2.3300 | 1.0000 | 2.1225 | [-1.9217, 6.4719] | 4.5595 | +/+/- | no | 0.0079 | COMPATIBLE_SIGN_UNSTABLE |

This table also makes the main weakness visible. The non-violation decisions are not
equivalent to a strong likelihood preference: several envelopes are broad, and
four of the nine SN+BAO points are sign-unstable. The table supports the narrow
claim that the locked K2 response does not violate the current diagnostic gate;
it does not support a direct measurement claim.

## 9. Toward A Measurement Gate

The present result should be read as diagnostic compatibility only. A
measurement gate would require the locked finite-memory projection hypothesis
to be tested without changing the K2 window after inspection of the benchmark.
The required next layer is a covariance-aware benchmark in which the locked
prediction is compared against explicit null comparators, including no-memory,
smooth-reconstruction, optical-propagation, and backreaction-only controls.

The repository now includes a minimal gate-engine scaffold for this purpose.
Its current output regenerates the SN+BAO diagnostic status from the public
point-level packet and reports first null comparators under a diagonal
covariance proxy. This is a reproducibility harness only: the null-comparison
rows are not a public likelihood result, and they should not be read as
measurement validation.

The same scaffold also includes a first coordinate-robustness runner. It keeps
the frozen K1 baseline fixed and changes only the finite-memory depth mapping.
This is an audit of coordinate sensitivity, not a refit.

An initial coordinate-robustness audit shows that the redshift-normalized,
optical-depth-like, and likelihood-native index mappings remain non-violating
under the current diagnostic gate. A flat-LCDM $\chi(z)$-normalized
operator-only remapping produces an envelope-tension warning. This does not by
itself constitute likelihood-level rejection, but it marks coordinate-native
reconstruction and covariance-aware scoring as required Phase II checks.

The row-level diagnosis indicates that the warning is driven by upper-envelope
excess at several mid-depth points, not by a sign-stable contradiction. A
bounded $\rho \leq 4$ scan shows that the $\chi$-normalized operator-only
mapping has non-violating points inside the paper's locked $\rho$ range. The
appropriate interpretation is therefore a coordinate-robustness warning that
requires a coordinate-native baseline and covariance-aware benchmark, not a
post-hoc change of kernel.

The first null-model benchmark also remains deliberately conservative. The
fixed $\rho=4$ K2 prediction is non-violating on most tested coordinate
mappings, and the bounded $\rho\in[3,4]$ grid is non-violating across the
current mapping set. However, a frozen no-memory K1 proxy scores better under
the current diagonal-proxy AIC/BIC summary. This is a weakening signal for the
present distilled packet and reinforces the need for a public covariance-aware
benchmark before any measurement-level interpretation.

A follow-up null-dominance audit decomposes this weakening signal. The current
packet indicates that the no-memory K1 proxy remains stronger than fixed K2
under diagonal scoring and simple validation splits, while correlated
covariance proxies reduce the K1 advantage. This means the present packet does
not yet isolate a distinct finite-memory contribution, but it also shows why a
full covariance-aware benchmark is the correct next test rather than a
post-hoc change to the K2 kernel.

The repository now includes a Phase II public-benchmark preflight manifest.
Candidate DESI BAO and Pantheon+SH0ES input files have been downloaded and
shape-validated for preflight use. This removes the first data-availability
blocker, but it does not promote the present result to measurement validation:
the raw public-observable preflight table still marks these inputs as not yet
K2 diagnostic vectors. The finite-memory diagnostic transform,
coordinate-native mapping, and public covariance-aware benchmark remain
required before stronger empirical language would be justified.

A separate diagnostic-transform contract now makes this boundary machine
readable. The repository now also contains a BAO log-residual preflight
transform with propagated covariance, but no registered transform is currently
allowed for measurement-gate scoring because the residual baseline is
audit-fiducial rather than likelihood-native. A first residual null benchmark
has been run and prefers a simple constant-offset control under this audit
baseline. This is a preflight warning about baseline choice, not a
finite-memory measurement result.

The offset diagnosis maps this constant residual mode to an approximately
1.5 percent BAO scale shift under the audit baseline. Absorbed into the audit
sound-horizon parameter, this would move `rd=147.0 Mpc` to roughly `rd=144.8
Mpc`. This is treated as a baseline-calibration warning, not as evidence for
the finite-memory projection hypothesis.

A BAO baseline export readiness check therefore keeps the measurement gate
closed. The current audit baseline is useful for residual-transform plumbing,
but it is not likelihood-native or coordinate-native and is not eligible for K2
scoring.

A same-data `rd` offset sensitivity check confirms that this residual layer is
baseline-scale dominated: absorbing the measured offset into `rd` lowers the
zero-residual score to the constant-offset benchmark level. Because that
calibration uses the tested BAO vector itself, it is retained only as a
sensitivity diagnostic and not as a measurement-gate baseline.

The source-readiness check reaches the same conservative conclusion from the
other side: public DESI mean/covariance files are available, but they do not by
themselves define a likelihood-native baseline prediction. A future BAO
measurement gate therefore requires either a public best-fit/chain export or a
reproducible model-evaluation export with frozen parameters.

An official DESI DR2 `iminuit/base/desi-bao-all` best-fit file has been ingested
as a public baseline-export preflight. The local evaluator recomputes a BAO
chi-square close to the reported DESI value, which validates the baseline
plumbing. This still remains a preflight check rather than a K2 measurement
test, because the best-fit baseline is optimized on the same BAO data vector.

A CMB-only public best-fit baseline has also been exported. It is more
independent of the DESI BAO data vector, but its predicted BAO chi-square is
higher than the same-data DESI best-fit baseline. The resulting scorecard helps
separate baseline independence from BAO fit quality before any locked
finite-memory comparison is attempted.

Before running any K2 score, the repository now registers a BAO baseline
selection policy and a K2 protocol readiness gate. The current readiness state
is intentionally false: the protocol records the required baseline bracket,
null comparators, shared covariance rule, and locked `p=3`, `rho<=4` policy,
but does not yet authorize measurement-gate scoring.

The immediate remaining blocker is the BAO K1 response. Several controls are
now available, but no locked no-memory response target is allowed for K2
scoring. Without that amplitude-normalized target, a K2 score would risk being
defined by the residual representation rather than by a predeclared finite
memory response.

The locked-response plan now makes this missing object explicit. A CMB-only
unit-covariance-norm candidate is listed, but it is not selected and lacks a
null scorecard. The BAO branch therefore remains a preflight benchmark rather
than a measurement gate.

That candidate has now been normalized and compared against simple nulls. The
zero-response null is AIC-preferred, so the candidate is not selected as the
locked BAO K1 response target. This is a weakening preflight result and keeps
the BAO measurement gate closed.

The BAO branch is therefore recorded as a preflight/control branch rather than
the next primary measurement route. Its value is that it shows the gate refusing
to score K2 when the locked K1 response target is not yet competitive with fair
nulls. The next empirical branch should focus on SN+BAO/source-split or another
coordinate-native benchmark where the no-memory target can be frozen before the
finite-memory multiplier is evaluated.

The source-split readiness check has now been registered as the next branch.
Public SN and BAO inputs are available, and the current distilled packet already
contains sign-family information. The scoring gate remains closed, however,
because the coordinate-native K1/no-memory target has not yet been exported.
This keeps the pivot conservative: the next step is a public source-split
diagnostic transform, not immediate K2 scoring.

A source-split transform contract now records that boundary explicitly. The
current distilled packet is usable as a sign-stability template, and the BAO
path is usable as an anchor/control, but the public joint SN+BAO diagnostic
vector, covariance propagation, and coordinate-native K1 target remain upstream
requirements.

As a first transform-development step, the Pantheon+SH0ES SN product has been
converted into an audit residual preflight and binned onto the current
diagnostic redshift grid where data are available. The centered residual uses a
same-sample nuisance offset, so it is not a K1 target and not a measurement
score. Its role is only to prepare the future source-split diagnostic vector.

The next preflight layer aligns this binned SN residual with nearest DESI BAO
residual anchors on the current diagnostic grid. Eight of the nine grid points
have both an SN bin and a BAO anchor. This is still not a K2 score, because the
SN and BAO residuals are in different units and no joint covariance or
coordinate-native K1 target has been exported.

A standardized preflight then divides each branch residual by its own diagonal
uncertainty estimate. This gives a common audit scale but not a final physical
response variable. In this standardized table, five of the eight rows with both
SN and BAO information have opposite branch signs. This is best read as a
source-split warning and a guide for the next transform, not as evidence for or
against the locked finite-memory multiplier.

The row-level sign-tension diagnosis sharpens this warning. Among rows that are
sign-stable in the current distilled packet and have both public branches
available, four of five show opposite standardized SN/BAO signs. This suggests
that source splitting is not merely a formatting choice: the two branches can
pull in different directions under the present preflight transform. Because the
table still uses diagonal standardization and no coordinate-native K1 target,
this remains transform-development evidence only.

A simple covariance-proxy sensitivity check varies the assumed within-row
SN-BAO correlation. The opposite-sign counts remain unchanged across the tested
proxy range, while the contrast magnitudes change as expected. This reinforces
the need for a public joint covariance, but it does not turn the source-split
warning into a finite-memory measurement.

Finally, a source-split K1 target registry records the baseline side of the
same problem. Several useful controls exist, including the current distilled
K1, an SN-only residual, a BAO-only CMB candidate, and a standardized
zero-response control. None is selected as the coordinate-native K1 target for
K2 scoring. The next required object is a public source-split K1/no-memory
target with joint covariance and sign-family export.

A matching source-split covariance registry records the statistical side of
the same boundary. The diagonal standardized and within-row correlation
covariances are kept as preflight controls only. No covariance candidate is
authorized for K2 scoring until the joint source-split target and K1 baseline
are defined in the same coordinate-native space.

The sign-family export is tracked separately. The current distilled packet and
standardized source-split branch-sign audit are useful templates, but neither
is a public reconstruction-family export. A K2 measurement gate would require
public source-split reconstruction families and a frozen sign-stability rule in
the same coordinate-native target space.

A compact source-split dashboard now aggregates these gates. It keeps the
input and null-comparator side open, but closes the transform, K1, joint
covariance, and sign-family gates. This makes the status of the source-split
branch explicit: technically active as a preflight program, but not yet
authorized for K2 scoring.

An ordered export queue then turns the closed gates into a concrete work plan.
The coordinate-native source-split target export has now been completed as a
preflight artifact. It defines a standardized `SN - BAO` branch contrast on a
declared chi-normalized audit coordinate. This is not a no-memory baseline and
does not authorize K2 scoring. The next required object is the coordinate-native
K1/no-memory target, with public sign-family export and joint covariance still
downstream gates.

The coordinate-native K1/no-memory control has also been exported as zero
standardized SN-minus-BAO branch contrast. This is a conservative no-memory
control, not an amplitude fit and not a K2 scoring result. The measurement gate
therefore still remains closed until joint covariance and public sign-family
exports are declared on the same target rows.

A coordinate-native shrinkage covariance policy has also been exported on the
same usable rows. The matrix is positive definite and K1-compatible, but it is
still a declared covariance policy rather than a public full covariance. The
source-split scorecard therefore remains closed until the public sign-family
export is declared.

A public branch sign-family preflight has now been exported as well. It uses
the public SN and BAO standardized branch signs on the same coordinate-native
rows, and it preserves the observed branch-sign tension. It is not a full
public reconstruction-family export, so it still does not authorize a K2/null
scorecard.

Finally, a reconstruction-family upgrade contract records the remaining gap.
The target rows and warning policy are available, but public reconstruction
family responses and a family-level sign-stability rule are still missing. This
keeps the branch-sign preflight from being treated as scoring-grade evidence.

A follow-up source-readiness registry makes this boundary explicit. The current
distilled packet remains a template, and the public branch-sign preflight
remains a warning preflight. The public source-split reconstruction-family
response table now exists with a declared family-level sign-stability rule on
the same coordinate-native rows. K2 scoring nevertheless remains closed until
the remaining transform, K1, covariance, and sign-family gates are resolved.

The repository also freezes the required response-table schema. The expected
candidate is a long-format public reconstruction-family export with at least
two families, every usable coordinate-native target row covered by every
family, finite response values, positive response sigmas, valid response signs,
and no fitting inside this note. The current validator reports
that the candidate export is available and clean, so the export blocker is
resolved. This remains input readiness rather than a K2 result.

A candidate-family plan identifies the first practical public-input branches:
the Pantheon+ SN residual branch and the DESI DR2 BAO residual branch. These
branches are not promoted to K2 inputs in the present note. They are only the
first candidates to be exported into the frozen reconstruction-family response
schema. Backreaction-envelope and optical-propagation controls remain registered
as later fair-null sources.

A non-scoring response preview maps the current SN and BAO branch residuals
into that frozen schema. The preview is schema-valid and contains two families
across the eight usable target rows, but it remains outside the measurement
gate: the family-level scoring rule is not locked, the covariance policy has
not been promoted, and the preview is not the candidate export path.

A row-level family sign-rule preview then applies the conservative rule:
stable if all nonzero public reconstruction-family signs agree. Under the
current preview, three rows are stable and five remain warnings. These warning
rows are not hidden support and not hidden rejection; they simply show that the
public SN and BAO branch responses disagree in sign on most preview rows.

A promotion-readiness check prevents this preview rule from being used as a
scoring rule prematurely. It records that the preview rule exists and that
warning rows are retained. With the real reconstruction-family candidate export
present and valid, the rule-promotion check is now authorized, but warning rows
remain warning rows.

A final K2 scoring authorization guard then aggregates the required gates. In
the current repository state it returns `AuthorizationDecision = BLOCKED`. This
is deliberate: the preview artifacts are allowed to document schema plumbing
and warning policy, but they are not allowed to become a K2/null scorecard.

A candidate-export handoff manifest now records the exact remaining data object
and validation order. The candidate file is now present at
`data/reconstruction_families/source_split_reconstruction_family_responses.csv`.
It contains the public SN and BAO residual branches in the frozen long-format
schema and validates cleanly.

A candidate-path guard adds a practical safety check: the real candidate file is
present and distinct from the non-scoring preview. A future file that merely
copies the non-scoring preview would still be blocked rather than promoted.

A blocker matrix finally aggregates the dashboard, handoff, and authorization
guards. In the current state the candidate-export blocker is resolved, but K2
scoring remains blocked by the remaining transform, K1, covariance, and
sign-family gates. This is operational audit information, not a cosmological
result.

The first subtask under that blocker is now explicit: the SN residual branch
handoff maps all eight usable coordinate-native rows into the required
source-split standardized response scale. These rows remain provenance handoff
rows and have now also been written to the real candidate export.

The BAO residual branch handoff now mirrors this state. It maps all eight
usable coordinate-native rows into the same source-split standardized response
scale, and those rows have also been written to the real candidate export. K2
scoring remains closed because the final authorization guard is still blocked
by the remaining upstream gates.

After the gate synchronization, the source-split K2/null preflight scorecard is
authorized and runnable. The result is a weakening diagnostic result rather
than a measurement result: because the current source-split K1 target is a
zero-contrast no-memory response, the locked multiplicative K2 response is also
zero for every allowed rho. Thus K2 is not distinguishable from the no-memory
control on this target. In the current preflight scorecard, the locked K2 rho=4
row has three sign-stable violations, while a degree-2 polynomial diagnostic
control has the best AIC. This does not close the finite-memory projection
hypothesis, but it shows that this particular source-split target does not yet
provide distinct K2 evidence.

A follow-up K1 degeneracy audit confirms the mechanism row by row. All eight
usable source-split rows have zero K1 response, all eight therefore have
K2=K1 under the locked multiplicative operator, and no row has finite-memory
leverage. The next source-split benchmark must therefore define an externally
derived nonzero K1 response target, or move to a likelihood-native target, before
it can test K2 as a distinct response.

An additional K1 candidate sensitivity audit checks whether mechanically
available nonzero candidates from the validated reconstruction-family export
change that conclusion. The family common-mode mean is nonzero on all usable
rows, but its locked K2 response worsens under the present preflight scorecard.
The best AIC sensitivity model is the SN branch used directly as K1, but that
single-branch control is not an allowed primary source-split no-memory target.
Thus the issue is not merely that K1 must be nonzero. It must be nonzero and
externally interpretable before K2 can be treated as a distinct response.

A K1 candidate promotion gate makes this restriction explicit. It promotes no
candidate to primary K1: the zero-contrast target remains a fair null but is
degenerate for multiplicative K2; the common-mode mean lacks predeclared
external provenance; and the single-branch responses remain diagnostic
controls. This prevents a score-based K1 rescue and keeps the source-split
branch in weakening/preflight status until an externally derived nonzero K1 or
a likelihood-native K1 target exists.

The next required object is now encoded as a separate export contract. The
external K1 schema requires a row-aligned, nonzero, predeclared source-split K1
response with public provenance, joint-covariance compatibility, and no
same-data amplitude fit. The current validator reports this object as missing,
so no stronger source-split measurement-gate statement is made here.

A source registry now records the acceptable routes for that object. The
cleanest route is a likelihood-native joint SN+BAO no-memory baseline with
frozen parameters and covariance. A reconstruction-family mean could also be
considered, but only if the mean and amplitude policy are declared before K2
scoring. Single-branch controls and same-data amplitude rescue paths remain
blocked.

The reconstruction-family mean route has therefore been isolated as a future
policy rather than used retroactively. The equal-weight signed mean of the SN
and BAO branch responses is nonzero on all usable rows, but no family-mean
policy was frozen before the current K2/null scorecard. It remains a possible
future predeclared K1 route, not a current measurement-gate result.

A future rerun protocol now freezes that boundary. No current rerun is
authorized. The preferred future route is a likelihood-native joint SN+BAO K1
baseline; the secondary route is a family-mean K1 only if its policy is frozen
before a new scorecard. Any K1 generated from the current K2 residuals, or any
comparison requiring `rho>4` or a kernel change, is explicitly outside the
measurement-gate protocol.

The secondary route has been materialized as a future-only export. The
equal-weight family-mean K1 file is nonzero on all eight usable rows, but it is
marked as not allowed for the current rerun and not allowed as current primary
K1. The validator therefore reports the object as available but blocked by
`not_marked_primary_candidate`. This is intentional: it prepares the next
clean rerun without changing the interpretation of the present scorecard.

A future-only dry run then tests whether this secondary route is promising.
Under the same preflight covariance, the family-mean K1 has lower AIC than its
locked K2 rho=4 response, and the K2 multiplier worsens the score by
approximately 27.49 AIC units relative to the K1 family mean. This is not a
current measurement result, but it weakens the family-mean route as the next
primary path and reinforces the likelihood-native K1 baseline as the cleaner
target.

The likelihood-native K1 route is now reduced to an artifact checklist rather
than left as an abstract phrase. Public SN and BAO inputs are available, and
the joint specification, frozen parameter source, preflight baseline vector,
and preflight coordinate map have now been written. The remaining blockers are
promotion-level issues: SN nuisance handling, joint covariance, the
likelihood-native K1 export, and null scores on the same vector.

That specification is now written. It fixes the intended public inputs, joint
vector, baseline parameter source, coordinate-map requirement, covariance
policy, K1 export rule, null comparators, and locked K2 rule. The readiness
state therefore moves to the next blocker: a frozen no-memory baseline
parameter source.

That parameter source is now available as a CMB-only public best-fit preflight
artifact. This is deliberately weaker than a K1 export: it freezes the
no-memory parameters, but it does not by itself create a K1 response or a
measurement gate. The next implementation step was therefore to evaluate the
baseline vector and coordinate map before any new locked K2/null comparison is
attempted.

The preflight baseline vector and coordinate map have now been generated. The
vector is useful because it is derived from a frozen external parameter source
rather than from the K2 residuals, but it remains below measurement-gate
quality: the SN nuisance treatment, joint covariance, and K1 export rule are
not yet promoted. Thus the result narrows the implementation blocker without
turning the method note into a measurement-validation claim.

A promotion gate now makes this boundary machine-readable. It finds that no
promotion check is currently clean: the baseline vector, coordinate map,
covariance policy, null scorecard, and external K1 export all remain blockers.
The appropriate interpretation is therefore procedural readiness progress, not
new empirical support for the finite-memory projection hypothesis.

The first promotion policy fixes the nuisance convention: the raw source-split
response is the only candidate for primary K1 promotion, while the same-sample
centered response is retained as a diagnostic control. This prevents an
implicit offset fit from becoming the baseline amplitude used against the
locked finite-memory operator.

The second policy fixes the coordinate convention for the next benchmark
candidate: the frozen CMB-chi coordinate is the declared depth map, while the
earlier coordinate-robustness controls remain part of the benchmark record.
This narrows the coordinate ambiguity without treating a coordinate choice as a
new empirical result.

The covariance policy then fixes the statistical boundary for a future
preflight scorecard. A shrinkage covariance can be used as a declared benchmark
covariance for K1, locked K2, and null comparators, but it remains below the
standard required for a public full-covariance measurement-validation claim.

The first likelihood-native preflight scorecard has now been generated under
that boundary. It is informative but not validating: the locked K2 response
improves over the K1/no-memory baseline on the promoted vector, yet simple
polynomial controls remain far stronger under the current proxy information
criteria. The result therefore supports continued benchmark development rather
than a measurement claim.

The scorecard diagnosis indicates that the limiting issue is not merely sign or
coordinate choice, but amplitude scale. Low-depth source-split rows have target
responses far larger than the locked K2 prediction, so the diagonal proxy score
is dominated by a few large amplitude residuals. This is a clear next benchmark
problem, but it must not be solved by post-hoc rescaling of K1.

A bounded-rho audit confirms this boundary. The best allowed value is already
the passive upper endpoint, `rho=4`, and exact row-level amplitude matching
would require `rho>4` in every row. The current result therefore weakens an
amplitude-level interpretation of the locked operator on this branch while
preserving the finite-memory claim discipline.

A scale/covariance sensitivity check gives a more nuanced picture. K2 improves
over K1/no-memory under all tested proxy covariance cases, but it beats the
flexible polynomial controls only when a strong target-fraction error floor is
introduced. The current branch therefore points to a response-scale and
covariance-definition problem rather than to an immediate measurement result.

A finer error-floor sweep makes this dependence explicit: in the current
preflight vector, locked `rho=4` first becomes AIC-competitive with the
polynomial controls at a target-fraction floor of about 0.14. This should be
read as a scale-diagnostic threshold, not as a fitted uncertainty model. A
future benchmark would have to justify such an error floor independently from
public covariance, systematic-error, or cross-branch scatter information.
The repository therefore treats the 0.14 value as a policy threshold rather
than as an adopted covariance: branch scatter is a useful preflight clue, but
stronger interpretation remains blocked until that scale is justified by an
independent benchmark route.

A branch-scatter preflight benchmark then applies this clue directly. Using
the public SN/BAO branch split as a row-level covariance scale, the locked K2
response becomes the best AIC model across all tested branch-scatter covariance
variants, including diagonal, quadrature, max-scale, nearest-neighbor, and
constant-correlation variants. This strengthens the K2 route conditionally, but
it remains below measurement-validation level because branch scatter is not yet
a public full-covariance likelihood.

A promotion gate records the same boundary mechanically. The branch-scatter
route is now eligible as a declared preflight benchmark, because the rows are
available, both branches are present, the scatter exceeds the K2 threshold, and
K2 is best under the tested scatter variants. It is not eligible as measurement
validation because the scatter model is not public full covariance and no
independent systematic or covariance source has yet been registered.

The covariance-source registry makes the remaining blocker more concrete. Raw
public covariance inputs are available for the SN and BAO products, while a
joint covariance propagated into the likelihood-native source-split vector is
not yet available. Thus the current K2 strengthening is best described as a
declared preflight-benchmark result. A stronger measurement-gate statement
requires the propagated public covariance, an independent systematic floor, or
a frozen reconstruction-family scatter rule.

The first propagated public covariance proxy has now been run. It uses the raw
Pantheon+ and DESI covariance inputs and maps them into the same source-split
diagnostic vector under a zero SN-BAO cross-covariance assumption. Under this
proxy, K2 still improves over K1/no-memory, but it does not beat the flexible
polynomial controls. This keeps the conclusion split: branch scatter gives a
stronger conditional K2 result, while the public covariance proxy motivates a
full-likelihood covariance upgrade before any stronger empirical statement.

A cross-covariance sensitivity audit tests whether this mixed result is merely
an artifact of setting SN-BAO cross-covariance to zero. In the positive-definite
range of a row-aligned cross-covariance proxy, K2 continues to improve over
K1/no-memory but still does not beat the polynomial controls. Thus the public
covariance route remains weaker than the branch-scatter benchmark at the
current preflight level.

A route-level covariance scorecard makes this split explicit. Across the tested
covariance routes, K2 improves over K1/no-memory in every case, but it beats the
best polynomial control only on the branch-scatter and related preflight-scale
routes. The propagated public covariance proxy and its cross-covariance
sensitivity remain mixed. This is a useful strengthening of the preflight
diagnostic, but it is not measurement validation; the next requirement is a
full likelihood-native public covariance transform or an independently
registered systematic/scatter route.

A row-level covariance-gap audit then separates the failure modes. K2 improves
over K1/no-memory on every usable row under both the public-proxy and
branch-scatter diagonal decompositions. The remaining weakness is instead that
flexible polynomial controls remain very competitive under the public-proxy
route. The branch-scatter route becomes K2-supportive because the same flexible
controls are penalized on particular rows under that response-scale model. This
is a useful diagnostic of route dependence, not a reason to promote the result
to measurement validation.

A polynomial cross-validation audit tests that objection directly. Under the
public-proxy diagonal route, the quadratic polynomial control remains stronger
than K2 in leave-one-out validation, but K2 beats the polynomial controls in the
blocked split. Under branch-scatter and native-plus-branch-scatter routes, K2
beats the polynomial controls in both validation modes. Thus the polynomial
dominance is not stable across validation policies. This weakens the in-sample
polynomial objection, while still leaving the result below measurement
validation.

The resulting support ladder is therefore deliberately conservative. K2 is
supportive relative to K1/no-memory, mixed but conditionally supportive relative
to polynomial controls, strongest under the declared branch-scatter preflight
route, and still blocked at the measurement-validation level. The public
covariance proxy remains the main weakening route and the next technical
target.

The corresponding public-covariance upgrade queue records this as a concrete
blocker rather than a narrative caveat. A stronger benchmark requires a full
likelihood-native public covariance transform or a predeclared shrinkage/scatter
route, a registered SN-BAO cross-covariance policy, and a locked rerun protocol
declaring K1, K2, nulls, mapping, covariance, and thresholds before execution.

That locked rerun protocol is now explicit. The preferred future path is a full
likelihood-native public benchmark; a secondary branch-scatter path is allowed
only if registered in advance as an independent systematic or
reconstruction-family scatter route. Rescue paths are forbidden: no K1 generated
from current K2 residuals, no covariance or cross-covariance tuned after seeing
the scorecard, no coordinate remapping selected as a rescue, and no dropped null
comparators. Under the current readiness check, no stronger public-covariance
rerun is authorized.

A covariance-policy registry then classifies the possible covariance routes.
Only the row-aligned cross-covariance sensitivity policy is currently available,
and it is sensitivity-only. The full public likelihood-native covariance route,
registered shrinkage route, and registered branch-scatter route are not yet
available for stronger interpretation. This keeps the next step operational:
freeze a registered shrinkage policy or implement the full public covariance
transform before rerunning the scorecard.

The registered-shrinkage rerun template now freezes that possible next route at
the component level. Six of eight components are locked or available for
preflight, including the K2 operator, K1 source, coordinate mapping, null
comparators, validation modes, and acceptance rule. Two components remain
template-only: the shrinkage covariance parameters and the cross-covariance
policy. Until those are declared before execution, the registered-shrinkage
route is not executable.

Those two missing components have now been frozen as a future-preflight
parameter policy: `lambda=0.15`, an exponential distance kernel with
correlation length `0.25`, and `rho_SN_BAO=0` as the primary cross-covariance
choice, with cross-covariance sensitivity reported separately. This makes the
registered-shrinkage route structurally complete for a future preflight
decision, but it still does not authorize a current stronger rerun or a
measurement-validation claim.

An activation gate now records the precise boundary. The registered-shrinkage
route has no preflight-blocking checks left and can be activated for a future
preflight rerun, but measurement validation remains blocked. The remaining
measurement blockers are the unresolved K2-vs-polynomial issue at the
public-covariance level and the absence of a full public measurement route.
Therefore no current scorecard should be rerun as a stronger result.

The registered-shrinkage future-preflight scorecard was then run under this
boundary. It is informative but weakening: K2 improves over K1/no-memory, but
the quadratic polynomial control remains AIC-preferred under the registered
shrinkage covariance. This shows that the shrinkage route was not tuned into a
K2 win. The public-polynomial objection therefore remains active for the public
benchmark path.

A polynomial-control fairness audit clarifies the interpretation. The polynomial
controls are not treated as a physical null model or as an explanation of the
effect. They are mandatory overfit-risk controls. They cannot be dismissed,
because they are preregistered and remain competitive under some public-proxy
tests; but they also cannot be promoted to a standalone physical cosmology
claim. The correct status is therefore a measurement blocker, not a final
falsification.

A physical-null hierarchy then defines what must replace a merely generic
smooth-control comparison. The next benchmark must include not only K1/no-memory
and polynomial controls, but also physical nulls for backreaction and
optical-propagation effects. At present, only the no-memory physical baseline is
scoring-ready. Backreaction-only and Dyer-Roeder/optical controls now exist as
unit-norm templates on the same source-split vector, and their amplitude policy
is now declared for future preflight use. However, those amplitudes are sanity /
sensitivity policies rather than physical calibrations. This keeps the
measurement claim blocked for a second reason: the physical null layer is not
measurement-calibrated.

The registered amplitude policy is deliberately restrictive. Unit-norm physical
null templates may be used as sanity controls, and a bounded amplitude grid may
be reported as sensitivity analysis, but no best-amplitude physical null may be
selected after inspecting the finite-memory scorecard.

The first physical-null preflight scorecard is therefore informative but still
bounded. On the branch-scatter preflight scale, the locked K2 response is
stronger than K1/no-memory and the reported physical-null template controls.
This is a supportive preflight signal, not a measurement-validation result,
because the physical-null amplitudes are not independently calibrated.

The row-level decomposition narrows the interpretation. K2 improves over
K1/no-memory in all usable rows, but against the best reported physical-null
template the row split is even. The aggregate still slightly favors K2. Thus the
physical-null comparison is supportive at preflight level, but not yet decisive.

The remaining physical-null blocker is now operationally explicit. A
measurement-grade comparison would need either a public backreaction amplitude
or envelope on the same source-split vector, and a public optical
clumpiness/Dyer-Roeder amplitude with covariance. Choosing those amplitudes from
the same scorecard residuals is disallowed.

The repository therefore registers source classes rather than claiming a
calibrated physical-null comparison. Candidate routes include published
backreaction constraints, independent simulation priors, Dyer-Roeder
`alpha(z)`/clumpiness constraints, and optical lensing or opacity proxies. None
is currently ingested and mapped to the source-split vector.

The mapping rule for those future sources is also frozen: sources must be
projected to the existing source-split coordinate vector by monotone
interpolation in redshift or a declared source coordinate, without
extrapolation, and without smoothing selected from the K2 residuals.

The covariance rule is likewise frozen at policy level. A measurement-grade
physical-null comparison would require source-native uncertainty or covariance
propagated through that mapping. Diagonal or shrinkage proxies may be used only
as preflight sensitivity checks, and uncertainty widening after seeing the K2
ranking is forbidden.

The resulting physical-null dashboard has seven gates. Four are ready at
preflight level, while three remain open measurement blockers: source ingestion,
mapping execution, and covariance propagation. Its compact reading is therefore
`supportive_but_narrow`, not measurement validation.

The first acquisition inventory registers six public source candidates,
including recent backreaction constraints, the optical-versus-expansion
classification framework, Dyer-Roeder smoothness-parameter constraints, and
weak-lensing to smoothness-parameter mapping references. These are candidate
inputs only: none is ingested, digitized, covariance-ready, or mapped to the
source-split vector in the present note.

The first acquisition triage ranks the Koksbang backreaction constraints as the
top backreaction ingest target, followed by two Dyer-Roeder smoothness
constraint papers as optical ingest targets. The Heinesen-Clifton and
weak-lensing references remain method references unless source tables or
compatible amplitude constraints are identified.

The first source-package probe has now been run for those three acquisition
targets. It finds one data-like route in the Koksbang backreaction package and
TeX/table-marker routes in the two Dyer-Roeder packages. This is acquisition
progress only: no numerical physical-null values are extracted, mapped to the
source-split vector, or propagated through covariance in the present note.

The provisional extraction manifest then tightens that boundary. The apparent
Koksbang data-like route is package metadata rather than a source-native
numeric constraint table, so the backreaction branch remains a formula,
figure, or external-reconstruction route. The two Dyer-Roeder sources provide
provisional smoothness-parameter candidates, but these are still not benchmark
inputs until a source-split mapping and uncertainty model are attached.

The first mapping-readiness check identifies two joint Dyer-Roeder
smoothness-parameter rows with full coverage of the current source-split
redshift grid. This is useful acquisition progress, but it is not a scorecard
result: no row yet has an independently declared transformation from
smoothness parameter to source-split response, and no row has covariance
propagation into the benchmark vector. The mapping task queue therefore starts
with the joint optical `alpha` route while keeping the physical-null benchmark
gate closed.

The first optical transform contract has now been written in non-scoring form:
`response_i=(1-alpha)*unit_norm(centered[x^2])`. The amplitude is the
source-reported clumpiness contrast, not a fit to K2 residuals. It produces a
preview for the two full-coverage joint Dyer-Roeder rows, but those rows remain
outside measurement scoring until sign convention and covariance propagation are
registered.

The sign-convention audit reinforces that caution. The inverted optical sign
matches more total source-split rows, while the as-declared sign matches more
sign-stable rows. Since these two summaries point in different directions, the
paper does not choose an optical physical-null sign by performance. Any future
scorecard must freeze that sign from external optical-response reasoning before
the benchmark is evaluated.

The alpha uncertainty has also been propagated into non-scoring covariance
previews: a diagonal amplitude-propagation matrix and a fixed
exponential-in-depth correlation matrix. These matrices are useful plumbing
checks, but they are not source-native covariance and they do not open the
physical-null scorecard.

The consolidated alpha scoring guard therefore remains closed. Two alpha
candidates now have transform, sign-audit, and covariance-preview artifacts, but
zero candidates are authorized for physical-null scorecard use because the
optical sign is not externally frozen and source-native covariance is still
missing.

This measurement gate is therefore a future test protocol, not a new result in
the present note. Its role is to define what would have to happen before the
method-note compatibility result could become measurement-validation evidence:
the locked prediction must remain competitive under the same covariance
benchmark, the null comparators must be reported, and the falsification
criteria must remain frozen before the comparison.

## 10. Robustness And Falsification Criteria

The current evidence is deliberately weaker than a full likelihood. For that
reason, it is useful to state what would make the finite-memory diagnostic fail
or become substantially less interesting.

The diagnostic would fail in its present form if:

- the BAO-only envelope overlap disappeared under the same locked K2 window;
- sign-stable SN+BAO points required the opposite sign from the locked
  prediction;
- compatibility required $\rho > 4$ or a different kernel power chosen after
  seeing the envelope;
- the localized SN+BAO warning became sign-stable under a stronger
  reconstruction audit;
- a full covariance likelihood rejected the whole locked window rather than
  merely shifting the best point inside it.

Conversely, the diagnostic would become more interesting if the same locked
window survived a covariance-aware likelihood test, if independent
reconstructions selected a similar late-depth response shape, or if
backreaction-aware and optical-propagation tests separated in a way naturally
tracked by the K2 window.

These criteria are included to keep the method honest. The finite-memory
operator is useful only if it remains constrained. If it must be repeatedly
relaxed to follow each new diagnostic reconstruction, it loses the main
advantage of being predeclared.

## 11. Expected Significance

The main significance of the construction is not that it establishes a new
cosmological model. Its value is methodological:

- it gives a compact finite-memory operator whose amplitude is bounded before
  comparison with data;
- it interfaces naturally with FLRW consistency, optical-propagation, and
  backreaction tests;
- it demonstrates a way to handle sign-unstable reconstructed diagnostics
  without silently overclaiming;
- it provides a small public module that can be tested independently as a
  diagnostic proposal.

The near-term audience is likely narrow: researchers interested in
cosmological consistency tests, backreaction, light propagation, and
method-level modified-gravity phenomenology. The higher-impact route requires
a later full covariance or shrinkage-covariance likelihood comparison with
direct public likelihood products.

## 12. Limitations

This manuscript is a theory-method diagnostic note. It does not claim:

- a full covariance likelihood;
- a direct measurement claim;
- exclusion of cosmic backreaction;
- a complete derivation of cosmology from an underlying action;
- reconstruction of a full background theory.

The next stage is a paper-aligned likelihood comparison using covariance or
shrinkage-covariance products and direct published likelihood data where
available.

The most important limitation is that the public packet contains distilled
diagnostic summaries rather than the full reconstruction pipeline. This is
acceptable for a method note whose purpose is to define a bounded operator and
state claim boundaries, but it is not sufficient for an observational paper.
The current manuscript should therefore be read as a bridge from a compact
diagnostic construction to a public, testable effective module, while leaving
the stronger likelihood comparison for a later release.

## 13. Phase II Roadmap

The next technical step is to replace the diagonal/envelope diagnostic with a
likelihood-level comparison. At minimum, this requires public likelihood or
data products, a covariance or shrinkage-covariance prescription, and a frozen
mapping from the reconstructed observable to the finite-memory diagnostic
coordinate $x$.

A useful future workflow is:

```text
freeze K2 window -> ingest public likelihood products -> build covariance-aware
diagnostic -> compare locked window -> report posterior support or rejection
```

This future comparison should not widen the K2 window unless a new paper is
explicitly framed as a different model. The main value of the present note is
that it fixes a small target before the stronger test is performed.

The Phase II work package should therefore include:

- covariance-aware likelihood ingestion;
- null comparators for no-memory, smooth-response, optical-propagation, and
  backreaction-only alternatives;
- a public reconstruction benchmark;
- coordinate-mapping robustness across redshift-normalized, comoving-distance,
  optical-depth-like, and likelihood-native coordinates;
- direct comparison against BAO-only and SN+BAO reconstruction families;
- a frozen benchmark challenge in which the K2 window is locked before testing.

## 14. Conclusion

We have defined a finite-memory projection correction as a bounded diagnostic
operator rather than as a complete cosmological model. The locked cubic form
$W(x)=1+\rho x^3$ follows from a passive memory budget and a simple
shape-selection audit over power kernels. With $\rho \leq 4$, the operator gives
a compact K2 diagnostic window that can be compared against reconstructed
cosmological consistency envelopes without fitting the memory depth after the
fact.

Within the distilled diagnostic packet used here, the locked K2 window is
compatible with the BAO-only envelope and remains non-violating under the
reconstruction-aware SN+BAO sign-stability gate. The strict SN+BAO median-sign
warning is retained as a limitation rather than hidden: it marks a
reconstruction-sensitive point that should be revisited with direct likelihood
products.

The result is therefore a release-candidate method-note claim, not an
measurement-validation claim. Its next meaningful test is a covariance-aware
likelihood comparison against public likelihood data and predeclared null
comparators.

## 15. Data And Code Availability

This draft uses a distilled diagnostic packet rather than a direct public
likelihood product. The public repository contains the manuscript scaffold, the
current PDF renderer, and compact result tables used in this note. The current
diagnostic evidence files are:

- `evidence/result_summary.csv`;
- `evidence/claim_matrix.csv`;
- `evidence/diagnostic_point_audit.csv`;
- `evidence/source_packet_manifest.csv`;
- `evidence/coordinate_mapping_policy.csv`;
- `evidence/threshold_sensitivity.csv`;
- `evidence/threshold_kernel_outcomes.csv`;
- `evidence/open_problem_resolution_matrix.csv`.
- `docs/measurement_gate_plan.md`;
- `evidence/measurement_gate_matrix.csv`;
- `evidence/null_model_registry.csv`.
- `evidence/gate_results_current.csv`.
- `evidence/coordinate_robustness_results.csv`.
- `evidence/coordinate_tension_audit.csv`.
- `evidence/rho_coordinate_scan.csv`.
- `evidence/coordinate_mapping_geometry.csv`.
- `evidence/null_comparison_results.csv`.
- `evidence/model_scorecard.csv`.
- `evidence/null_dominance_audit.csv`.
- `evidence/null_dominance_summary.csv`.
- `evidence/subset_model_scorecard.csv`.
- `evidence/cross_validation_results.csv`.
- `evidence/shrinkage_covariance_sensitivity.csv`.
- `evidence/k1_baseline_provenance_audit.csv`.
- `evidence/public_benchmark_readiness.csv`.
- `docs/bao_branch_pivot_decision.md`.
- `evidence/bao_branch_decision_matrix.csv`.
- `docs/source_split_benchmark_plan.md`.
- `evidence/source_split_readiness.csv`.
- `docs/source_split_transform_contract.md`.
- `evidence/source_split_transform_registry.csv`.
- `evidence/source_split_transform_readiness.csv`.
- `docs/sn_residual_transform_preflight.md`.
- `evidence/sn_residual_preflight.csv`.
- `evidence/sn_residual_binned_preflight.csv`.
- `evidence/sn_residual_preflight_summary.csv`.
- `docs/source_split_joint_preflight.md`.
- `evidence/source_split_joint_preflight.csv`.
- `evidence/source_split_joint_preflight_summary.csv`.
- `docs/source_split_standardized_preflight.md`.
- `evidence/source_split_standardized_preflight.csv`.
- `evidence/source_split_standardized_preflight_summary.csv`.
- `evidence/source_split_sign_tension_audit.csv`.
- `evidence/source_split_sign_tension_summary.csv`.
- `evidence/source_split_covariance_sensitivity.csv`.
- `evidence/source_split_covariance_sensitivity_summary.csv`.
- `docs/source_split_k1_target_plan.md`.
- `evidence/source_split_k1_target_registry.csv`.
- `evidence/source_split_k1_target_readiness.csv`.
- `docs/source_split_covariance_plan.md`.
- `evidence/source_split_covariance_registry.csv`.
- `evidence/source_split_covariance_readiness.csv`.
- `docs/sign_family_export_plan.md`.
- `evidence/sign_family_export_registry.csv`.
- `evidence/sign_family_export_readiness.csv`.
- `evidence/source_split_gate_dashboard.csv`.
- `evidence/source_split_gate_dashboard_summary.csv`.
- `docs/source_split_export_task_queue.md`.
- `evidence/source_split_export_task_queue.csv`.
- `evidence/source_split_export_task_queue_summary.csv`.
- `docs/source_split_reconstruction_family_sources.md`.
- `evidence/source_split_reconstruction_family_source_registry.csv`.
- `evidence/source_split_reconstruction_family_source_readiness.csv`.
- `docs/source_split_reconstruction_family_export_schema.md`.
- `evidence/source_split_reconstruction_family_export_schema.csv`.
- `evidence/source_split_reconstruction_family_export_template.csv`.
- `evidence/source_split_reconstruction_family_export_validation.csv`.
- `docs/source_split_reconstruction_family_candidate_plan.md`.
- `evidence/source_split_reconstruction_family_candidate_plan.csv`.
- `evidence/source_split_reconstruction_family_candidate_summary.csv`.
- `docs/source_split_reconstruction_family_response_preview.md`.
- `evidence/source_split_reconstruction_family_response_preview.csv`.
- `evidence/source_split_reconstruction_family_response_preview_summary.csv`.
- `docs/source_split_family_sign_rule_preview.md`.
- `evidence/source_split_family_sign_rule_preview.csv`.
- `evidence/source_split_family_sign_rule_preview_summary.csv`.
- `docs/source_split_sign_rule_promotion_readiness.md`.
- `evidence/source_split_sign_rule_promotion_readiness.csv`.
- `docs/source_split_k2_scoring_authorization.md`.
- `evidence/source_split_k2_scoring_authorization.csv`.
- `docs/source_split_candidate_export_handoff.md`.
- `evidence/source_split_candidate_export_handoff_manifest.csv`.
- `evidence/source_split_candidate_export_handoff_summary.csv`.
- `docs/source_split_candidate_path_guard.md`.
- `evidence/source_split_candidate_path_guard.csv`.
- `docs/source_split_blocker_matrix.md`.
- `evidence/source_split_blocker_matrix.csv`.
- `evidence/source_split_blocker_matrix_summary.csv`.
- `docs/source_split_sn_branch_export_handoff.md`.
- `evidence/source_split_sn_branch_export_handoff.csv`.
- `evidence/source_split_sn_branch_export_handoff_summary.csv`.
- `docs/source_split_bao_branch_export_handoff.md`.
- `evidence/source_split_bao_branch_export_handoff.csv`.
- `evidence/source_split_bao_branch_export_handoff_summary.csv`.
- `docs/source_split_reconstruction_family_candidate_export.md`.
- `data/reconstruction_families/source_split_reconstruction_family_responses.csv`.
- `docs/source_split_k2_null_scorecard.md`.
- `evidence/source_split_k2_null_scorecard.csv`.
- `evidence/source_split_k2_null_scorecard_summary.csv`.
- `docs/source_split_k1_degeneracy_audit.md`.
- `evidence/source_split_k1_degeneracy_audit.csv`.
- `evidence/source_split_k1_degeneracy_summary.csv`.
- `evidence/source_split_k1_response_requirements.csv`.
- `docs/source_split_k1_candidate_sensitivity.md`.
- `evidence/source_split_k1_response_candidate_audit.csv`.
- `evidence/source_split_k1_response_candidate_summary.csv`.
- `evidence/source_split_k1_candidate_sensitivity.csv`.
- `evidence/source_split_k1_candidate_sensitivity_summary.csv`.

The PDF can be regenerated locally with:

```text
python3 -m pip install -r requirements.txt
python3 make_pdf.py
```

The underlying comparison should be treated as a reconstruction-level
diagnostic until direct likelihood products or covariance/shrinkage-covariance
inputs are added.

## References

[1] A. Heinesen and T. Clifton, "Observational Tests for Distinguishing Classes
of Cosmological Models", arXiv:2604.07244, 2026.
https://arxiv.org/abs/2604.07244

[2] S. M. Koksbang, "First observational constraints on cosmic backreaction
over an extended redshift range", arXiv:2604.11249, 2026.
https://arxiv.org/abs/2604.11249

[3] C. C. Dyer and R. C. Roeder, "The Distance-Redshift Relation for Universes
with No Intergalactic Medium", The Astrophysical Journal 174, L115-L117,
1972.

[4] C. C. Dyer and R. C. Roeder, "Distance-Redshift Relations for Universes
with Some Intergalactic Medium", The Astrophysical Journal 180, L31-L34,
1973.
