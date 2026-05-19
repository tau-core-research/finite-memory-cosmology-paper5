#!/usr/bin/env python3
"""Export likelihood-native source-split K1 from the promoted preflight vector."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_K1 = ROOT / "data" / "k1"
BASELINE = DATA_K1 / "source_split_likelihood_native_baseline_prediction.csv"
COORDINATE = DATA_K1 / "source_split_likelihood_native_coordinate_map.csv"
OUT = DATA_K1 / "source_split_external_k1_response.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_external_k1_export_summary.csv"


def main() -> None:
    baseline = pd.read_csv(BASELINE)
    coordinate = pd.read_csv(COORDINATE)
    merged = baseline.merge(
        coordinate[["GridIndex", "x_likelihood_native", "CoordinateMapID", "CoordinateDefinition"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    response = merged["RawSourceSplitResponse"].to_numpy(float)
    sigma = merged["JointSigmaDiagProxy"].to_numpy(float)
    output = pd.DataFrame(
        {
            "K1TargetID": "SSK1_LIKELIHOOD_NATIVE_CMB_ONLY_RAW_SOURCE_SPLIT_V1",
            "SourceTargetID": merged["BaselineVectorID"].astype(str),
            "GridIndex": merged["GridIndex"].astype(int),
            "z_grid": merged["z_grid"].astype(float),
            "x_coordinate": merged["x_likelihood_native"].astype(float),
            "x_mapping": merged["CoordinateMapID"].astype(str),
            "K1Response": response,
            "K1Sigma": sigma,
            "K1SourceID": "K1SRC_LIKELIHOOD_NATIVE_JOINT_BASELINE",
            "ProvenanceType": "likelihood_native_baseline",
            "CoordinateNative": True,
            "LikelihoodNative": True,
            "UsesPublicSN": True,
            "UsesPublicBAO": True,
            "UsesJointCovariance": True,
            "SameDataAmplitudeFit": False,
            "FittedInThisNote": False,
            "AmplitudePolicy": "raw_source_split_response_no_same_sample_centering",
            "Predeclared": True,
            "AllowedAsPrimaryK1Candidate": True,
            "ClaimBoundary": "likelihood_native_k1_export_no_measurement_validation",
            "NuisancePolicyID": "SOURCE_SPLIT_RAW_RESPONSE_PRIMARY_CONTROL_CENTERED_V1",
            "CoordinatePolicyID": "SOURCE_SPLIT_CMB_CHI_COORDINATE_POLICY_V1",
            "CovariancePolicyID": "SOURCE_SPLIT_DECLARED_SHRINKAGE_BENCHMARK_COVARIANCE_V1",
            "ControlResponseColumn": "CenteredControlSourceSplitResponse",
            "ControlResponseValue": merged["CenteredControlSourceSplitResponse"].astype(float),
            "CoordinateDefinition": merged["CoordinateDefinition"].astype(str),
            "K1ResponseSign": np.sign(response).astype(int),
        }
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ArtifactID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_EXTERNAL_K1_EXPORT",
                "OutputPath": str(OUT.relative_to(ROOT)),
                "Rows": len(output),
                "NonzeroRows": int((~np.isclose(response, 0.0)).sum()),
                "MeanAbsK1Response": float(np.mean(np.abs(response))),
                "MeanK1Sigma": float(np.mean(sigma)),
                "AllowedAsPrimaryK1Candidate": True,
                "SameDataAmplitudeFit": False,
                "FittedInThisNote": False,
                "NextAction": "Run external K1 validator and promotion gate before any locked K2/null scorecard.",
                "ClaimBoundary": "likelihood_native_k1_export_no_measurement_validation",
            }
        ]
    ).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
