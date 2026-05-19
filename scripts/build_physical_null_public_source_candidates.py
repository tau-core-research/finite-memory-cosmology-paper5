#!/usr/bin/env python3
"""Register concrete public-paper candidates for physical-null calibration."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

OUT = EVIDENCE / "physical_null_public_source_candidates.csv"
OUT_READINESS = EVIDENCE / "physical_null_public_source_candidate_readiness.csv"


def main() -> None:
    rows = [
        {
            "CandidateID": "PNC_BACKREACTION_KOKSBANG_2604_11249",
            "NullID": "BACKREACTION_ONLY",
            "Reference": "Koksbang, First observational constraints on cosmic backreaction over an extended redshift range",
            "URL": "https://arxiv.org/abs/2604.11249",
            "CandidateUse": "backreaction envelope or constraints over redshift",
            "LikelyMachineReadableData": "unknown",
            "NeedsDigitization": True,
            "NeedsCovarianceExtraction": True,
            "NeedsSourceSplitMapping": True,
            "CurrentStatus": "candidate_not_ingested",
            "NextAction": "inspect paper/source files for tables, expressions, or repository links usable as backreaction calibration source",
            "ClaimBoundary": "physical_null_public_source_candidates_no_measurement_validation",
        },
        {
            "CandidateID": "PNC_BACKREACTION_HEINESEN_CLIFTON_2604_07244",
            "NullID": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "Reference": "Heinesen and Clifton, Observational Tests for Distinguishing Classes of Cosmological Models",
            "URL": "https://arxiv.org/abs/2604.07244",
            "CandidateUse": "method/source for separating optical-property and expansion/backreaction effects",
            "LikelyMachineReadableData": "method_reference",
            "NeedsDigitization": False,
            "NeedsCovarianceExtraction": True,
            "NeedsSourceSplitMapping": True,
            "CurrentStatus": "method_candidate_not_ingested",
            "NextAction": "use as classification/mapping reference; not a direct amplitude source unless tables are available",
            "ClaimBoundary": "physical_null_public_source_candidates_no_measurement_validation",
        },
        {
            "CandidateID": "PNC_DYER_ROEDER_SNE_GRB_1303_1574",
            "NullID": "DYER_ROEDER_OPTICAL",
            "Reference": "Observational constraints from SNe Ia and Gamma-Ray Bursts on a clumpy universe",
            "URL": "https://arxiv.org/abs/1303.1574",
            "CandidateUse": "smoothness parameter alpha constraint for optical-propagation calibration",
            "LikelyMachineReadableData": "paper_constraints_or_tables",
            "NeedsDigitization": True,
            "NeedsCovarianceExtraction": True,
            "NeedsSourceSplitMapping": True,
            "CurrentStatus": "candidate_not_ingested",
            "NextAction": "extract alpha constraints and uncertainty; check whether redshift-dependent information is available",
            "ClaimBoundary": "physical_null_public_source_candidates_no_measurement_validation",
        },
        {
            "CandidateID": "PNC_DYER_ROEDER_SMOOTHNESS_DD_1305_6989",
            "NullID": "DYER_ROEDER_OPTICAL",
            "Reference": "Constraining smoothness parameter and the DD relation of Dyer-Roeder equation with supernovae",
            "URL": "https://arxiv.org/abs/1305.6989",
            "CandidateUse": "smoothness parameter and distance-duality check for optical calibration",
            "LikelyMachineReadableData": "paper_constraints_or_tables",
            "NeedsDigitization": True,
            "NeedsCovarianceExtraction": True,
            "NeedsSourceSplitMapping": True,
            "CurrentStatus": "candidate_not_ingested",
            "NextAction": "inspect constraints for alpha and uncertainty usable as optical null amplitude prior",
            "ClaimBoundary": "physical_null_public_source_candidates_no_measurement_validation",
        },
        {
            "CandidateID": "PNC_WEAK_LENSING_DYER_ROEDER_IPAC_1999",
            "NullID": "DYER_ROEDER_OPTICAL",
            "Reference": "Analytical Modeling of the Weak Lensing of Standard Candles I",
            "URL": "https://www.ipac.caltech.edu/publication/1999ApJ...525..651W",
            "CandidateUse": "weak-lensing to generalized Dyer-Roeder mapping reference",
            "LikelyMachineReadableData": "method_reference",
            "NeedsDigitization": False,
            "NeedsCovarianceExtraction": True,
            "NeedsSourceSplitMapping": True,
            "CurrentStatus": "method_candidate_not_ingested",
            "NextAction": "use as optical-proxy mapping reference if a public lensing amplitude source is selected",
            "ClaimBoundary": "physical_null_public_source_candidates_no_measurement_validation",
        },
        {
            "CandidateID": "PNC_REDUCED_CONVERGENCE_SMOOTHNESS_IPAC_2005",
            "NullID": "DYER_ROEDER_OPTICAL",
            "Reference": "Reduced Convergence and the Local Smoothness Parameter",
            "URL": "https://www.ipac.caltech.edu/publication/2005ApJ...624...46W",
            "CandidateUse": "mapping between weak-lensing reduced convergence and smoothness parameter",
            "LikelyMachineReadableData": "method_reference",
            "NeedsDigitization": False,
            "NeedsCovarianceExtraction": True,
            "NeedsSourceSplitMapping": True,
            "CurrentStatus": "method_candidate_not_ingested",
            "NextAction": "use only if a compatible lensing/convergence source with uncertainty is selected",
            "ClaimBoundary": "physical_null_public_source_candidates_no_measurement_validation",
        },
    ]
    candidates = pd.DataFrame(rows)
    candidates.to_csv(OUT, index=False)

    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PHYSICAL_NULL_PUBLIC_SOURCE_CANDIDATE_READINESS",
                "CandidatesRegistered": len(candidates),
                "BackreactionCandidates": int(candidates["NullID"].str.contains("BACKREACTION_ONLY").sum()),
                "OpticalCandidates": int(candidates["NullID"].str.contains("DYER_ROEDER_OPTICAL").sum()),
                "DirectAmplitudeCandidates": int(candidates["CandidateUse"].str.contains("constraint|envelope").sum()),
                "MethodReferenceCandidates": int(candidates["LikelyMachineReadableData"].eq("method_reference").sum()),
                "CandidatesIngested": 0,
                "CandidatesMapped": 0,
                "CandidatesWithCovariance": 0,
                "PhysicalNullSourceCandidateReady": False,
                "PrimaryBlockingIssue": "candidate_sources_not_ingested_digitized_or_mapped",
                "NextAction": "inspect candidate papers for tables/source files, then create row-aligned source CSVs with uncertainties",
                "Interpretation": "public candidates are registered for acquisition, but none is a usable calibration source yet",
                "ClaimBoundary": "physical_null_public_source_candidates_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
