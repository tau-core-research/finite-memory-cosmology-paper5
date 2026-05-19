# Measurement Gate Audit Log

This document preserves the detailed implementation/audit log that was compressed out of the main Paper 5 draft for readability. It is repository documentation, not the main manuscript narrative.

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

