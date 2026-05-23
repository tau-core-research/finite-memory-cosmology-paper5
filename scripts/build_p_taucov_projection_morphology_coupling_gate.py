#!/usr/bin/env python3
"""Freeze the projection/morphology coupling gate for the next P-TauCov route."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

PREFLIGHT_SUMMARY = EVIDENCE / "p_taucov_reduced_jacobian_specificity_preflight_summary.csv"
PMORPH_SUMMARY = EVIDENCE / "p_taucov_tccs_pmorph_piperp_summary.csv"
MORPH_BASIS = EVIDENCE / "p_taucov_p4_morphology_basis.csv"
DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"

OUT = EVIDENCE / "p_taucov_projection_morphology_coupling_gate.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_projection_morphology_coupling_gate_summary.csv"
DOC = DOCS / "p_taucov_projection_morphology_coupling_gate.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_v1"
CLAIM_BOUNDARY = "projection_morphology_coupling_gate_no_scoring"


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    preflight = pd.read_csv(PREFLIGHT_SUMMARY).iloc[0]
    pmorph = pd.read_csv(PMORPH_SUMMARY).iloc[0]
    morph_basis = pd.read_csv(MORPH_BASIS)
    domain = pd.read_csv(DOMAIN)

    reduced = set(domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
    active_projection_present = "TEMPLATE_P_MORPH_PROJECTION" in reduced
    parent_morphology_forbidden = bool(
        domain.loc[
            domain["CoordinateID"].eq("TEMPLATE_M_PARENT_MORPHOLOGY"),
            "EmbeddingRole",
        ].eq("forbidden").any()
    )
    has_mp_coupling = bool(morph_basis["BasisID"].eq("M_P_SYMMETRIC_COUPLING").any())
    strict_failed = str(preflight["Status"]) == "P_TAUCOV_REDUCED_JACOBIAN_SPECIFICITY_PREFLIGHT_FAIL_NO_SCORING"
    pmorph_frozen = str(pmorph["Status"]) == "P_TAUCOV_TCCS_PMORPH_PIPERP_FROZEN_NO_OBJECT_NO_SCORING"

    requirements = [
        (
            "PMC-G1_PRIOR_PREFLIGHT_FAILED_BEFORE_SCORING",
            strict_failed,
            "the strict branch-only candidate was rejected before scoring",
        ),
        (
            "PMC-G2_PMORPH_CONVENTION_FROZEN",
            pmorph_frozen,
            "target-blind P_morph and Pi_perp conventions exist",
        ),
        (
            "PMC-G3_MORPHOLOGY_BASIS_HAS_MP_COUPLING",
            has_mp_coupling,
            "the frozen morphology basis includes an M/P symmetric coupling axis",
        ),
        (
            "PMC-G4_ACTIVE_PROJECTION_COORDINATE_AVAILABLE",
            active_projection_present,
            "the reduced domain includes TEMPLATE_P_MORPH_PROJECTION",
        ),
        (
            "PMC-G5_PARENT_MORPHOLOGY_REMAINS_FORBIDDEN",
            parent_morphology_forbidden,
            "the new route must use projection readout, not direct forbidden M_parent leakage",
        ),
        (
            "PMC-G6_NEXT_CANDIDATE_MUST_INCLUDE_D_P_MPROJ",
            True,
            "a next assembly must declare a target-blind D_P M_proj or equivalent projection derivative",
        ),
        (
            "PMC-G7_NEXT_CANDIDATE_MUST_BE_NONDIAGONAL",
            True,
            "a next candidate must fail closed if diagonal energy share exceeds 0.80",
        ),
        (
            "PMC-G8_NEXT_CANDIDATE_MUST_BE_NONCOMMUTING_WITH_PMORPH",
            True,
            "a next candidate must carry nonzero commutator share with the frozen P_morph convention",
        ),
        (
            "PMC-G9_NO_SCORE_OR_TARGET_ACCESS",
            True,
            "this gate uses only frozen domain, basis, and no-score preflight artifacts",
        ),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "Requirement": requirement,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, requirement in requirements
        ]
    )
    table.to_csv(OUT, index=False)

    status = (
        "P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_READY_NO_OBJECT_NO_SCORING"
        if bool(table["Passed"].all())
        else "P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_BLOCKED_NO_SCORING"
    )
    failed = ";".join(table.loc[~table["Passed"].astype(bool), "GateID"].astype(str))
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(table["Passed"].sum()),
                "GatesTotal": len(table),
                "FailedGates": failed,
                "PriorStrictCandidateStatus": str(preflight["Status"]),
                "PmorhConventionStatus": str(pmorph["Status"]),
                "ActiveProjectionCoordinateAvailable": active_projection_present,
                "ParentMorphologyForbidden": parent_morphology_forbidden,
                "MorphologyBasisHasMPCoupling": has_mp_coupling,
                "RequiredNextDerivative": "D_P_M_proj_or_equivalent_projection_morphology_coupling",
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Projection/Morphology Coupling Gate

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

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
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
