# SN+BAO Source-Split Benchmark Plan

Status: next empirical branch; readiness check added; K2 scoring not yet
authorized.

The BAO-only public-data branch is now a documented preflight/control path.
The next primary measurement-gate candidate is the SN+BAO/source-split branch,
because the current diagnostic packet already contains sign-family information
and the public SN and BAO inputs are locally available.

## Goal

Build a coordinate-native source-split benchmark that asks whether the locked
finite-memory projection hypothesis adds information beyond no-memory, optical,
backreaction, and reconstruction-artifact null comparators.

This branch must not change the locked K2 kernel:

```text
W(x) = 1 + rho*x^3
p = 3
rho <= 4
```

## What Is Already Available

- Pantheon+SH0ES SN data vector and covariance are locally available.
- DESI DR2 BAO mean/covariance products are locally available.
- The current distilled SN+BAO packet contains sign-family columns:
  `all_sign`, `no_degree4_sign`, `degree2_sign`, and `sign_stable`.
- Null comparator families are registered.
- The current measurement-gate harness can already score diagnostic packets
  once a target vector, covariance, coordinate mapping, and K1/no-memory target
  are exported.

## What Is Still Missing

- a public source-split diagnostic transform from SN/BAO observables to the K2
  target space;
- a coordinate-native K1/no-memory target;
- a shared covariance or shrinkage covariance prescription for the transformed
  target;
- source-split versions of the optical, backreaction, no-memory, and
  reconstruction-artifact comparators;
- a rule for keeping sign-unstable rows as warnings rather than hidden failures
  or hidden support.

## Readiness Gate

Run:

```text
python3 scripts/check_source_split_readiness.py
python3 scripts/build_source_split_gate_dashboard.py
python3 scripts/build_source_split_export_task_queue.py
```

They write:

```text
evidence/source_split_readiness.csv
evidence/source_split_gate_dashboard.csv
evidence/source_split_gate_dashboard_summary.csv
evidence/source_split_export_task_queue.csv
evidence/source_split_export_task_queue_summary.csv
```

The gate remains closed even though the public reconstruction-family candidate
export now exists and the sign rule is promoted after validation. That is
intentional: the branch still needs the public diagnostic transform, K1,
covariance, and sign-family gates to authorize K2 scoring.

Current dashboard interpretation:

- public inputs and null registry are available;
- the standardized source-split transform is available as preflight only;
- no coordinate-native K1/no-memory target is selected;
- no joint source-split covariance is selected;
- no public source-split sign-family export is selected;
- K2 scoring remains closed.

Current task-queue interpretation:

- `TQ1_COORDINATE_NATIVE_TRANSFORM` is completed as a preflight target export;
- `TQ2_COORDINATE_NATIVE_K1` is completed as a zero-contrast K1/control
  preflight;
- `TQ3_JOINT_COVARIANCE` is completed as a shrinkage covariance-policy
  preflight;
- `TQ4_PUBLIC_SIGN_FAMILY` is completed as a public branch-sign preflight;
- `TQ4A_CANDIDATE_EXPORT_SCHEMA` is completed as a schema preflight;
- `TQ4B_CANDIDATE_EXPORT_PREVIEW` is completed as a non-scoring preview;
- `TQ4C_SIGN_RULE_PROMOTION` is authorized after the validated candidate export;
- the reconstruction-family upgrade contract is exported and identifies the
  remaining public family-response/sign-rule blockers;
- K2 scoring remains blocked until the downstream exports are complete.

The TQ1 artifact is:

```text
evidence/source_split_coordinate_native_target.csv
```

It defines `SourceSplitResponse = SN_standardized - BAO_standardized` on the
`x_chi_normalized_flat_lcdm_audit` coordinate. It remains a preflight target
only, not a K1 baseline and not a K2 scoring result.

The TQ2 artifact is:

```text
evidence/source_split_k1_coordinate_native_target.csv
```

It defines the no-memory control as zero standardized SN-minus-BAO branch
contrast. It remains a control preflight, not a K2 scoring result.

The TQ3 artifact is:

```text
evidence/source_split_joint_covariance_policy.csv
```

It defines a positive-definite shrinkage covariance policy on the same eight
usable target rows. It remains a covariance-policy preflight, not a public full
covariance and not a K2 scoring result.

The TQ4 artifact is:

```text
evidence/source_split_public_sign_family.csv
```

It exports SN and BAO branch signs on the same coordinate-native target rows.
It remains a branch-sign preflight, not a full reconstruction-family export and
not a K2 scoring result.

The upgrade contract is:

```text
evidence/source_split_reconstruction_family_upgrade_contract.csv
```

It records that row alignment and warning policy are available, while public
reconstruction-family responses and a family-level sign-stability rule are
still missing.

The corresponding source-readiness registry is:

```text
evidence/source_split_reconstruction_family_source_registry.csv
evidence/source_split_reconstruction_family_source_readiness.csv
```

It keeps the current distilled packet, the public branch-sign preflight, the
missing public reconstruction-family export, and the later likelihood-native
target separate. The public branch-sign preflight remains useful as a warning
control, but it is not a scoring-grade reconstruction-family source.

The required public reconstruction-family response export now has a frozen
schema and validator:

```text
evidence/source_split_reconstruction_family_export_schema.csv
evidence/source_split_reconstruction_family_export_template.csv
evidence/source_split_reconstruction_family_export_validation.csv
```

The current validation state is clean for the real public response table. This
resolves the candidate-export blocker while keeping K2 scoring closed until the
remaining gates are resolved.

The candidate-family plan then identifies the first practical export targets:

```text
evidence/source_split_reconstruction_family_candidate_plan.csv
evidence/source_split_reconstruction_family_candidate_summary.csv
```

The immediate export candidates are the Pantheon+ SN residual branch and DESI
DR2 BAO residual branch. They are not K2 inputs yet; they are source candidates
for the missing reconstruction-family response table.

A non-scoring response preview now maps those two branches into the frozen
schema. It is schema-valid, with two families across eight usable rows, but it
remains blocked because it is only a preview and the family-level scoring rule
is not locked.

The row-level sign-rule preview then classifies those same eight rows with the
rule `stable if all nonzero public reconstruction-family signs agree`. It gives
three stable rows and five warning rows. This is a warning-policy preview, not
a scoring rule.

The promotion-readiness gate confirms the same boundary: the preview rule is
declared, warning rows are retained, and rule promotion is now authorized for
the validated candidate export.

The final source-split K2 authorization guard then aggregates the required
gates and currently returns `AuthorizationDecision = BLOCKED`. This is now due
to remaining transform, K1, covariance, and sign-family gates rather than
candidate-export absence.

The candidate-export handoff manifest records the candidate data object:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

It also records the validation order from schema, to SN/BAO branch export, to
sign-rule promotion, to final K2 authorization.

A candidate path guard also records that the real candidate path is currently
absent and prevents a shortcut copy from the non-scoring preview.

The blocker matrix aggregates the dashboard, handoff, and authorization guards.
It now reports upstream gates as the primary blocker, with the candidate export
present and validated.

After gate synchronization, the source-split K2/null preflight scorecard runs.
The current result weakens distinct K2 evidence on this source-split target:
the zero-contrast K1/no-memory target makes the multiplicative K2 response
zero as well, so locked K2 is not distinguishable from the no-memory control in
this benchmark.

The follow-up K1 promotion gate now records that no mechanically available K1
candidate is eligible for promotion to primary source-split K1. Nonzero
candidate arrays exist, but the common-mode mean lacks predeclared external
provenance and the single-branch responses are diagnostic controls. The branch
therefore needs an externally derived nonzero K1 target or a likelihood-native
K1 target before it can make a distinct K2 measurement-gate comparison.

The external K1 target requirement is now encoded as a schema and validator.
The expected candidate file is:

```text
data/k1/source_split_external_k1_response.csv
```

The current readiness output reports `external_k1_export_missing`. This means
the branch has a clear next input contract, but no K1 rescue has been inserted.

The source-route registry now records the possible origins for that missing
external K1. The likelihood-native joint SN+BAO baseline is the preferred clean
route. An external reconstruction-family mean is a possible preflight route
only if the family averaging and amplitude policy are predeclared. The
zero-contrast control, single-branch controls, and same-data amplitude rescue
path remain blocked as primary K1 sources.

The family-mean route now has a policy gate. It records that the equal-weight
signed mean is nonzero on all eight usable rows, but no family-mean policy is
authorized for the current external K1 export because it was not frozen before
the current scorecard. This keeps the branch honest: the family mean is a
future predeclared route, not a retroactive K1 rescue.

The future rerun protocol then freezes the operational boundary. It authorizes
no current rerun. A likelihood-native joint SN+BAO K1 baseline is the preferred
future route; an equal-weight family mean is a secondary future preflight route
only after pre-registration; and a current-scorecard K1 rescue is forbidden.

The equal-weight family mean has now been exported as a future-only K1
candidate. It is nonzero on all eight usable rows and validates as available,
but it is deliberately not marked as current primary K1. The source-split branch
therefore moves from "missing candidate file" to "future candidate exists,
current gate closed".

The future-only dry run is also complete. It shows that the family-mean K1
route is not currently promising as a primary path: locked K2 rho=4 has a worse
AIC than the family-mean K1 itself under the preflight covariance. The branch
therefore should pivot toward the likelihood-native joint SN+BAO baseline
rather than promote the family-mean route.

The likelihood-native K1 route now has a concrete readiness plan. It reports
that public SN and BAO inputs are available. The joint likelihood-native K1
specification, the frozen CMB-only parameter source, the preflight baseline
prediction vector, and the preflight coordinate map are now written.

The preflight baseline prediction vector and coordinate map are now also
available. They close the missing-file part of the route, but not the K1 export
gate: the baseline vector still carries an SN nuisance-policy blocker, and the
coordinate map is a CMB-parameter comoving-distance preflight rather than a
promoted joint likelihood-native map. The next task is therefore promotion and
validation, not K2 scoring.

The promotion gate is now explicit. It reports five checks, four available
preflight artifacts, zero promotable checks, and five blockers. This keeps the
source-split likelihood-native K1 route closed until the baseline vector,
coordinate map, covariance policy, null scorecard, and external K1 export are
all promoted together.

The nuisance policy is now explicit: the raw source-split response is the only
candidate for primary K1 promotion, while the same-sample-centered response is
kept as a control. This prevents the SN offset from becoming a hidden K1
amplitude fit.

The coordinate promotion policy is also explicit. The CMB-parameter
comoving-distance coordinate is the next benchmark candidate coordinate, but it
must be used consistently for K1, locked K2, and null comparators, and the older
coordinate-robustness controls remain reportable.

The covariance promotion policy is now explicit as well. The current shrinkage
covariance may support an internally consistent null-scorecard preflight, but
it is not public full covariance and cannot support measurement validation.

The likelihood-native external K1 export now validates as a primary K1
preflight object, and the guarded null-scorecard has run. The result is mixed:
locked K2 improves over K1/no-memory on this vector, but polynomial controls
dominate the information criteria. This keeps the branch scientifically useful
but below measurement-validation strength.

A dominance audit isolates the mechanism. The main loss is an amplitude gap,
especially in the first two low-depth rows: K2 has the right broad direction
relative to K1, but its fixed multiplicative amplitude is far below the
source-split target scale. This must not be patched by post-hoc K1 rescaling.

The bounded-rho audit confirms that this cannot be repaired within the locked
rho budget. The best allowed value is the upper endpoint `rho=4`, and every row
would need `rho>4` for exact amplitude matching. The next branch is therefore a
target-scale/covariance investigation, not an operator rescue.

The first target-scale/covariance sensitivity is now complete. K2 improves over
K1 in all tested proxy cases, but it beats the best polynomial control only
when a 25 percent target-fraction error floor is imposed. This makes the next
question precise: the branch needs an independently justified response-scale or
covariance model before the K2 improvement can be interpreted more strongly.

A finer error-floor sweep now sharpens that threshold. K2 first becomes the
best AIC model at a target-fraction floor of 14 percent, and the same floor is
where it first beats the best polynomial control. This does not authorize
choosing a 14 percent floor after inspection; it identifies the response-scale
level that a future public covariance, systematic-floor, or cross-branch
scatter argument would have to justify independently.

The corresponding policy gate records that the current branch-scatter preflight
does exceed the 14 percent scale, but is not eligible as a benchmark covariance.
This is conditional strengthening only: the branch needs an independently
declared covariance, systematic floor, or reconstruction-family scatter rule.

The branch-scatter preflight benchmark now shows why this route matters:
with the SN/BAO branch split used as the response-scale covariance, locked K2
is the best AIC model in every tested branch-scatter covariance variant. The
result strengthens K2 conditionally while keeping the measurement gate below
validation level until the scatter model is independently promoted.

The promotion check now allows preflight-benchmark use of branch scatter, but
blocks measurement-validation promotion. The next route is therefore not more
K2 fitting; it is independent covariance/systematic-source registration.

The covariance-source registry now records that raw public SN and BAO covariance
files are available, while the transformed joint covariance is missing. This
makes the next task operational: propagate the public covariance into the
likelihood-native source-split vector or register an independent systematic /
reconstruction-family scatter source.

The first public covariance proxy has now been built. It uses raw Pantheon+ and
DESI covariance inputs, but remains a proxy because it assumes zero SN-BAO
cross-covariance and uses the current simplified source-split transform. Its
scorecard is mixed: K2 improves over K1, but polynomial controls remain
stronger. This makes covariance quality the next technical bottleneck.

The cross-covariance sensitivity audit keeps the same conclusion: within the
positive-definite row-aligned cross-covariance proxy range, K2 remains better
than K1/no-memory but does not beat the polynomial controls.

The route-level covariance scorecard now collects these covariance paths in one
place. It finds that K2 improves over K1/no-memory on every tested route, and
that the branch-scatter covariance variants make K2 competitive with polynomial
controls. The public covariance proxy and cross-covariance sensitivity routes
remain mixed. This makes the current support route-dependent: strong as a
branch-scatter preflight result, not yet strong as a public full-covariance
benchmark.

The covariance-gap audit then checks this row by row. It shows that K2 is not
losing to K1/no-memory on individual rows; K2 improves over K1 under both
public-proxy and branch-scatter diagonal decompositions. The unresolved issue is
that polynomial controls remain too competitive under the public covariance
proxy. The next branch should therefore improve the covariance transform or
register an independent scatter route, not alter the locked K2 operator.

The polynomial cross-validation audit adds a stability check for that unresolved
issue. The public-proxy leave-one-out split still favors the quadratic
polynomial, but public-proxy blocked validation favors K2. The branch-scatter
routes favor K2 in both validation modes. This makes the polynomial objection a
real warning, but not a stable shutdown of the K2 route.

The support ladder is the current compact reading of this branch. K2 is
supportive against K1/no-memory, mixed against polynomial controls, strongest
under branch-scatter preflight, and still blocked for measurement validation
because the public covariance route remains weaker.

The public covariance upgrade queue turns this into a concrete work list. The
next stronger scorecard must not be run as an exploratory rescue: it needs a
frozen covariance route, cross-covariance policy, K1 source, null comparator
set, coordinate mapping, and acceptance rule before execution.

The public-covariance locked rerun protocol now freezes those rules. It permits
no stronger current rerun, but separates the preferred full-public route from a
secondary registered branch-scatter route and a forbidden rescue route.

The covariance policy registry makes the current restriction explicit: the only
available route is cross-covariance sensitivity, not a benchmark policy. This
keeps the source-split branch in preflight mode until full public covariance or
registered shrinkage/scatter is available.

The registered-shrinkage template now provides the scaffold for one such route,
but leaves it non-executable until shrinkage parameters and cross-covariance
handling are declared before a rerun.

The registered-shrinkage parameter policy now declares those values for a future
preflight route. The source-split branch remains in preflight mode because the
route has not been activated for a new locked rerun.

The activation gate now allows that activation only as future preflight. It
does not authorize a current stronger scorecard and does not change the claim
boundary.

The registered-shrinkage future-preflight run keeps the result conservative:
K2 improves over K1/no-memory, but the quadratic polynomial control remains
preferred. This branch therefore still needs a stronger public benchmark route
or a principled reason why polynomial controls are not fair comparators.

The polynomial-control fairness audit resolves the last phrase more carefully:
polynomial controls are not fair physical nulls, but they are fair
overfit-risk controls. They remain mandatory blockers for stronger claims.

The physical null hierarchy now names the missing physical comparators:
backreaction-only and Dyer-Roeder/optical controls. These must be implemented on
the same source-split vector before the branch can support stronger public
claims.

The proxy templates now exist, but they are non-scoring. The next source-split
task is to freeze amplitude policies for those physical nulls.

Those amplitude policies are now frozen for preflight. The physical nulls can be
used as sanity / sensitivity controls, but not as measurement-calibrated nulls.
The allowed policies are unit-norm comparison and a bounded reported amplitude
grid; post-hoc free-amplitude rescue remains disallowed.

The physical-null preflight scorecard has now been run on the likelihood-native
source-split vector. On the branch-scatter preflight scale, locked K2 improves
over K1/no-memory and over the reported physical-null template controls. This is
a K2-supportive preflight result, not a measurement claim, because the physical
null amplitudes are not independently calibrated.

The row audit keeps this support disciplined. K2 improves over K1 in all rows,
but the best reported physical-null row is better than K2 in half of the rows.
The aggregate still favors K2 slightly, so the correct reading is supportive but
narrow preflight evidence.

The next source-split task is to find or build independent calibration inputs
for the physical-null amplitudes. Until then, physical nulls remain
sanity/sensitivity controls rather than measurement-grade alternatives.

The current task queue asks for a backreaction constraint table, an optical
alpha/clumpiness table, a source-split mapping policy, and covariance policy.
The mapping policy is now registered; source tables and covariance remain
missing.
The covariance policy is now registered as well; source-native covariance is the
preferred route, while diagonal/shrinkage proxies are preflight-only.
The dashboard condenses the open work to three blockers: ingest source data,
execute the mapping policy, and propagate source covariance.

The SN branch handoff now makes that first action row-level: all eight usable
coordinate-native target rows are ready in source-split standardized units, but
they have now been written to the real candidate export.

The BAO branch handoff now mirrors that status: all eight usable
coordinate-native target rows are ready in source-split standardized units, but
they have now been written to the real candidate export. The next step is still
not K2 scoring; the remaining work is to resolve the transform, K1, covariance,
and sign-family gates.

## Outcome Classes

Supportive:

- the locked K2 response is competitive with no-memory and optical/backreaction
  controls under the same source-split covariance;
- sign-stable rows remain non-violating;
- sign-unstable rows are consistently classified as warnings;
- no `rho > 4` rescue is required.

Weakening:

- K1/no-memory remains preferred under source-split covariance;
- K2 only improves broad sign-unstable rows;
- coordinate-native and likelihood-native mappings disagree strongly.

Strong negative:

- sign-stable source-split rows contradict the locked prediction;
- the comparison requires changing the kernel or using `rho > 4`;
- a registered null comparator explains the source-split target with lower
  complexity under the same covariance.

## Immediate Next Work

1. Export public reconstruction-family source-split responses and signs.
2. Run the same locked K2 and null comparator scorecard only after those gates
   are open.

Until those steps exist, this branch remains a readiness track and not a
measurement-validation result.
