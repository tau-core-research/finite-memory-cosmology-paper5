# Public Benchmark Plan

Status: Phase II preflight.

The current MVP is an operational diagnostic benchmark. It is not a public
covariance-aware measurement validation. This plan lists what must be added
before stronger empirical language is considered.

## Required BAO-Only Products

- BAO-only diagnostic vector or reconstruction grid.
- Redshift or likelihood-native coordinate for each diagnostic point.
- Public covariance matrix or enough information for a declared
  shrinkage-covariance prescription.
- Documentation of how the diagnostic vector is transformed into the K2
  comparison space.

Current candidate products are DESI DR2 and DR1 Gaussian BAO mean/covariance
files from the Cobaya `bao_data` repository. They are available locally for
preflight validation, but they are not yet transformed into the finite-memory
diagnostic benchmark space.

The raw public-observable preflight table currently standardizes the DESI rows
with redshift, observable type, diagonal covariance scale, and audit coordinate
columns. These rows remain marked `RAW_OBSERVABLE_NOT_K2_DIAGNOSTIC` until a
registered finite-memory diagnostic transform is defined.

The transform contract is maintained in
`docs/diagnostic_transform_contract.md` and
`evidence/diagnostic_transform_registry.csv`. Under the current registry no
transform is allowed for measurement-gate scoring yet. `T0` is input preflight
only, while `T1_BAO_DISTANCE_RATIO_RESIDUAL` is now available as a BAO
log-residual preflight transform with propagated covariance. It is still
blocked from measurement-gate scoring until a likelihood-native baseline,
coordinate-native K1 export, and null benchmark exist.

The first T1 null benchmark has been run as a preflight. A constant-offset
control is preferred under the current audit-fiducial baseline, indicating that
the baseline choice itself dominates this residual layer. This weakens any
attempt to use T1 directly for a locked K2 comparison and motivates a
likelihood-native BAO baseline export as the next technical step.

The offset diagnosis maps this constant mode to an approximately 1.5 percent
BAO scale difference, equivalent to moving the audit `rd=147.0 Mpc` baseline to
about `rd=144.8 Mpc`. This remains a baseline calibration issue, not a
finite-memory measurement.

The BAO baseline export readiness check currently finds no measurement-gate
eligible baseline. The only available baseline is the audit preflight baseline;
the required likelihood-native and coordinate-native exports are still missing.

A same-data `rd` offset sensitivity check confirms that the dominant T1
residual mode can be absorbed as a BAO scale calibration. Because that
calibration is learned from the tested data vector, it is retained only as a
diagnostic sensitivity check.

The likelihood-native source-readiness check adds one more boundary: the Cobaya
DESI files are public mean/covariance inputs, not baseline predictions. A fair
BAO baseline export still requires either a public best-fit/chain source or a
reproducible Cobaya/CAMB/CLASS model evaluation with frozen parameters.

The official DESI DR2 `iminuit/base/desi-bao-all` best-fit source is now
ingested as a public baseline-export preflight. It is useful for validating the
BAO evaluator because the recomputed chi2 is close to the reported DESI BAO
chi2. It remains blocked from K2 measurement scoring because it is optimized on
the same DESI BAO data.

A CMB-only best-fit baseline has also been exported. It is more independent of
the DESI BAO vector, but gives a higher BAO chi2 than the same-data DESI
best-fit baseline. This provides a useful bracket for future K2 protocol design:
same-data baselines are too permissive, while CMB-only baselines are more
independent but already carry BAO tension.

The BAO baseline selection policy now freezes this interpretation before any K2
scoring. Same-data baselines may appear only as sensitivity controls, at least
one independent baseline must be reported, and K2 must use the same residual
covariance as the null comparators with `p=3` and `rho<=4`.

The remaining BAO blocker is not data access or baseline scoring. It is the
absence of a locked K1/no-memory response target in the BAO log-residual space.
Until that amplitude target is frozen, K2 scoring remains precluded by policy.

The locked-response plan identifies a possible CMB-only unit-covariance-norm
candidate, but it is not yet selected and has no null scorecard. The public
benchmark therefore remains in preflight mode.

After adding the null scorecard, the CMB-only unit-covariance-norm candidate
remains weak: the zero-response null is AIC-preferred. This keeps the BAO branch
from becoming a K2 measurement gate.

## Required SN+BAO Products

- SN+BAO diagnostic vector or reconstruction grid.
- Source-split metadata sufficient to reproduce sign-stability checks.
- Public covariance matrix or declared shrinkage-covariance prescription.
- Clear distinction between reconstruction-stable and reconstruction-sensitive
  points.

Current SN candidate input is the Pantheon+SH0ES distance and covariance
release. It is available locally for preflight validation. This is not yet a
SN+BAO diagnostic vector; a transform into the finite-memory benchmark space is
still required.

The Pantheon+ rows are likewise standardized as raw SN distance observables.
They are useful for input validation and coordinate preflight only; they do not
yet constitute a SN+BAO finite-memory benchmark.

## Required Covariance Matrices

The benchmark requires either:

- a public full covariance matrix; or
- a declared shrinkage-covariance recipe with reproducible parameters.

The current diagonal, nearest-neighbor, exponential, and constant-off-diagonal
covariance proxies are MVP sensitivity checks only.

The public-covariance upgrade queue now records the exact next blockers after
the support-ladder audit: a full likelihood-native covariance transform or
registered shrinkage/scatter route, a fixed SN-BAO cross-covariance policy, and
a locked rerun protocol. The current public covariance proxy is available but
not strong enough for measurement validation.

The locked rerun protocol is now available as a preregistration artifact. It
does not authorize a stronger rerun; it prevents post-hoc route selection by
declaring the preferred public route, secondary branch-scatter route, and
forbidden rescue route before the next scorecard.

The covariance policy registry now separates public full covariance, registered
shrinkage, cross-covariance sensitivity, registered branch scatter, and forbidden
tuned routes. At present only the sensitivity route is available, so the public
benchmark remains below stronger interpretation.

The registered-shrinkage rerun template specifies what must be frozen if the
project chooses a shrinkage proxy instead of waiting for full public covariance.
The template is not executable yet because the shrinkage parameters and
cross-covariance policy are still unregistered.

The registered-shrinkage parameter policy now fills that template for future
preflight use. It does not run a scorecard and does not replace the preferred
full public covariance route.

The activation gate permits that route only as future preflight. Measurement
validation still requires resolving polynomial-control competitiveness under a
public covariance route and obtaining a full public measurement path.

The registered-shrinkage future-preflight run confirms that warning. The route
keeps K2 above K1/no-memory but does not beat the quadratic polynomial control.
The next public benchmark work must therefore address the polynomial-control
issue directly, not only the covariance proxy.

The polynomial-control fairness audit classifies this issue as mandatory
overfit-risk blocking. A polynomial control is not a physical cosmological null,
but its success under public-proxy routes prevents stronger public claims.

The physical null hierarchy adds the next requirement: backreaction-only and
Dyer-Roeder/optical controls must be implemented on the same source-split vector
before stronger public interpretation.

The first implementation step is complete as non-scoring templates. These
templates still need predeclared amplitude policies before they can enter a
scorecard.

Those amplitude policies now exist for preflight only. Stronger public
interpretation still requires physical amplitude calibration or a public
reconstruction source for the physical nulls.

The registered policy allows only unit-norm sanity comparison and a bounded
reported sensitivity grid. It does not allow a best-amplitude physical null to
be selected after seeing the K2 scorecard.

The first physical-null scorecard is therefore only a preflight sanity check.
It currently favors locked K2 over K1/no-memory and the reported physical-null
templates on the branch-scatter scale, but stronger public interpretation still
requires calibrated physical-null amplitudes and a public covariance route.

The row-level check shows why this cannot be overread: K2 beats K1 on every row,
but only splits evenly against the best reported physical-null row. Public
benchmarking still needs calibrated physical nulls.

The public benchmark input list therefore now includes two physical-null
calibration products: a backreaction reconstruction/envelope or simulation-prior
amplitude, and an optical clumpiness / Dyer-Roeder amplitude with covariance.
Neither may be chosen from the same residual scorecard.

The corresponding source registry is still empty at data level: candidate
classes are declared, but no public physical-null source has yet been ingested,
mapped, and attached to covariance.

The mapping policy is already fixed. Future public physical-null products must
cover the target redshift range or be rejected; extrapolation is not allowed.

The covariance policy is also fixed. A public physical-null calibration product
must provide uncertainty or covariance, or it remains a preflight sensitivity
input rather than a measurement comparator.

The dashboard view keeps the public benchmark requirement simple: the physical
null branch needs a real source table, a completed mapping to the source-split
vector, and propagated covariance before it can be used as a measurement
comparator.

The first candidate list includes backreaction constraints, Dyer-Roeder
smoothness-parameter constraints, and weak-lensing/optical mapping references.
These are acquisition targets, not benchmark inputs yet.

The acquisition triage recommends starting with the Koksbang backreaction
constraint paper, then the two Dyer-Roeder smoothness-parameter constraint
papers. Method references remain secondary until a compatible amplitude source
is selected.

The first source-package probe now confirms that those three acquisition
targets have extractability routes: one data-like backreaction route and two
TeX/table-marker optical routes. This improves acquisition readiness, but no
physical-null values are ingested, mapped, or covariance-ready yet.

The provisional extraction manifest refines this: the apparent Koksbang
data-like route is package metadata rather than a source-native numeric
constraint table, while the two Dyer-Roeder sources provide provisional
smoothness-parameter candidates. All extracted rows remain blocked for benchmark
use until mapping and covariance are attached.

The mapping-readiness audit finds two joint Dyer-Roeder smoothness rows with
full source-split redshift coverage, but no row has a declared
physical-to-source-split transform or covariance propagation. The mapping task
queue therefore starts with the joint optical `alpha` route while keeping the
backreaction route numeric-extraction blocked.

The first optical transform contract now provides a non-scoring preview:
`response_i=(1-alpha)*unit_norm(centered[x^2])`. This improves the plumbing for
future physical-null controls, but it remains outside measurement scoring until
sign convention and covariance propagation are registered.

The sign-convention audit is deliberately unresolved. Inverted signs match more
rows overall, while the as-declared sign matches more sign-stable rows. The
public benchmark must therefore freeze the optical sign convention from external
physical reasoning rather than selecting it from benchmark performance.

The alpha covariance preview now provides diagonal and fixed exponential
correlation matrices as plumbing checks. These are not measurement covariance
products. A public benchmark still needs source-native covariance or a declared
propagation route that is frozen before comparison.

The alpha scoring guard keeps the public benchmark closed: two alpha candidates
have transform, sign-audit, and covariance-preview artifacts, but none has an
externally frozen sign convention or source-native covariance.

## Coordinate-Native Mapping

The Phase II benchmark must freeze at least one of:

- likelihood-native coordinate;
- comoving-distance normalized coordinate;
- optical-depth-like coordinate with declared weights.

The current `x=z/z_max` mapping remains an operational diagnostic coordinate,
not a physical final coordinate.

## Registered Null Comparators

The public benchmark should compare the locked prediction against:

- `LCDM_NO_MEMORY`;
- `GENERIC_POLYNOMIAL_SMOOTHING`;
- `BACKREACTION_ONLY`;
- `DYER_ROEDER_OPTICAL`;
- `RECONSTRUCTION_ARTIFACT`;
- `SIGN_RANDOMIZED_CONTROL`;
- `COORDINATE_REMAP_CONTROL`.

## Outcome Conditions

Supportive:

- locked K2 is competitive against fair nulls under covariance-aware scoring;
- coordinate-native mappings do not create sign-stable contradictions;
- the result does not require `rho > 4` or kernel changes.

Weakening:

- no-memory or smooth nulls remain better under public covariance;
- K2 is competitive only under one coordinate choice;
- K2 requires bounded grid selection rather than fixed locked prediction.

Failure:

- compatibility requires `rho > 4`;
- kernel changes are required after seeing the benchmark;
- sign-stable public points contradict the locked prediction;
- public covariance rejects the locked prediction while null comparators remain
  viable.
