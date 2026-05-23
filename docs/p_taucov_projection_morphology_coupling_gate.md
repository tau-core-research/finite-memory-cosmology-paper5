# P-TauCov Projection/Morphology Coupling Gate

Freeze ID: `P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_v1`

Status:

`P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_READY_NO_OBJECT_NO_SCORING`

## Purpose

The strict branch-only reduced-Jacobian candidate was clean but too simple: it
was diagonal, low-rank, and carried no explicit morphology/projection channel.
This gate freezes the next admissible route before any new object construction
or scoring.

## Frozen Inputs

- prior specificity preflight:
  [`p_taucov_reduced_jacobian_specificity_preflight.md`](p_taucov_reduced_jacobian_specificity_preflight.md)
- frozen morphology/projection convention:
  [`p_taucov_tccs_pmorph_piperp.md`](p_taucov_tccs_pmorph_piperp.md)
- frozen morphology basis:
  `evidence/p_taucov_p4_morphology_basis.csv`
- frozen full-action coordinate domain:
  `evidence/p_taucov_full_action_domain_coordinates.csv`

## Result

The next admissible candidate must include a target-blind projection/morphology
coupling, represented operationally as `D_P M_proj` or an equivalent frozen
projection derivative. It must not leak direct forbidden `M_parent` support into
the reduced object.

Minimum next-candidate gates:

- explicit `TEMPLATE_P_MORPH_PROJECTION` support;
- no direct `TEMPLATE_M_PARENT_MORPHOLOGY` leakage;
- non-diagonal support, with diagonal energy share not above `0.80`;
- nonzero commutator share with frozen `P_morph`;
- no target residuals, score outcomes, family gains, or P5C survival outcomes;
- scoring remains blocked until a new object-specific preflight passes.

## Claim Boundary

Allowed statement:

> The failed strict branch-only route has been converted into a stricter
> projection/morphology coupling requirement for any next Tau-side candidate.

Forbidden statement:

> This gate constructs a new `delta_C_Tau` object, authorizes scoring, or
> establishes a Tau-specific signal.
