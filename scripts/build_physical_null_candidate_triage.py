#!/usr/bin/env python3
"""Triage public physical-null source candidates for acquisition priority."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

CANDIDATES = EVIDENCE / "physical_null_public_source_candidates.csv"
OUT = EVIDENCE / "physical_null_candidate_triage.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_candidate_triage_summary.csv"


TRIAGE = {
    "PNC_BACKREACTION_KOKSBANG_2604_11249": {
        "TriageRole": "primary_backreaction_candidate",
        "ExtractionPriority": 1,
        "ObservedNumericConstraintInAbstract": False,
        "MachineReadableExpectation": "TeX/PDF extraction likely required; arXiv source exists",
        "PotentialUse": "backreaction envelope over redshift if constraints can be digitized or source tables found",
        "ImmediateAction": "inspect TeX source and figures for redshift-binned backreaction constraints",
    },
    "PNC_BACKREACTION_HEINESEN_CLIFTON_2604_07244": {
        "TriageRole": "method_mapping_reference",
        "ExtractionPriority": 4,
        "ObservedNumericConstraintInAbstract": False,
        "MachineReadableExpectation": "method note; not direct amplitude source",
        "PotentialUse": "classification of optical-property versus expansion/backreaction deviations",
        "ImmediateAction": "use as mapping/interpretation reference, not first amplitude-ingest target",
    },
    "PNC_DYER_ROEDER_SNE_GRB_1303_1574": {
        "TriageRole": "primary_optical_candidate",
        "ExtractionPriority": 2,
        "ObservedNumericConstraintInAbstract": True,
        "MachineReadableExpectation": "abstract gives alpha constraints; table/source check still required",
        "PotentialUse": "constant smoothness-parameter prior for Dyer-Roeder optical amplitude",
        "ImmediateAction": "extract alpha best fits and uncertainties; decide whether constant-alpha prior can map to source-split rows",
    },
    "PNC_DYER_ROEDER_SMOOTHNESS_DD_1305_6989": {
        "TriageRole": "secondary_optical_candidate",
        "ExtractionPriority": 3,
        "ObservedNumericConstraintInAbstract": True,
        "MachineReadableExpectation": "abstract gives alpha constraint; source/table check still required",
        "PotentialUse": "constant smoothness-parameter prior and DD consistency check",
        "ImmediateAction": "extract alpha=0.92 constraint and uncertainty; check if it can serve as conservative optical prior",
    },
    "PNC_WEAK_LENSING_DYER_ROEDER_IPAC_1999": {
        "TriageRole": "optical_mapping_reference",
        "ExtractionPriority": 5,
        "ObservedNumericConstraintInAbstract": False,
        "MachineReadableExpectation": "method reference",
        "PotentialUse": "mapping from weak-lensing magnification to generalized Dyer-Roeder smoothness",
        "ImmediateAction": "retain for transform design if lensing/convergence source is selected",
    },
    "PNC_REDUCED_CONVERGENCE_SMOOTHNESS_IPAC_2005": {
        "TriageRole": "optical_mapping_reference",
        "ExtractionPriority": 6,
        "ObservedNumericConstraintInAbstract": False,
        "MachineReadableExpectation": "method reference",
        "PotentialUse": "mapping between reduced convergence and local smoothness parameter",
        "ImmediateAction": "retain for transform design if convergence source is selected",
    },
}


def main() -> None:
    candidates = pd.read_csv(CANDIDATES)
    rows = []
    for _, row in candidates.iterrows():
        triage = TRIAGE[str(row["CandidateID"])]
        rows.append(
            {
                **row.to_dict(),
                **triage,
                "CanBeFirstIngestTarget": triage["ExtractionPriority"] in {1, 2, 3},
                "CanBeMeasurementInputNow": False,
                "MissingBeforeIngest": "paper_source_or_tables;row_mapping;covariance_or_uncertainty",
                "ClaimBoundary": "physical_null_candidate_triage_no_measurement_validation",
            }
        )
    output = pd.DataFrame(rows).sort_values("ExtractionPriority")
    output.to_csv(OUT, index=False)

    first_targets = output[output["CanBeFirstIngestTarget"].astype(bool)]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_CANDIDATE_TRIAGE_SUMMARY",
                "CandidatesTriaged": int(len(output)),
                "FirstIngestTargets": int(len(first_targets)),
                "BackreactionFirstTargets": int(
                    first_targets["NullID"].str.contains("BACKREACTION_ONLY").sum()
                ),
                "OpticalFirstTargets": int(first_targets["NullID"].str.contains("DYER_ROEDER_OPTICAL").sum()),
                "DirectNumericConstraintCandidates": int(output["ObservedNumericConstraintInAbstract"].sum()),
                "MethodReferenceCandidates": int(output["TriageRole"].str.contains("reference").sum()),
                "MeasurementInputsReadyNow": 0,
                "RecommendedNextCandidate": str(output.iloc[0]["CandidateID"]),
                "PrimaryBlockingIssue": "candidate_constraints_not_extracted_or_mapped",
                "NextAction": "inspect first-ingest targets for tables/source files and create provisional extracted-source CSVs",
                "Interpretation": "candidate triage identifies first acquisition targets but does not create measurement inputs",
                "ClaimBoundary": "physical_null_candidate_triage_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
