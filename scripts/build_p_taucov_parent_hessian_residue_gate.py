#!/usr/bin/env python3
"""Build the no-score parent-Hessian residue gate for the next P-TauCov route."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

EXPANDED_FAILURE = EVIDENCE / "p_taucov_expanded_parent_operator_failure_analysis_summary.csv"
COMMUTATOR_SUMMARY = EVIDENCE / "p_taucov_parent_hessian_commutator_summary.csv"

OUT = EVIDENCE / "p_taucov_parent_hessian_residue_gate.csv"
SUMMARY = EVIDENCE / "p_taucov_parent_hessian_residue_gate_summary.csv"
DOC = DOCS / "p_taucov_parent_hessian_residue_gate.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
GATE_ID = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_GATE_v1"
STATUS = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_GATE_DEFINED_NO_OBJECT_NO_SCORING"
CLAIM_BOUNDARY = "parent_hessian_residue_gate_no_object_no_scoring"


def read_optional(path: Path) -> pd.Series | None:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    return df.iloc[0]


def main() -> int:
    EVIDENCE.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    expanded = read_optional(EXPANDED_FAILURE)
    comm = read_optional(COMMUTATOR_SUMMARY)

    expanded_status = "" if expanded is None else str(expanded["Status"])
    comm_status = "" if comm is None else str(comm["Status"])
    smooth_failure = expanded is not None and float(expanded["PrimaryMinusStrongestNull"]) < 0.0
    projection_failure = comm is not None and float(comm["ProjectionNullAbsCorrelation"]) >= 0.60

    gates = [
        {
            "GateID": "PHR-G1_PARENT_HESSIAN_RESIDUE_DECLARED",
            "Requirement": "candidate must declare a parent-Hessian residue, not only a PSD covariance envelope",
            "FrozenThreshold": "required",
            "Reason": "expanded object improved covariance but remained generic-smooth-PSD reproducible",
        },
        {
            "GateID": "PHR-G2_SMOOTH_PSD_EXCLUSION",
            "Requirement": "smooth_psd_projection_overlap must be below a frozen threshold before scoring",
            "FrozenThreshold": "<=0.50 recommended; exact threshold must be frozen in candidate packet",
            "Reason": "GENERIC_RANDOM_SMOOTH_PSD beat the expanded primary object",
        },
        {
            "GateID": "PHR-G3_PROJECTION_NULL_EXCLUSION",
            "Requirement": "projection-null absolute correlation must be below the frozen threshold",
            "FrozenThreshold": "<0.60",
            "Reason": "previous parent-Hessian commutator object failed projection-null specificity",
        },
        {
            "GateID": "PHR-G4_SPECTRAL_RESIDUE_LOCALITY",
            "Requirement": "candidate must declare a compact spectral band, residue rank, or non-smooth mode support",
            "FrozenThreshold": "required",
            "Reason": "generic smooth covariance can mimic broad smooth envelopes",
        },
        {
            "GateID": "PHR-G5_PARENT_ORIENTATION_ANCHOR",
            "Requirement": "if signed/oriented information is used, orientation must come from a target-blind parent anchor",
            "FrozenThreshold": "required_if_oriented",
            "Reason": "sign choice cannot be selected after observing score outcomes",
        },
        {
            "GateID": "PHR-G6_BALANCED_SUPPORT_RETENTION",
            "Requirement": "candidate must retain nonzero structure after family, clock, and context balancing",
            "FrozenThreshold": "balanced_retained_norm > 0 and max block share <= frozen cap",
            "Reason": "expanded scorecard failed dominance and alpha-stability gates",
        },
        {
            "GateID": "PHR-G7_NO_TARGET_OR_SCORE_INPUTS",
            "Requirement": "construction and threshold selection must not use target residuals, scores, alpha behavior, or winner/loser null outcomes beyond documented failure classes",
            "FrozenThreshold": "required",
            "Reason": "next candidate must be theory-gated, not score-rescued",
        },
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "GatePacketID": GATE_ID,
                **gate,
                "RequiredBeforeScoring": True,
                "ScoringAuthorizedByGate": False,
                "SurvivalClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate in gates
        ]
    )
    table.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "GatePacketID": GATE_ID,
                "Status": STATUS,
                "GatesDefined": len(gates),
                "ExpandedFailureStatus": expanded_status,
                "CommutatorFailureStatus": comm_status,
                "ExpandedSmoothPSDFailureObserved": bool(smooth_failure),
                "CommutatorProjectionNullFailureObserved": bool(projection_failure),
                "NextAllowedArtifact": "p_taucov_parent_hessian_residue_candidate_v1_no_score_preflight",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Hessian Residue Gate",
                "",
                f"Status: `{STATUS}`",
                "",
                "This is a no-score gate packet. It does not define a new empirical",
                "scorecard and does not rescue any failed candidate.",
                "",
                "## Inputs From Previous Failures",
                "",
                f"- expanded parent-operator failure: `{expanded_status}`",
                f"- parent-Hessian commutator status: `{comm_status}`",
                f"- smooth PSD failure observed: `{smooth_failure}`",
                f"- projection-null failure observed: `{projection_failure}`",
                "",
                "The two failure modes are different and both matter:",
                "",
                "1. the expanded parent-operator object was too reproducible by a generic",
                "   smooth PSD covariance null;",
                "2. the previous parent-Hessian commutator object was close enough to the",
                "   projection-null direction to fail specificity.",
                "",
                "## Gate Definition",
                "",
                "A future candidate may approach empirical scoring only if it first declares",
                "a target-blind parent-Hessian residue satisfying all gate rows in",
                "`evidence/p_taucov_parent_hessian_residue_gate.csv`.",
                "",
                "The intended object class is not another smooth covariance shape. It is a",
                "parent-Hessian residue with non-smooth or spectrally localized structure,",
                "projection-null exclusion, smooth-PSD exclusion, and balanced support",
                "retention.",
                "",
                "## Forbidden Claim",
                "",
                "> The expanded P-TauCov object found a Tau Core signal.",
                "",
                "## Allowed Claim",
                "",
                "> The failed scorecards identify the next required Tau-specific gate: a",
                "> parent-Hessian residue that is not representable as generic smooth PSD",
                "> covariance and does not leak into projection-null structure.",
                "",
                "## Next Allowed Artifact",
                "",
                "`p_taucov_parent_hessian_residue_candidate_v1_no_score_preflight`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
