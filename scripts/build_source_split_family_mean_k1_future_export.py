#!/usr/bin/env python3
"""Build a future-only equal-weight family-mean external K1 candidate export."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
FAMILIES = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
OUT = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
SUMMARY = EVIDENCE / "source_split_family_mean_k1_future_export_summary.csv"


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def main() -> None:
    families = pd.read_csv(FAMILIES)
    target = pd.read_csv(TARGET)
    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].sort_values("GridIndex")

    rows: list[dict[str, object]] = []
    for _, target_row in usable.iterrows():
        grid_index = int(target_row["GridIndex"])
        family_rows = families[families["GridIndex"].astype(int).eq(grid_index)].copy()
        values = family_rows["ResponseValue"].astype(float).to_numpy()
        sigmas = family_rows["ResponseSigma"].astype(float).to_numpy()
        if len(values) < 2:
            raise ValueError(f"Expected at least two family rows for GridIndex={grid_index}")

        k1_response = float(np.mean(values))
        # Equal-weight uncertainty propagation; no amplitude refit is applied.
        k1_sigma = float(np.sqrt(np.sum(sigmas**2)) / len(sigmas))
        rows.append(
            {
                "K1TargetID": "SSK1_EXTERNAL_NONZERO_SOURCE_SPLIT_TARGET",
                "SourceTargetID": target_row["TargetID"],
                "GridIndex": grid_index,
                "z_grid": float(target_row["z_grid"]),
                "x_coordinate": float(target_row["x_coordinate"]),
                "x_mapping": target_row["x_mapping"],
                "K1Response": k1_response,
                "K1Sigma": k1_sigma,
                "K1SourceID": "K1SRC_EXTERNAL_RECONSTRUCTION_FAMILY_MEAN",
                "ProvenanceType": "external_reconstruction_family_mean",
                "CoordinateNative": True,
                "LikelihoodNative": False,
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "UsesJointCovariance": True,
                "SameDataAmplitudeFit": False,
                "FittedInThisNote": False,
                "AmplitudePolicy": "equal_weight_signed_mean_no_rescale_future_only",
                "Predeclared": True,
                "AllowedAsPrimaryK1Candidate": False,
                "ClaimBoundary": "future_only_family_mean_k1_no_measurement_validation",
                "FutureRerunProtocolID": "SSRERUN_FAMILY_MEAN_EQUAL_WEIGHT_V1",
                "AllowedForCurrentRerun": False,
                "AllowedForFutureRerun": True,
                "K1ResponseSign": sign(k1_response),
                "FamilyCount": len(family_rows),
                "FamilyIDs": ";".join(sorted(family_rows["FamilyID"].astype(str))),
            }
        )

    output = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "ExportID": "SOURCE_SPLIT_FAMILY_MEAN_K1_FUTURE_EXPORT_V1",
                "CandidatePath": str(OUT.relative_to(ROOT)),
                "Rows": len(output),
                "NonzeroRows": int((~np.isclose(output["K1Response"].to_numpy(float), 0.0)).sum()),
                "MeanAbsK1Response": float(np.mean(np.abs(output["K1Response"].to_numpy(float)))),
                "MeanK1Sigma": float(np.mean(output["K1Sigma"].to_numpy(float))),
                "AllowedForCurrentRerun": False,
                "AllowedForFutureRerun": True,
                "AllowedAsPrimaryK1Candidate": False,
                "BlockingIssue": "future_only_export_not_current_primary_k1;policy_declared_after_current_scorecard",
                "NextAction": "Use only after explicit future rerun pre-registration; current K2 scorecard remains closed.",
                "ClaimBoundary": "future_only_family_mean_k1_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
