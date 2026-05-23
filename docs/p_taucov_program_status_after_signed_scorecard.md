# P-TauCov Program Status After Signed Scorecard

Status: protocol-success / candidate-failure / no Tau Core validation.

## Completed Gates

The P-TauCov program now has two fully executed, predeclared score branches and
one newer no-scoring structural branch:

1. Parent-action PSD covariance scorecard.
2. Branch-localized signed-response alignment scorecard.
3. TCCS parent-Hessian commutator / transfer-curvature preflight sequence.

The two score branches were frozen before scoring, authorized by manifests,
executed, validated, and interpreted with no survival claim. The TCCS branch
has not been scored; it is a pre-score structural audit.

## Results

| Route | Primary result | Status |
|---|---:|---|
| Parent-action PSD covariance | `-0.2996400323571766` | fail |
| Signed-response alignment | `31.70572026946584` | positive raw alignment, but fail |
| TCCS double-sided commutator | exact no-go | blocked before scoring |
| TCCS transfer-curvature | retained norm `0.0012660320646664862` | failed pre-score object gate |
| Cleaner domain compatibility | `7 / 7` gates | pass, no scoring |
| Common-clean-subspace support | `0 / 5` candidates pass | no scoring |
| Q-native parent-curvature gate | defined | no object, no scoring |
| Q-native route registry | four routes defined | no object, no scoring |
| Q-native route priority | branch-response curvature recommended | no object, no scoring |
| Minimal Q-native branch-response preflight | failed | no scoring |
| Q-range projector freeze | passed | no object, no scoring |
| Q-range branch-response retest | failed | no scoring |
| Reduced branch-Jacobian requirement | required | no object, no scoring |
| Reduced branch-Jacobian source spec | blocked by 4 source objects | no object, no scoring |
| Branch-equation completion audit | partial completion; mediated forcing required | no object, no scoring |
| Mediated parent-forcing chain | pass, stability open | no object, no scoring |
| Response/energy split | pass, full dynamical stability open | no scoring |
| Projected morphology derivative | strict-linear pass | no scoring |
| Reference-state reconciliation | operational reference frozen; physical stability open | no scoring |
| Dynamical-stability reconciliation | linear assembly-ready; nonlinear/UV open | no scoring |
| Reduced-Jacobian current blocker rollup | source-assembly blockers clear | no scoring |
| Reduced-Jacobian assembly | strict branch-only `delta_C_Tau` candidate assembled | no scoring |
| Reduced-Jacobian specificity preflight | strict branch-only candidate fails | no scoring |

The signed-response route failed because the diagonal signed control was much
larger and the family contribution was single-family dominated:

```text
RequiredNullMaxSignedS = 152.41444638165376
MaxPositiveFamilyShare = 0.998171886220409
```

The TCCS route sharpened the theory rather than producing a scoreable object.
The double-sided commutator is algebraically zero after exact complement
projection, and the no-go-corrected transfer-curvature object becomes too weak
and leaky after branch/perp cleaning. A follow-up cleaner audit shows that the
cleaners themselves are compatible, so the failure is now localized to the
candidate curvature object rather than to the branch/perp cleaner pair.
The common-clean-subspace support audit then checks the existing candidate
inventory and finds no scoreable object.

## Scientific Meaning

This is a useful negative result. It shows that the current minimal
parent-action/signed-response/TCCS constructions do not yet isolate a
Tau-specific empirical signal.

The program did not fail methodologically. The tested candidates failed
scientifically, and the TCCS failures identify a sharper theoretical
requirement: the next candidate must put parent curvature into the already
available common clean subspace.

## Current Best Claim

```text
P_TAUCOV_PROTOCOL_INFRASTRUCTURE_VALID_BUT_NO_SURVIVING_TAU_SPECIFIC_SIGNAL
```

Allowed:

- the protocol machinery is reproducible and disciplined;
- the tested minimal PSD and signed candidates are non-survivors;
- the TCCS route currently blocks scoring but motivates a common-clean-subspace refinement;
- future candidates must be more constrained before scoring.

Forbidden:

- Tau Core validation;
- covariance-survival claim;
- signed-response survival claim;
- TCCS survival claim;
- post-hoc rescue by diagonal or family-dominated diagnostics.

## Next Admissible Direction

The next route must remove diagonal, projection-leakage, and single-family
dominance at the model-design stage, before scoring. A valid next candidate
would need:

1. off-diagonal-only or diagonal-orthogonal signed support;
2. held-out branch-support rule;
3. family-balance constraint frozen before scoring;
4. non-negligible support in the common `Pi_bal Pi_perp Pi_bal` clean subspace;
5. the same null and aggregation discipline retained.

The current theory refinement is recorded in
[`p_taucov_domain_compatibility_refinement.md`](p_taucov_domain_compatibility_refinement.md).

The next no-scoring protocol gate is recorded in
[`p_taucov_common_clean_subspace_support_protocol.md`](p_taucov_common_clean_subspace_support_protocol.md).

The first support audit is recorded in
[`p_taucov_common_clean_subspace_support_audit.md`](p_taucov_common_clean_subspace_support_audit.md).

The next derivation gate is recorded in
[`p_taucov_q_native_parent_curvature_derivation_gate.md`](p_taucov_q_native_parent_curvature_derivation_gate.md).

The route registry is recorded in
[`p_taucov_q_native_route_registry.md`](p_taucov_q_native_route_registry.md).

The route priority note is recorded in
[`p_taucov_q_native_route_priority_note.md`](p_taucov_q_native_route_priority_note.md).

The minimal branch-response preflight is recorded in
[`p_taucov_q_native_branch_response_curvature_preflight.md`](p_taucov_q_native_branch_response_curvature_preflight.md).

The Q-range projector freeze is recorded in
[`p_taucov_q_range_projector_freeze.md`](p_taucov_q_range_projector_freeze.md).

The Q-range branch-response retest is recorded in
[`p_taucov_q_range_branch_response_preflight.md`](p_taucov_q_range_branch_response_preflight.md).

The reduced branch-Jacobian requirement is recorded in
[`p_taucov_reduced_branch_jacobian_requirement.md`](p_taucov_reduced_branch_jacobian_requirement.md).

The reduced branch-Jacobian source spec is recorded in
[`p_taucov_reduced_branch_jacobian_source_spec.md`](p_taucov_reduced_branch_jacobian_source_spec.md).

The blocker-resolution audit is recorded in
[`p_taucov_reduced_branch_jacobian_blocker_resolution.md`](p_taucov_reduced_branch_jacobian_blocker_resolution.md).

The next dependency-ordered gate is recorded in
[`p_taucov_reference_state_resolution_gate.md`](p_taucov_reference_state_resolution_gate.md).

The reference-state candidate spec is recorded in
[`p_taucov_reference_state_candidate_spec.md`](p_taucov_reference_state_candidate_spec.md).

The next branch-equation completion gate is recorded in
[`p_taucov_branch_equation_completion_gate.md`](p_taucov_branch_equation_completion_gate.md).

The first branch-equation completion audit is recorded in
[`p_taucov_branch_equation_completion_audit.md`](p_taucov_branch_equation_completion_audit.md).

The mediated parent-forcing chain audit is recorded in
[`p_taucov_mediated_parent_forcing_chain_audit.md`](p_taucov_mediated_parent_forcing_chain_audit.md).

The response/energy split packet is recorded in
[`p_taucov_response_energy_split_packet.md`](p_taucov_response_energy_split_packet.md).

The strict-linear projected morphology derivative audit is recorded in
[`p_taucov_projected_morphology_derivative_audit.md`](p_taucov_projected_morphology_derivative_audit.md).

The current reduced-Jacobian blocker rollup is recorded in
[`p_taucov_reduced_jacobian_current_blocker_rollup.md`](p_taucov_reduced_jacobian_current_blocker_rollup.md).

The reference-state status reconciliation is recorded in
[`p_taucov_reference_state_status_reconciliation.md`](p_taucov_reference_state_status_reconciliation.md).

The dynamical-stability reconciliation is recorded in
[`p_taucov_dynamical_stability_status_reconciliation.md`](p_taucov_dynamical_stability_status_reconciliation.md).

The first conservative reduced-Jacobian assembly is recorded in
[`p_taucov_reduced_jacobian_assembly.md`](p_taucov_reduced_jacobian_assembly.md).

The reduced-Jacobian specificity preflight is recorded in
[`p_taucov_reduced_jacobian_specificity_preflight.md`](p_taucov_reduced_jacobian_specificity_preflight.md).
