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
| Projection/morphology coupling gate | next admissible route frozen | no object, no scoring |
| `D_P M_proj` source spec | minimal active branch/projection derivative frozen | no object, no scoring |
| Projection-coupled Jacobian assembly | active projection channel included | no scoring |
| Projection-coupled specificity preflight | projection channel fixed, but diagonal/rank gates fail | no scoring |
| Active-triad PSD ceiling audit | current `Phi/B/P` PSD route structurally too narrow | no scoring |
| Parent-operator source expansion gate | broader non-outcome source space required | no object, no scoring |
| Expanded parent-operator domain packet | 5 active coordinates, 2 new non-outcome axes | no object, no scoring |
| Expanded parent-operator source packet | 5-axis role-declared source matrix frozen | no scoring |
| Expanded parent-operator PSD preflight | structural PSD specificity gates pass | no scoring |
| Expanded parent-operator scoring firewall | structural hashes ready, policy freezes missing | no scoring |
| Expanded parent-operator final manifest | primary scorecard authorized, no survival claim | scorecard authorized only |

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

The projection/morphology coupling gate is recorded in
[`p_taucov_projection_morphology_coupling_gate.md`](p_taucov_projection_morphology_coupling_gate.md).
It freezes the next admissible route after the strict branch-only failure:
future candidates must include target-blind projection/morphology coupling,
must avoid direct forbidden `M_parent` leakage, and must still pass an
object-specific preflight before any scoring.

The first `D_P M_proj` source spec is recorded in
[`p_taucov_d_p_mproj_source_spec.md`](p_taucov_d_p_mproj_source_spec.md).
It freezes a minimal symmetric active coupling between
`TEMPLATE_B_BRANCH_RESPONSE` and `TEMPLATE_P_MORPH_PROJECTION`; it is a source
derivative only, not a new covariance candidate.

The first projection-coupled Jacobian assembly is recorded in
[`p_taucov_projection_coupled_jacobian_assembly.md`](p_taucov_projection_coupled_jacobian_assembly.md).
It adds the frozen projection derivative to the reduced-Jacobian assembly.

The projection-coupled specificity preflight is recorded in
[`p_taucov_projection_coupled_specificity_preflight.md`](p_taucov_projection_coupled_specificity_preflight.md).
It shows that the projection channel is now present, but the PSD-lifted
candidate remains too diagonal-dominated and low-rank for scoring.

The active-triad PSD ceiling audit is recorded in
[`p_taucov_active_triad_psd_ceiling_audit.md`](p_taucov_active_triad_psd_ceiling_audit.md).
It shows that the current active `Phi/B/P` triad is structurally too narrow for
the PSD covariance route under the existing specificity gates. The next route
must either expand the target-blind parent-side operator source or open a
separately frozen signed-operator-contrast protocol.

The parent-operator source expansion gate is recorded in
[`p_taucov_parent_operator_source_expansion_gate.md`](p_taucov_parent_operator_source_expansion_gate.md).
It requires the next PSD route to declare at least five active reduced
coordinates and at least two new non-outcome axes from allowed source classes
before any new covariance object is assembled.

The expanded parent-operator domain packet is recorded in
[`p_taucov_expanded_parent_operator_domain_packet.md`](p_taucov_expanded_parent_operator_domain_packet.md).
It keeps the `Phi/B/P` core active and adds `TEMPLATE_COORD_SCALE_UNIT` plus
`TEMPLATE_EXT_OBSERVING_CONTEXT` as target-blind non-outcome axes. Direct
`M_PARENT_MORPHOLOGY` and `EXT_SOURCE_FAMILY` remain forbidden.

The expanded parent-operator source packet is recorded in
[`p_taucov_expanded_parent_operator_source_packet.md`](p_taucov_expanded_parent_operator_source_packet.md).
It freezes a role-declared five-axis source rule without target or score input.

The expanded parent-operator PSD preflight is recorded in
[`p_taucov_expanded_parent_operator_psd_preflight.md`](p_taucov_expanded_parent_operator_psd_preflight.md).
It passes the structural no-scoring PSD specificity gates that the active
`Phi/B/P` triad could not pass. This is still not empirical survival.

The expanded parent-operator scoring firewall is recorded in
[`p_taucov_expanded_parent_operator_scoring_firewall.md`](p_taucov_expanded_parent_operator_scoring_firewall.md).
It now validates 10/10 authorization items after the final manifest.

The expanded parent-operator final manifest is recorded in
[`p_taucov_expanded_parent_operator_final_manifest.md`](p_taucov_expanded_parent_operator_final_manifest.md).
It authorizes only the primary expanded covariance scorecard entrypoint. It
does not authorize survival language, null-survival language, measurement
validation, or a Tau Core validation claim.
