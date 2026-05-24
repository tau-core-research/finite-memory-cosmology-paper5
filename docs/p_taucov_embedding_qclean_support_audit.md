# P-TauCov Embedding Q-Clean Support Audit

Freeze ID: `P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_v1`

Status: `P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_BLOCKS_CURRENT_EMBEDDING_NO_SCORING`

## Purpose

This target-blind audit checks whether the current parent-to-score
embedding places the declared parent coordinates into the frozen common
clean subspace `Q_clean = Pi_bal Pi_perp Pi_bal`.

It does not inspect target residuals and does not authorize scoring.

## Top Coordinate Support

| Coordinate | Q-clean support ratio |
|---|---:|
| `TEMPLATE_P_MORPH_PROJECTION` | `0.08715747582432105` |
| `TEMPLATE_B_BRANCH_RESPONSE` | `6.914594610948657e-16` |
| `TEMPLATE_M_PARENT_MORPHOLOGY` | `5.347579709013353e-16` |
| `TEMPLATE_PHI_PARENT_SOURCE` | `3.2553021195279366e-16` |
| `TEMPLATE_COORD_ORIGIN_CENTER` | `0.0` |
| `TEMPLATE_COORD_SCALE_UNIT` | `0.0` |
| `TEMPLATE_EXT_SOURCE_FAMILY` | `0.0` |
| `TEMPLATE_EXT_OBSERVING_CONTEXT` | `0.0` |

## Top Pair-Difference Support

| Pair contrast | Q-clean support ratio |
|---|---:|
| `TEMPLATE_P_MORPH_PROJECTION` - `TEMPLATE_EXT_OBSERVING_CONTEXT` | `0.0871574758243211` |
| `TEMPLATE_P_MORPH_PROJECTION` - `TEMPLATE_EXT_SOURCE_FAMILY` | `0.0871574758243211` |
| `TEMPLATE_P_MORPH_PROJECTION` - `TEMPLATE_COORD_SCALE_UNIT` | `0.0871574758243211` |
| `TEMPLATE_P_MORPH_PROJECTION` - `TEMPLATE_COORD_ORIGIN_CENTER` | `0.0871574758243211` |
| `TEMPLATE_M_PARENT_MORPHOLOGY` - `TEMPLATE_P_MORPH_PROJECTION` | `0.06175616319193948` |
| `TEMPLATE_PHI_PARENT_SOURCE` - `TEMPLATE_P_MORPH_PROJECTION` | `0.0613249335223854` |
| `TEMPLATE_B_BRANCH_RESPONSE` - `TEMPLATE_P_MORPH_PROJECTION` | `0.06072883383277974` |
| `TEMPLATE_PHI_PARENT_SOURCE` - `TEMPLATE_M_PARENT_MORPHOLOGY` | `9.983663808624632e-16` |

## Key Interpretation

- best coordinate: `TEMPLATE_P_MORPH_PROJECTION` with support `0.08715747582432105`
- max branch-coordinate support: `6.914594610948657e-16`

The current embedding almost completely removes the active branch
coordinates from the common clean subspace. This explains why the
minimal Q-native branch-response curvature and older Hessian inventory
cannot pass the parent-domain curvature source requirement.

## Consequence

The next step is not a new empirical scorecard. The next step is a new
parent-domain embedding or domain metric in which active branch
curvature has intrinsic support inside the clean subspace before
projection cleaning is applied.

## Claim Boundary

Allowed statement:

> The current parent-to-score embedding lacks enough Q-clean support for active branch curvature.

Forbidden statement:

> This audit validates Tau Core, constructs a survivor, or authorizes empirical scoring.
