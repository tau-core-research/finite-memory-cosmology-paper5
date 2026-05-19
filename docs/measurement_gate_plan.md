# Finite-Memory Measurement Gate Plan

Status: protocol layer for a diagnostic method note.

This document defines the first measurement-gate path for the finite-memory
projection hypothesis. It does not upgrade the current manuscript claim. The
current paper remains a bounded diagnostic method note.

## Current Status

The current repository contains:

- a locked prediction shape, `W(x)=1+rho*x^3`;
- a passive amplitude bound, `rho <= 4`;
- a current diagnostic packet in `evidence/diagnostic_point_audit.csv`;
- a minimal gate runner in `scripts/run_gate_current_packet.py`;
- a coordinate robustness runner in `scripts/run_coordinate_robustness.py`;
- registered null comparators in `evidence/null_model_registry.csv`.

The present result is diagnostic compatibility. It is not measurement
validation and not a full covariance-aware benchmark.

## Why This Is Not Measurement Validation

The current packet is useful because it makes the diagnostic claim
reproducible. It is still limited because:

- the score uses a diagonal covariance proxy from the public envelope columns;
- the coordinate mapping is still the current redshift-normalized diagnostic
  mapping;
- the null comparators are MVP controls, not full physical alternatives;
- the current packet is a distilled diagnostic product rather than a direct
  public likelihood ingestion.

For that reason, the present gate can report non-violation or tension. It
cannot establish a measurement-level validation claim.

## Locked Prediction

The benchmark prediction must be locked before comparison:

```text
W(x) = 1 + rho*x^3
rho <= 4
K2(x) = W(x) * K1(x)
```

The comparison must not tune `rho`, change the kernel power, or redefine the
coordinate mapping after inspecting benchmark residuals.

## Required Data And Statistics

A stronger measurement gate requires:

- public reconstruction points or likelihood products;
- a covariance matrix or declared shrinkage-covariance prescription;
- a frozen coordinate mapping such as redshift-normalized, comoving-distance,
  optical-depth-like, or likelihood-native depth;
- a public implementation of the locked prediction;
- a documented null comparator registry;
- point-level residuals, chi2, AIC/BIC, and falsification flags reported for
  the locked prediction and null comparators under the same benchmark.

## Null Comparators

The minimum comparator families are:

- `LCDM_NO_MEMORY`;
- `GENERIC_POLYNOMIAL_SMOOTHING`;
- `BACKREACTION_ONLY`;
- `DYER_ROEDER_OPTICAL`;
- `RECONSTRUCTION_ARTIFACT`;
- `SIGN_RANDOMIZED_CONTROL`;
- `COORDINATE_REMAP_CONTROL`.

The MVP runner currently implements the first no-memory proxy and simple
polynomial smoothing controls. The remaining comparators are registered for
the next benchmark layer.

## Gate Matrix

The gate program is organized as:

- `G1_BAO_MEMORY_WINDOW`;
- `G2_SN_BAO_SIGN_STABILITY`;
- `G3_COORDINATE_ROBUSTNESS`;
- `G4_COVARIANCE_LIKELIHOOD`;
- `G5_CROSS_BRANCH_PATTERN`.

## Outcome Classes

Supportive outcome:

- the locked prediction remains non-violating under the same frozen gate;
- null comparators are reported under the same covariance-aware benchmark;
- the result is stable across predeclared coordinate mappings;
- no falsification criterion is triggered.

Weakening outcome:

- compatibility holds only under the diagonal proxy;
- the result is sensitive to coordinate mapping;
- a null comparator matches or improves the score with fewer assumptions;
- the locked prediction remains non-violating but not competitive.

Strong negative outcome:

- the locked prediction requires `rho > 4`;
- the kernel or coordinate mapping must be changed after inspection;
- sign-stable points contradict the locked prediction;
- a covariance-aware benchmark rejects the locked prediction;
- the effect appears only as a reconstruction artifact.

## Current MVP Harness

Run:

```text
python3 scripts/run_gate_current_packet.py
```

It reads:

```text
evidence/diagnostic_point_audit.csv
frozen/k1_baseline_v1.csv
```

and writes:

```text
evidence/gate_results_current.csv
```

The current score uses `covariance_status = diagonal_proxy_from_p16_p84`.
This is intentionally weaker than a covariance-aware benchmark. Its role is to
make the present diagnostic claim reproducible from code before public
likelihood products are ingested.

The first coordinate robustness harness is:

```text
python3 scripts/run_coordinate_robustness.py
```

It writes:

```text
evidence/coordinate_robustness_results.csv
```

This check changes the finite-memory depth coordinate while keeping the frozen
K1 baseline fixed. It is a robustness audit, not a new fit.

## Current Coordinate Warning Diagnosis

The first G3 run found a warning in the flat-LCDM `chi`-normalized mapping
under operator-only remapping. The follow-up diagnosis separates this warning
into three evidence products:

- `evidence/coordinate_tension_audit.csv`;
- `evidence/rho_coordinate_scan.csv`;
- `evidence/coordinate_mapping_geometry.csv`.

Current interpretation:

- the warning is primarily upper-envelope excess at mid-depth points;
- no sign-stable contradiction is triggered in the row-level diagnosis;
- the bounded `rho <= 4` scan finds non-violating chi-mapping points inside
  the paper's locked `rho` range;
- the result is a coordinate robustness warning, not a final falsification.

## Current Null-Model Benchmark MVP

The first null-model benchmark is:

```text
python3 scripts/run_null_comparison.py
python3 scripts/build_model_scorecard.py
```

It writes:

```text
evidence/null_comparison_results.csv
evidence/model_scorecard.csv
```

Current interpretation:

- fixed `K2_LOCKED_RHO4` is non-violating on four of five coordinate mappings;
- `K2_LOCKED_GRID_WITHIN_3_4` is non-violating on all five mappings, but is
  counted as a one-parameter bounded grid result;
- the frozen `K1_NO_MEMORY` proxy has stronger diagonal-proxy AIC/BIC in the
  current distilled packet;
- this is a weakening benchmark signal, not a final rejection.

The next required step is a covariance-aware public benchmark. The current
diagonal proxy is useful for reproducibility, but it is not sufficient for a
measurement-validation claim.

## Current Source-Split Preflight Target

The first source-split export task is now completed as a preflight artifact:

```text
python3 scripts/build_source_split_coordinate_native_target.py
```

It writes:

```text
evidence/source_split_coordinate_native_target.csv
evidence/source_split_coordinate_native_target_summary.csv
```

The target uses `x_chi_normalized_flat_lcdm_audit` and the standardized branch
contrast:

```text
SourceSplitResponse = SN_standardized - BAO_standardized
```

This is not a K1/no-memory baseline and it is not a K2 score. It only moves
the source-split branch into a declared coordinate-native preflight target
space.

The coordinate-native K1/no-memory control is now also exported:

```text
python3 scripts/build_source_split_k1_coordinate_native_target.py
```

It writes:

```text
evidence/source_split_k1_coordinate_native_target.csv
evidence/source_split_k1_coordinate_native_target_summary.csv
```

The current control is zero standardized SN-minus-BAO branch contrast. It is
not an amplitude fit and it is not authorized for K2 scoring. The remaining
source-split blockers are joint covariance and public sign-family export.

The source-split shrinkage covariance policy is now exported:

```text
python3 scripts/build_source_split_joint_covariance_policy.py
```

It writes:

```text
evidence/source_split_joint_covariance_policy.csv
evidence/source_split_joint_covariance_policy_summary.csv
```

The policy is positive definite on the eight usable coordinate-native rows. It
is not a public full covariance and it is not authorized for K2 scoring while
the public sign-family export is missing.

The source-split branch sign-family preflight is now exported:

```text
python3 scripts/build_source_split_public_sign_family.py
```

It writes:

```text
evidence/source_split_public_sign_family.csv
evidence/source_split_public_sign_family_summary.csv
```

The export uses public SN and BAO standardized branch signs on the same
coordinate-native rows. It is not a full public reconstruction-family export,
so the K2/null scorecard remains closed.

The reconstruction-family upgrade contract is:

```text
python3 scripts/build_source_split_reconstruction_family_upgrade.py
```

It writes:

```text
evidence/source_split_reconstruction_family_upgrade_contract.csv
evidence/source_split_reconstruction_family_upgrade_summary.csv
```

This contract keeps the branch-sign preflight from being overinterpreted. It
requires public reconstruction-family responses and a family-level sign-stable
rule before K2/null scoring can be considered.

The reconstruction-family source readiness check is:

```text
python3 scripts/check_source_split_reconstruction_family_sources.py
```

It writes:

```text
evidence/source_split_reconstruction_family_source_readiness.csv
```

The current registry separates four cases: the distilled method-note template,
the public branch-sign preflight, the missing public source-split
reconstruction-family export, and the later likelihood-native target. None is
allowed for K2 scoring. The useful new output is operational only: it shows
that branch signs are row-aligned and public, but still lack exported
reconstruction-family responses and a family-level sign-stability rule.

The exact schema for that missing export is now frozen:

```text
python3 scripts/build_source_split_reconstruction_family_export_schema.py
python3 scripts/validate_source_split_reconstruction_family_export.py
```

Current outputs:

```text
evidence/source_split_reconstruction_family_export_schema.csv
evidence/source_split_reconstruction_family_export_template.csv
evidence/source_split_reconstruction_family_export_validation.csv
```

The validation state is now clean for the real candidate export. This resolves
the candidate-export input blocker, but it is still not a K2 result.

The candidate-family plan is:

```text
python3 scripts/build_source_split_reconstruction_family_candidate_plan.py
```

It writes:

```text
evidence/source_split_reconstruction_family_candidate_plan.csv
evidence/source_split_reconstruction_family_candidate_summary.csv
```

The plan identifies SN residual and BAO residual branches as the first
public-input candidates for the missing response table. It also keeps
backreaction and optical propagation controls registered as later fair-null
sources, not as current scoring inputs.

The response-preview builder maps the current SN and BAO branch rows into the
frozen long-format schema:

```text
python3 scripts/build_source_split_reconstruction_family_response_preview.py
```

The preview is schema-valid, but K2 scoring remains blocked because the preview
is not the candidate export, the family-level sign rule is not locked, and the
covariance policy is not promoted to the scoring benchmark.

The family sign-rule preview is:

```text
python3 scripts/build_source_split_family_sign_rule_preview.py
```

It classifies preview rows as stable only when all nonzero family signs agree.
The current preview yields three stable rows and five warning rows. This
records the warning policy without promoting the preview to scoring evidence.

The promotion-readiness check keeps that boundary enforceable:

```text
python3 scripts/check_source_split_sign_rule_promotion.py
```

It currently reports that rule promotion is authorized for the validated
candidate export, while warning rows must remain explicit in any later
scorecard.

The final source-split K2 authorization guard is:

```text
python3 scripts/check_source_split_k2_scoring_authorization.py
```

It currently reports `AuthorizationDecision = BLOCKED`. This prevents the
preview artifacts from being accidentally treated as K2 scoring inputs.

The candidate-export handoff manifest is the current practical next step:

```text
python3 scripts/build_source_split_candidate_export_handoff.py
```

It keeps the real candidate export separate from the non-scoring preview and
lists the exact validation order required before any K2/null scorecard could be
considered.

The candidate export has now been created at:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

It contains the SN and BAO residual branches, two families total, with eight
usable target rows per family. The schema validation is clean. This removes the
candidate-export blocker but does not open K2 scoring.

The candidate path guard adds one more safety check: the real candidate path is
expected to be absent until a documented public export is prepared, and copying
the non-scoring preview into that path is explicitly blocked.

The source-split blocker matrix provides the compact operational state of this
branch. It should be read before any attempted K2 scorecard run, because it
lists every gate and handoff blocker that still prevents authorization.

The first blocker subtask is now the SN branch export handoff. It maps the
Pantheon+ binned SN residual branch into source-split standardized units for
all eight usable rows. These rows are now included in the real candidate
export.

The matching BAO branch export handoff is also ready. It maps the DESI DR2 BAO
residual branch into the same source-split standardized response scale for all
eight usable rows. These rows are now included in the real candidate export,
without opening K2 scoring.

The authorized source-split K2/null preflight scorecard is now exported:

```text
evidence/source_split_k2_null_scorecard.csv
evidence/source_split_k2_null_scorecard_summary.csv
```

Its main result is that the current zero-contrast source-split K1 target makes
the locked multiplicative K2 response degenerate with the no-memory control.
This is a weakening preflight result for this target, not final falsification.

The follow-up K1 degeneracy audit confirms this row by row and records the
requirements for a non-degenerate source-split K1 response target:

```text
evidence/source_split_k1_degeneracy_audit.csv
evidence/source_split_k1_degeneracy_summary.csv
evidence/source_split_k1_response_requirements.csv
```

The K1 candidate sensitivity audit then checks mechanically available nonzero
candidate responses from the validated reconstruction-family export:

```text
evidence/source_split_k1_response_candidate_audit.csv
evidence/source_split_k1_response_candidate_summary.csv
evidence/source_split_k1_candidate_sensitivity.csv
evidence/source_split_k1_candidate_sensitivity_summary.csv
```

Its current result is that nonzero candidates exist, but none is promoted to
primary K1. This keeps the source-split result in weakening/preflight status.

The promotion gate records that decision explicitly:

```text
python3 scripts/check_source_split_k1_candidate_promotion.py
```

It writes:

```text
evidence/source_split_k1_candidate_promotion_readiness.csv
evidence/source_split_k1_candidate_promotion_summary.csv
```

The current promotion count is zero. The zero-contrast K1 remains a fair null
but is degenerate for multiplicative K2; the common-mode mean is nonzero but
not externally predeclared; and the SN/BAO branch responses remain diagnostic
controls. The next required object is therefore an externally derived nonzero
K1 response target or a likelihood-native K1 target, not a post-hoc K1 chosen
because it improves the current scorecard.

That missing object now has its own export contract:

```text
python3 scripts/build_source_split_external_k1_export_schema.py
python3 scripts/validate_source_split_external_k1_export.py
```

It writes:

```text
evidence/source_split_external_k1_export_schema.csv
evidence/source_split_external_k1_export_template.csv
evidence/source_split_external_k1_export_readiness.csv
```

The candidate path is:

```text
data/k1/source_split_external_k1_response.csv
```

The current readiness state is `external_k1_export_missing`. This is the
correct conservative state: the repo now knows what an acceptable external K1
would look like, but it has not inserted a post-hoc K1 response to rescue K2.

The source routes for that missing object are registered by:

```text
python3 scripts/build_source_split_external_k1_source_registry.py
```

It writes:

```text
evidence/source_split_external_k1_source_registry.csv
evidence/source_split_external_k1_source_readiness.csv
```

No source route is currently authorized. The likelihood-native joint SN+BAO
baseline route is the cleanest future path; the reconstruction-family mean
route remains possible only after its averaging and amplitude policy are
declared before K2 scoring. The zero-contrast control, single-branch controls,
and same-data amplitude rescue path are not external K1 targets.

The reconstruction-family mean route is further separated into a policy gate:

```text
python3 scripts/build_source_split_family_mean_k1_policy.py
```

It writes:

```text
evidence/source_split_family_mean_k1_policy.csv
evidence/source_split_family_mean_k1_policy_readiness.csv
```

The equal-weight signed mean is nonzero on all eight usable rows, but it is not
allowed as the current external K1 because the policy was not frozen before the
current K2/null scorecard. It can only become a future route if the family mean
and amplitude policy are declared before rerunning the locked comparison.

The future rerun protocol is now explicit:

```text
python3 scripts/build_source_split_future_rerun_protocol.py
```

It writes:

```text
evidence/source_split_future_rerun_protocol.csv
evidence/source_split_future_rerun_protocol_summary.csv
```

The current decision is `no_current_rerun_authorized`. The preferred future
protocol is the likelihood-native joint K1 baseline route. The family-mean route
is secondary and only valid if frozen before a future rerun. A post-hoc K1 based
on current residuals is recorded as a forbidden path.

The secondary route now has a concrete future-only export:

```text
python3 scripts/build_source_split_family_mean_k1_future_export.py
python3 scripts/validate_source_split_external_k1_export.py
```

It writes:

```text
data/k1/source_split_external_k1_response.csv
evidence/source_split_family_mean_k1_future_export_summary.csv
evidence/source_split_external_k1_export_readiness.csv
```

The export is available and nonzero on all eight usable rows, but it remains
blocked for current primary K1 use by `not_marked_primary_candidate`. This is
intentional: it prepares a future rerun without opening the present measurement
gate.

The future-only family-mean route is then checked by:

```text
python3 scripts/run_source_split_future_k1_k2_dry_run.py
```

It writes:

```text
evidence/source_split_future_k1_k2_dry_run.csv
evidence/source_split_future_k1_k2_dry_run_summary.csv
```

The current dry-run result is weakening for the family-mean route:
`K1FamilyMeanAIC = 25.062371419386807`, while
`K2Rho4AIC = 52.5499794390236`. This does not open or close the measurement
gate; it says the secondary family-mean route is not currently the strongest
next path.

The preferred likelihood-native route is tracked by:

```text
python3 scripts/build_source_split_likelihood_native_k1_plan.py
```

It writes:

```text
evidence/source_split_likelihood_native_k1_plan.csv
evidence/source_split_likelihood_native_k1_readiness.csv
```

The current readiness state is `likelihood_native_k1_not_ready`. Public SN and
BAO inputs, the joint likelihood specification, and the frozen CMB-only
parameter source are available. The remaining blockers are the baseline
prediction vector, likelihood-native coordinate map, promoted covariance policy,
likelihood-native K1 export, and null scores on the same vector. The next
artifact is:

```text
data/k1/source_split_likelihood_native_baseline_prediction.csv
```

The specification has now been written:

```text
docs/source_split_likelihood_native_k1_spec.md
```

The next implementation artifact was the frozen parameter source:

The frozen parameter source has now been written:

```text
data/k1/source_split_likelihood_native_parameters.yaml
evidence/source_split_likelihood_native_parameters_summary.csv
```

It is a parameter source only. It does not yet authorize a likelihood-native K1
export or a new locked K2/null comparison.

The preflight baseline prediction vector and coordinate map have now been
written:

```text
data/k1/source_split_likelihood_native_baseline_prediction.csv
data/k1/source_split_likelihood_native_coordinate_map.csv
```

They make the route executable at the artifact level, but do not yet open the
measurement gate. The remaining issue is promotion: SN nuisance handling, joint
covariance, the likelihood-native K1 export, and null scores must all be
registered on the same vector before locked K2 can be compared again.

After rerunning the readiness check, all nine required artifacts have data or
preflight placeholders, but five promotion blockers remain.

The promotion gate has now been added:

```text
evidence/source_split_likelihood_native_k1_promotion_gate.csv
evidence/source_split_likelihood_native_k1_promotion_summary.csv
```

It reports `PrimaryK1PromotionAllowed = False`. This is not a negative K2
result; it means the likelihood-native K1 route has not yet reached export
quality.

The first promotion policy now fixes the nuisance boundary: raw source-split
response is the primary K1 candidate path, while same-sample-centered response
is a control only. This reduces the main hidden-fit risk before any future
scorecard is run.

The coordinate promotion policy now fixes the next candidate coordinate as the
frozen CMB-chi depth map. This is a predeclared benchmark choice, not a
post-hoc coordinate rescue, and coordinate controls remain part of the reporting
boundary.

The covariance promotion policy now marks the shrinkage covariance as a
declared preflight benchmark covariance. It can be used consistently for K1,
locked K2, and null comparators in a future preflight scorecard, but it remains
below public full-covariance measurement-validation level.

That preflight scorecard now exists. It is a useful diagnostic because K2 is no
longer degenerate with K1 on the promoted likelihood-native vector. However, it
is not yet supportive measurement evidence: K2 improves over K1, while simple
polynomial controls still achieve much lower AIC/BIC under the current proxy
scoring.

The row-level diagnosis shows why: the likelihood-native preflight score is
dominated by an amplitude gap at low depth. Four rows have target amplitude more
than five times larger than the K2 prediction, and the first two rows dominate
the chi2. This points to target-scale, covariance, or independently declared
amplitude-normalization work, not to a post-hoc K1 rescue.

The rho-requirement audit makes the boundary sharper: no row can be exactly
matched with `rho<=4`, and the bounded scan chooses `rho=4`. This keeps the
locked operator discipline intact and turns the next work toward scale and
covariance diagnostics.

The scale/covariance sensitivity confirms that direction. K2 is not random
noise relative to K1; it improves over K1 across the tested cases. But it is
competitive with flexible controls only under a strong target-fraction error
floor, so the next empirical requirement is an independently justified
covariance/scale model.

The follow-up error-floor sweep makes the scale dependence more precise. Under
the current likelihood-native source-split preflight vector, `K2_LOCKED_RHO4`
first becomes the best AIC model at a target-fraction floor of 0.14. This is a
diagnostic threshold only, not a selected benchmark covariance. A future
measurement gate would need an independently declared covariance or systematic
floor before using this scale in a stronger comparison.

The companion error-floor policy keeps this boundary explicit. The public
SN/BAO branch-scatter preflight exceeds the 0.14 scale, but it is not yet an
eligible benchmark covariance. It remains a clue for the next covariance route,
not a measurement-gate result.

That covariance route has now been tested as a preflight benchmark. Under the
declared branch-scatter scale, the locked K2 response is the best AIC model
across all tested branch-scatter covariance variants. This is the strongest
current conditional support for K2, but it remains preflight-level because the
branch-scatter covariance is not public full covariance.

The promotion gate reflects this exactly: branch scatter may be promoted to a
declared preflight benchmark, while measurement validation remains blocked by
the absence of public full covariance and an independent systematic/covariance
source.

The covariance-source registry now identifies the precise next blocker. Raw
Pantheon+ and DESI covariance inputs are locally available, but they have not
been propagated into the likelihood-native source-split vector. Therefore the
next decisive work is a public SN+BAO covariance transform, not another K2
operator adjustment.

The first public covariance proxy and its cross-covariance sensitivity audit
keep the public route mixed: K2 improves over K1/no-memory, but polynomial
controls remain stronger. Branch scatter therefore remains the stronger current
preflight route.

The route-level covariance scorecard now summarizes the split mechanically. K2
improves over K1/no-memory on all tested covariance routes, and it beats the
best polynomial controls on the branch-scatter family of preflight routes. The
public covariance proxy routes remain mixed and do not yet beat the polynomial
controls. The immediate blocker is therefore covariance-route quality, not a
need to alter the locked K2 kernel.

The covariance-gap audit adds the row-level explanation. K2 improves over
K1/no-memory on every usable source-split row under both public-proxy and
branch-scatter diagonal decompositions. The current weakness is instead
polynomial-control dominance under the public-proxy route. This keeps the next
work focused on covariance quality and independent route registration rather
than K2 refitting.

The polynomial cross-validation audit partially weakens that objection. The
public-proxy leave-one-out check still favors `POLY_DEG2`, but blocked
validation favors K2. Under branch-scatter and native-plus-branch-scatter
routes, K2 beats the polynomial controls in both leave-one-out and blocked
validation. The polynomial-control advantage is therefore not stable enough to
be treated as final falsification at preflight level.

The support ladder now summarizes the status: K2-vs-K1 is supportive at
preflight level; K2-vs-polynomial controls is mixed but conditionally
supportive; the public covariance route is still weakening; branch scatter is
the strongest declared preflight route; measurement validation remains blocked.
The next work is covariance-route improvement, not K2 modification.

The public-covariance upgrade queue freezes the next work items. Measurement
validation remains blocked until a full likelihood-native covariance transform
or a registered shrinkage/scatter route is declared, the SN-BAO cross-covariance
policy is fixed, and the next rerun protocol is locked before execution.

The public-covariance locked rerun protocol now performs that last step. It
defines the preferred full-likelihood route, the secondary registered
branch-scatter route, and the forbidden post-hoc rescue route. Its readiness
output authorizes zero current stronger reruns, which keeps the current result
as preflight evidence only.

The public-covariance policy registry adds the covariance route boundary. The
only currently available policy is row-aligned cross-covariance sensitivity,
which cannot be selected as the benchmark route. Full-public, registered
shrinkage, and registered branch-scatter policies remain unavailable for
stronger interpretation.

The registered-shrinkage rerun template now defines the possible proxy route
without executing it. It locks the K2 operator, K1 source, coordinate mapping,
null comparators, validation modes, and acceptance rule. The covariance
parameters and cross-covariance policy remain unregistered, so the route is not
yet allowed to run.

The registered-shrinkage parameter policy now freezes those missing parameters
for future preflight use: `lambda=0.15`, an exponential distance kernel with
correlation length `0.25`, and `rho_SN_BAO=0` as the primary cross-covariance
choice with sensitivity reported separately. This completes the template
structurally, but it still authorizes no current stronger rerun.

The activation gate now allows registered shrinkage as a future-preflight route
only. It reports zero preflight blockers, two measurement blockers, and no
current scorecard authorization. The next valid step is a separate future
preflight script that consumes the registered policy without modifying K2 or
K1.

That future-preflight scorecard now exists. It reports a weakening but useful
result: K2 improves over K1/no-memory, while `POLY_DEG2` remains stronger under
the registered shrinkage covariance. Therefore registered shrinkage is not a
K2 rescue route.

The polynomial-control fairness audit keeps this boundary precise. Polynomial
controls are mandatory overfit-risk controls, not physical null explanations.
They cannot be dismissed while they win some public-proxy tests. Measurement
validation remains blocked until K2 is competitive against them under a public
benchmark or a more specific physical null hierarchy is registered.

The physical null hierarchy now registers that more specific comparator layer.
It shows that the physical-null layer is incomplete for scoring: no-memory is
implemented, while backreaction-only and Dyer-Roeder/optical controls now exist
only as non-scoring templates on the same source-split benchmark.

The physical-null amplitude policy now permits those templates to enter future
preflight scorecards only as sanity / sensitivity controls. It does not provide
physical amplitude calibration.

The current policy registry separates the allowed and forbidden routes:
`PHYSNULL_AMP_UNIT_ONLY_V1` is the primary unit-norm sanity comparator,
`PHYSNULL_AMP_BOUNDED_GRID_V1` is a secondary bounded sensitivity scan that
must report all amplitudes, and `PHYSNULL_AMP_FORBIDDEN_FREE_FIT_V1` blocks any
post-hoc least-squares or information-criterion amplitude rescue. This makes a
physical-null preflight scorecard possible, while keeping measurement
validation blocked until physical amplitudes are calibrated independently.

That physical-null preflight scorecard now exists:

- `evidence/physical_null_preflight_scorecard.csv`;
- `evidence/physical_null_preflight_summary.csv`.

Under the branch-scatter preflight covariance scale, locked K2 is stronger than
K1/no-memory and the reported physical-null sanity/sensitivity controls. This is
a useful K2-supportive preflight result. It is not measurement validation,
because the physical-null amplitudes are still not independently calibrated and
the covariance scale is not a public full likelihood covariance.

The row-level physical-null audit reports a narrower result: K2 improves over
K1/no-memory on all eight rows, but splits 4-4 against the best reported
physical-null row. The net chi2 contribution still favors K2 slightly. This
keeps the physical-null route supportive at preflight level but not resolved.

The physical-null calibration requirements now state what is missing before a
measurement-grade comparison: independent backreaction and optical-propagation
amplitude sources with covariance on the same coordinate-native vector. Fitting
those amplitudes from the same K2 scorecard is forbidden.

The calibration source registry now lists the candidate source classes and task
queue. It registers backreaction constraints, simulation priors, Dyer-Roeder
`alpha(z)`/clumpiness constraints, and optical proxy routes as candidates, but
none is currently ingested or mapped to the benchmark vector.

The physical-null mapping policy freezes how future sources may enter the
benchmark: monotone interpolation to the existing source-split rows, no
extrapolation, no smoothing chosen from K2 residuals, and preservation of any
external amplitude calibration.

The physical-null covariance policy freezes the uncertainty boundary. The
preferred route is source-native covariance propagated to the source-split
rows. Diagonal and shrinkage proxies remain preflight-only, and post-scorecard
uncertainty rescue is forbidden.

The physical-null readiness dashboard now summarizes this branch: K2 is
supportive but narrow at preflight level, while source ingestion, mapping
execution, and covariance propagation remain open measurement blockers.

The public-source candidate inventory now lists concrete acquisition targets,
but no candidate source is yet ingested, digitized, covariance-ready, or mapped
to the source-split vector.

The candidate triage ranks Koksbang's backreaction constraint paper as the first
backreaction ingest target, and two Dyer-Roeder smoothness-parameter papers as
the first optical ingest targets. This does not create a measurement input; it
only prioritizes acquisition.

## Current Null Dominance Diagnosis

The current null dominance audit adds:

- `evidence/null_dominance_audit.csv`;
- `evidence/null_dominance_summary.csv`;
- `evidence/subset_model_scorecard.csv`;
- `evidence/cross_validation_results.csv`;
- `evidence/shrinkage_covariance_sensitivity.csv`.

Current interpretation:

- `K1_NO_MEMORY` remains stronger than fixed `K2_LOCKED_RHO4` under the current
  diagonal proxy and simple validation checks;
- the K2 penalty is not only a single hidden point effect;
- the K1 advantage shrinks under correlated covariance proxies;
- therefore the current result is a weakening signal for distinct K2
  contribution, not a final falsification.

## Current BAO Branch Decision

The BAO public-data branch has reached a useful preflight decision point:

- public DESI BAO inputs are locally available and shape-validated;
- the BAO residual transform and covariance propagation run reproducibly;
- same-data DESI best-fit and same-data `rd` offset baselines are useful
  controls but cannot be primary K2 baselines;
- the independent CMB-only baseline is available but less BAO-compatible;
- the CMB-only unit-covariance K1 candidate is normalizable but loses to the
  zero-response null in the current scorecard.

Therefore BAO K2 measurement-gate scoring remains closed. The branch should be
kept as a documented preflight/control path until a coordinate-native or
likelihood-native BAO K1 target is selected under the same covariance benchmark.
The recommended primary empirical pivot is SN+BAO/source-split or another
coordinate-native public benchmark where a locked no-memory target can be
defined without calibrating the response amplitude on the tested BAO vector.

## SN+BAO/Source-Split Readiness

The next branch is tracked by:

```text
python3 scripts/check_source_split_readiness.py
```

It writes:

```text
evidence/source_split_readiness.csv
```

Current interpretation:

- public Pantheon+SH0ES SN input is available;
- public DESI DR2 BAO input is available;
- the current diagnostic packet already contains sign-family splits;
- fair null comparator families are registered;
- the coordinate-native and likelihood-native K1/no-memory targets are not yet
  selected.

Therefore source-split K2 scoring is not yet authorized. The immediate work is
to define the source-split diagnostic transform and export a coordinate-native
K1 target before evaluating the locked finite-memory multiplier.

The transform contract is tracked by:

```text
python3 scripts/check_source_split_transform_contract.py
```

It writes:

```text
evidence/source_split_transform_readiness.csv
```

This registry separates the current distilled sign-family packet from the
future public source-split diagnostic vector. The current packet can guide the
sign-stability policy, but it is not a public covariance-native measurement
target.

The first SN residual preflight is:

```text
python3 scripts/build_sn_residual_preflight.py
```

It writes SN residual rows and binned rows from Pantheon+SH0ES. The centered
residual subtracts a same-sample offset, so it remains a transform-development
artifact rather than a K1/no-memory target.

The first joint source-split preflight is:

```text
python3 scripts/build_source_split_joint_preflight.py
```

It aligns the current sign-stability packet, binned SN residuals, and nearest
BAO residual anchors. The output remains preflight only because the residual
units differ and the joint covariance/K1 target are not yet exported.

The common-scale preflight is:

```text
python3 scripts/build_source_split_standardized_preflight.py
```

It divides the SN and BAO branch residuals by their diagonal uncertainty
estimates. This removes the immediate unit mismatch for audit purposes, but it
is still not a physical K1 target. In the current output, five of eight rows
with both branches have opposite standardized signs, which is a source-split
warning rather than a K2 result.

The sign-tension diagnosis is:

```text
python3 scripts/diagnose_source_split_sign_tension.py
```

It shows that the standardized source-split warning is concentrated in
sign-stable rows: four of five sign-stable rows with both branches have
opposite SN/BAO signs. This makes the source-split branch scientifically
interesting, but it also keeps K2 scoring closed until a joint covariance and
coordinate-native K1 target exist.

The covariance-proxy sensitivity check is:

```text
python3 scripts/run_source_split_covariance_sensitivity.py
```

It varies a simple within-row SN-BAO correlation proxy. The opposite-sign counts
remain unchanged across the tested proxy range, while contrast magnitudes vary.
This supports treating the source-split warning as a real transform-development
issue, not as a reason to score K2 prematurely.

The source-split K1 target gate is:

```text
python3 scripts/check_source_split_k1_target.py
```

It writes:

```text
evidence/source_split_k1_target_readiness.csv
```

No source-split K1 target is currently allowed for K2 scoring. The standardized
zero-response object is a fair null/control, but not a K1 target. The required
next object is `SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET`, with joint
covariance and sign-family export.

The joint covariance gate is:

```text
python3 scripts/check_source_split_covariance.py
```

It writes:

```text
evidence/source_split_covariance_readiness.csv
```

No covariance candidate is currently allowed for K2 scoring. The diagonal
standardized proxy and within-row correlation proxy remain useful controls, but
the required target is a public or declared shrinkage joint covariance in the
same source-split space as the coordinate-native K1 target.

The public sign-family export gate is:

```text
python3 scripts/check_sign_family_export.py
```

It writes:

```text
evidence/sign_family_export_readiness.csv
```

No sign-family export is currently allowed for K2 scoring. The current
distilled packet and standardized source-split branch-sign audit remain useful
templates, but the required target is `SF_PUBLIC_SOURCE_SPLIT_FAMILIES`: public
reconstruction families with a declared sign-stable rule in the same
coordinate-native source-split space.

The compact source-split dashboard is:

```text
python3 scripts/build_source_split_gate_dashboard.py
```

It writes:

```text
evidence/source_split_gate_dashboard.csv
evidence/source_split_gate_dashboard_summary.csv
```

The current dashboard keeps the input/null side open but closes all core
measurement gates: transform, K1 target, joint covariance, sign-family export,
reconstruction-family candidate export, response-preview promotion, and
sign-rule promotion. The primary next action is to create a valid public
reconstruction-family candidate export before promoting the sign rule or
scoring K2.

The ordered export task queue is:

```text
python3 scripts/build_source_split_export_task_queue.py
```

It writes:

```text
evidence/source_split_export_task_queue.csv
evidence/source_split_export_task_queue_summary.csv
```

The next active blocker is now `TQ4C_SIGN_RULE_PROMOTION`. The schema and
non-scoring preview tasks are completed, but sign-rule promotion remains
blocked until a real public reconstruction-family candidate export validates
cleanly. K2 scoring remains blocked by the final authorization guard.

The next serious benchmark must use public covariance or a declared
shrinkage-covariance prescription and a coordinate-native baseline export.

## Phase II Public Benchmark Preflight

The preflight manifest is:

```text
data/public_ingest_manifest.yaml
```

The readiness check is:

```text
python3 scripts/check_public_benchmark_readiness.py
```

It writes:

```text
evidence/public_benchmark_readiness.csv
```

Current status: public input preflight is partially unblocked. The repo now
contains local DESI DR2 BAO, DESI DR1 BAO fallback, and Pantheon+SH0ES SN
candidate files, and `evidence/public_input_inventory.csv` validates their
basic data/covariance dimensions. The remaining blockers are not missing files:
they are the finite-memory diagnostic transform, the coordinate-native or
likelihood-native mapping, and the public covariance-aware benchmark definition.

The first raw-observable preflight table is
`evidence/public_diagnostic_transform_preflight.csv`, summarized by
`evidence/public_diagnostic_transform_summary.csv`. It puts DESI and Pantheon+
inputs into a common row schema with audit coordinates and diagonal covariance
scales, while explicitly marking every row as not yet a K2 diagnostic vector.

The diagnostic-transform contract is now checked by
`scripts/check_diagnostic_transform_contract.py`, which writes
`evidence/diagnostic_transform_readiness.csv`. The current contract has no
measurement-gate-allowed transform. This is intentional: `T0` is
raw-observable preflight only, and `T1_BAO_DISTANCE_RATIO_RESIDUAL` is a BAO
residual preflight transform using an audit-fiducial baseline rather than a
likelihood-native K1 export.

The T1 null benchmark indicates that a constant-offset control is preferred
under this audit baseline. This is a preflight weakening signal for direct T1
use, not a finite-memory falsification. The next step is to remove the
audit-baseline offset ambiguity by exporting a likelihood-native or
coordinate-native BAO baseline before comparing against the locked prediction.

The baseline-offset diagnosis finds that this constant mode is consistent with
an approximately 1.5 percent BAO scale offset, equivalent to an effective
`rd` near 144.8 Mpc under the audit baseline. This reinforces the interpretation
that T1 is currently baseline-limited rather than memory-limited.

The BAO baseline export readiness check keeps the gate closed: no current BAO
baseline export is eligible for measurement-gate scoring. This is the expected
state until a public likelihood-native or coordinate-native BAO baseline is
frozen.

The same-data `rd` offset sensitivity reduces the residual score to the
constant-offset benchmark level, confirming that the current T1 residual layer
is baseline-scale dominated. Since the `rd` value is inferred from the same
BAO vector, this does not open the measurement gate.

The likelihood-native source-readiness check currently finds no eligible BAO
baseline source. Public data/covariance are available, but a baseline prediction
requires either a public best-fit/chain export or a reproducible model
evaluator with frozen parameters.

The public DESI DR2 `iminuit/base/desi-bao-all` best-fit has now been ingested
and reproduces the reported BAO fit quality at preflight precision. This is a
stronger baseline-export plumbing check, but it still does not open the
measurement gate because the baseline is optimized on the same BAO data.

A CMB-only public best-fit has also been exported as a more independent BAO
baseline. It yields a higher BAO chi2 than the same-data DESI best fit. The
baseline scorecard therefore separates baseline independence from BAO fit
quality before any locked finite-memory comparison is attempted.

The BAO K2 protocol registry now exists, but its readiness check is false by
construction. The protocol records the baseline bracket, required nulls,
shared-covariance rule, and locked `p=3`, `rho<=4` policy before any K2 scoring
script is allowed.

The BAO K1/no-memory response readiness check adds the immediate blocker:
there are useful controls, including zero residual, constant offset, same-data
DESI best-fit residual, and CMB-only residual, but no locked BAO K1 response
target is allowed for K2 scoring. The missing object is the amplitude-normalized
`BAO_K1_LOCKED_RESPONSE_TARGET`.

The locked-response plan now defines the missing object explicitly. The current
most plausible candidate is a CMB-only residual normalized to unit covariance
norm, but it remains unselected and lacks a null scorecard. This keeps the BAO
K2 measurement gate closed.

The candidate null scorecard has now been added. It finds that the normalized
CMB-only K1 candidate is not structurally stronger than the zero-response null
under AIC. This weakens the case for selecting it as the locked BAO K1 target.

The physical-null acquisition branch now has a source-package probe:

```text
python3 scripts/probe_physical_null_candidate_sources.py
```

It writes:

```text
evidence/physical_null_candidate_source_probe.csv
evidence/physical_null_candidate_source_probe_summary.csv
```

The current result is acquisition-positive but measurement-closed: all three
first candidates were probed, one exposes a data-like route and two expose
TeX/table-marker routes, but no calibration values are ingested or mapped to the
source-split vector.

The follow-up provisional extraction manifest is:

```text
python3 scripts/build_physical_null_provisional_extraction_manifest.py
```

It writes:

```text
evidence/physical_null_provisional_extraction_manifest.csv
evidence/physical_null_provisional_extraction_summary.csv
```

It records seven provisional Dyer-Roeder optical rows and one Koksbang
backreaction route row. All eight rows remain blocked for benchmark use. The
Koksbang branch still needs a numeric backreaction envelope or reconstruction
route; the Dyer-Roeder branch needs source-split mapping and covariance.

The mapping-readiness check is:

```text
python3 scripts/check_physical_null_mapping_readiness.py
```

It writes:

```text
evidence/physical_null_mapping_readiness.csv
evidence/physical_null_mapping_readiness_summary.csv
```

It finds two full-coverage optical rows but zero rows with a declared
source-split transform or covariance propagation. The follow-up task queue is:

```text
python3 scripts/build_physical_null_mapping_task_queue.py
```

It writes:

```text
evidence/physical_null_mapping_task_queue.csv
evidence/physical_null_mapping_task_queue_summary.csv
```

The first queued task is `PX_ZKDR_1303_TABLE1_JOINT_ALPHA_PRIOR`: define an
`alpha -> source-split response` transform and propagate uncertainty. This still
does not open measurement scoring.

The first alpha transform contract is:

```text
python3 scripts/build_physical_null_alpha_transform_contract.py
```

It writes:

```text
evidence/physical_null_alpha_transform_policy.csv
evidence/physical_null_alpha_response_preview.csv
evidence/physical_null_alpha_transform_summary.csv
```

The policy fixes the preview transform
`response_i=(1-alpha)*DYER_ROEDER_OPTICAL_UNIT_NORM_V1_i`. It previews two
full-coverage joint Dyer-Roeder alpha rows and keeps all rows non-scoring. The
remaining blockers are a sign-convention audit and covariance propagation.

The sign-convention audit is:

```text
python3 scripts/audit_physical_null_alpha_sign_convention.py
```

It writes:

```text
evidence/physical_null_alpha_sign_convention_audit.csv
evidence/physical_null_alpha_sign_convention_summary.csv
```

The audit finds a split result: the inverted convention matches more total rows,
while the as-declared convention matches more sign-stable rows. This prevents a
score-based sign choice. A future physical-null scorecard must freeze the sign
from external optical-response reasoning before scoring.

The alpha covariance preview is:

```text
python3 scripts/build_physical_null_alpha_covariance_preview.py
```

It writes:

```text
evidence/physical_null_alpha_covariance_preview_policy.csv
evidence/physical_null_alpha_covariance_preview_matrix.csv
evidence/physical_null_alpha_covariance_preview_summary.csv
```

It exports diagonal and fixed exponential-in-`x` preview covariance matrices for
the two full-coverage alpha candidates. These matrices are plumbing artifacts
only: they do not replace source-native covariance and do not open physical-null
scoring.

The alpha scoring authorization guard is:

```text
python3 scripts/check_physical_null_alpha_scoring_authorization.py
```

It writes:

```text
evidence/physical_null_alpha_scoring_authorization.csv
evidence/physical_null_alpha_scoring_authorization_summary.csv
```

The guard finds two technically prepared alpha candidates, but authorizes zero
scorecard rows. The remaining blockers are external sign-convention freezing,
source-native covariance, and explicit measurement-scorecard authorization.
