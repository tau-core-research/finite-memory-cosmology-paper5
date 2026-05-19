# Public Target Convention Adjudication

Status: target convention adjudicated without using A2 score. Measurement validation remains closed.

## Decision

- Preferred preflight convention: `STANDARDIZED_SN_MINUS_BAO_COORDINATE_TARGET`
- Recommended next measurement candidate: `WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1`
- Current raw projected target: diagnostic only, not promoted.
- Locked A2 changes allowed: False.

## Conventions

### RAW_PROJECTED_SN_MINUS_BAO_CURRENT

- Class: raw_likelihood_projection_candidate
- Definition: y = L_SN*r_SN_raw - L_BAO*r_BAO_log
- Promotion status: DO_NOT_PROMOTE_TO_MEASUREMENT_TARGET
- Allowed use: rerun_candidate_diagnostic_only
- Score-independent justification: closest to current public residual projection, but branch units differ and sign/scale is convention-sensitive
- Known issue: projected/standardized sign mismatch rows=3; compressed rows=6
- Required next check: derive branch-unit normalization or replace with whitening target before interpretation

### STANDARDIZED_SN_MINUS_BAO_COORDINATE_TARGET

- Class: standardized_branch_contrast
- Definition: y = SN_standardized - BAO_standardized on the frozen coordinate-native grid
- Promotion status: PREFERRED_PREFLIGHT_CONVENTION_NOT_MEASUREMENT_TARGET
- Allowed use: preflight_target_convention
- Score-independent justification: puts SN and BAO branches on common dimensionless units and matches the source-split sign-family convention
- Known issue: not a full covariance-whitened likelihood target; remains preflight unless covariance-native transform is built
- Required next check: construct covariance-native whitening transform using the same branch convention

### RAW_PROJECTED_SIGN_ALIGNED_TO_STANDARDIZED

- Class: sign_alignment_counterfactual
- Definition: y = sign(y_standardized) * abs(L_SN*r_SN_raw - L_BAO*r_BAO_log)
- Promotion status: FORBIDDEN_AS_PRIMARY_TARGET
- Allowed use: counterfactual_diagnostic_only
- Score-independent justification: diagnoses sign-convention sensitivity only; sign is imposed from another target
- Known issue: uses target sign alignment and is therefore not admissible as a primary measurement convention
- Required next check: none for promotion; retain only as sensitivity check

### WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1

- Class: executable_covariance_proxy_preflight_target
- Definition: y = W_cov * [SN_standardized - BAO_standardized] with W_cov declared before scoring
- Promotion status: IMPLEMENTED_AS_PREFLIGHT_NOT_MEASUREMENT_TARGET
- Allowed use: implementation_target_for_next_locked_rerun
- Score-independent justification: retains common branch units while allowing public covariance to define the metric scale
- Known issue: SN-BAO cross-covariance is still set to zero and weighted polynomial controls remain strong
- Required next check: replace the zero cross-covariance policy with a declared public joint covariance or registered shrinkage route, then rerun K1/A2/nulls unchanged

### STANDARDIZED_SN_PLUS_BAO_SIGN_FLIP_CHECK

- Class: sign_flip_counterfactual
- Definition: y = SN_standardized + BAO_standardized
- Promotion status: FORBIDDEN_AS_PRIMARY_TARGET
- Allowed use: counterfactual_diagnostic_only
- Score-independent justification: tests opposite source-split orientation only
- Known issue: does not match the declared source-split contrast orientation
- Required next check: none for promotion; retain only as sign-orientation control

## Claim Boundary

This adjudication does not choose the target that makes A2 look best. It selects the next route by branch-unit consistency and covariance-native measurability.
