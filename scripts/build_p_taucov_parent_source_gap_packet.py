#!/usr/bin/env python3
"""Build the P-TauCov parent-source gap packet after residue collapse."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

RESIDUE = EVIDENCE / "p_taucov_parent_hessian_residue_candidate_summary.csv"
EXPANDED = EVIDENCE / "p_taucov_expanded_parent_operator_scorecard_summary.csv"
COMM = EVIDENCE / "p_taucov_parent_hessian_commutator_summary.csv"

OUT = EVIDENCE / "p_taucov_parent_source_gap_packet.csv"
SUMMARY = EVIDENCE / "p_taucov_parent_source_gap_packet_summary.csv"
DOC = DOCS / "p_taucov_parent_source_gap_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_PARENT_SOURCE_GAP_PACKET_v1"
STATUS = "P_TAUCOV_PARENT_SOURCE_GAP_IDENTIFIED_NO_SCORING"
CLAIM_BOUNDARY = "parent_source_gap_packet_no_object_no_scoring"


def row(path: Path) -> pd.Series | None:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    return df.iloc[0]


def main() -> int:
    residue = row(RESIDUE)
    expanded = row(EXPANDED)
    comm = row(COMM)

    residue_norm = float(residue["CandidateNormBeforeNormalization"]) if residue is not None else float("nan")
    expanded_margin = (
        float(expanded["PrimaryOOSDeltaNLL_BaselineMinusKernel"])
        - float(expanded["StrongestNullPrimaryOOSDeltaNLL"])
        if expanded is not None
        else float("nan")
    )
    projection_corr = float(comm["ProjectionNullAbsCorrelation"]) if comm is not None else float("nan")

    gap_rows = [
        {
            "GapID": "SG1_NO_NONZERO_RESIDUE_AFTER_CLEANING",
            "ObservedValue": residue_norm,
            "Interpretation": "current commutator-derived source collapses under smooth/projection/balance cleaning",
            "RequiredResolution": "derive a source with intrinsic non-smooth parent-Hessian support before bridge projection",
        },
        {
            "GapID": "SG2_SMOOTH_PSD_COMPETITOR_STRONGER",
            "ObservedValue": expanded_margin,
            "Interpretation": "expanded covariance object is still too generic-smooth",
            "RequiredResolution": "source must include a spectral or operator residue not representable by smooth PSD covariance",
        },
        {
            "GapID": "SG3_PROJECTION_NULL_LEAKAGE_IN_COMMUTATOR_ROUTE",
            "ObservedValue": projection_corr,
            "Interpretation": "previous commutator route was still too projection-null aligned",
            "RequiredResolution": "source must be defined in a projection-orthogonal parent domain before empirical embedding",
        },
        {
            "GapID": "SG4_MISSING_MICROSCOPIC_SOURCE_SELECTOR",
            "ObservedValue": 0.0,
            "Interpretation": "current source is a toy operator recipe, not selected by a microscopic action or compact spectrum",
            "RequiredResolution": "derive allowed residue modes from parent action, compact spectrum, boundary/domain condition, or index residue",
        },
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                **gap,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gap in gap_rows
        ]
    )
    table.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "Status": STATUS,
                "GapCount": len(gap_rows),
                "ResidueCandidateStatus": "" if residue is None else str(residue["Status"]),
                "ResidueNormBeforeNormalization": residue_norm,
                "ExpandedPrimaryMinusStrongestNull": expanded_margin,
                "CommutatorProjectionNullAbsCorrelation": projection_corr,
                "NextAllowedArtifact": "p_taucov_microscopic_residue_source_spec_v1_no_score",
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
                "# P-TauCov Parent-Source Gap Packet",
                "",
                f"Status: `{STATUS}`",
                "",
                "This packet records why the current P-TauCov source route must stop",
                "before any new empirical scorecard.",
                "",
                "## Key Diagnosis",
                "",
                f"- residue candidate status: `{summary.iloc[0]['ResidueCandidateStatus']}`",
                f"- residue norm after required cleaning: `{residue_norm}`",
                f"- expanded primary minus strongest null: `{expanded_margin}`",
                f"- previous commutator projection-null correlation: `{projection_corr}`",
                "",
                "The problem is no longer just empirical scoring. The problem is source",
                "selection. The current parent-side recipes can create positive covariance",
                "gain, but when forced to be non-smooth, projection-clean, and balanced,",
                "the available residue vanishes.",
                "",
                "## Consequence",
                "",
                "The next object must be derived upstream of the empirical bridge. It must",
                "come from a microscopic parent source selector: a compact spectrum,",
                "boundary/domain condition, index residue, or parent-action Hessian mode",
                "selection rule.",
                "",
                "## Next Allowed Artifact",
                "",
                "`p_taucov_microscopic_residue_source_spec_v1_no_score`",
                "",
                "Forbidden: building another empirical covariance kernel before this source",
                "selector exists.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
