#!/usr/bin/env python3
"""Check mapping readiness for provisional physical-null extraction rows.

The check is deliberately conservative. It only asks whether provisional
source rows cover the source-split redshift grid and whether they carry any
source uncertainty. It does not transform alpha/backreaction quantities into a
benchmark prediction and does not authorize measurement use.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

MANIFEST = EVIDENCE / "physical_null_provisional_extraction_manifest.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
OUT = EVIDENCE / "physical_null_mapping_readiness.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_mapping_readiness_summary.csv"


def parse_range(text: object) -> tuple[float | None, float | None]:
    if not isinstance(text, str) or not text.strip():
        return None, None
    nums = [float(x) for x in re.findall(r"[-+]?\d+(?:\.\d+)?", text)]
    if len(nums) >= 2:
        return min(nums[0], nums[1]), max(nums[0], nums[1])
    return None, None


def is_number(value: object) -> bool:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(x)


def classify(
    *,
    quantity: str,
    coverage_fraction: float,
    has_value: bool,
    has_uncertainty: bool,
    has_transform: bool,
) -> tuple[str, str, str]:
    blockers: list[str] = []
    if not has_value:
        blockers.append("numeric_value_missing")
    if coverage_fraction < 1.0:
        blockers.append("redshift_coverage_incomplete")
    if not has_uncertainty:
        blockers.append("source_uncertainty_missing")
    if not has_transform:
        blockers.append("physical_to_source_split_transform_missing")
    blockers.append("covariance_propagation_missing")

    if quantity == "distance_duality_delta":
        blockers.append("control_quantity_not_primary_physical_null")

    if not blockers:
        return "MAPPING_READY_BUT_COVARIANCE_UNCHECKED", "", "preflight_only"

    if coverage_fraction == 0.0:
        status = "MAPPING_BLOCKED_NO_GRID_COVERAGE"
    elif has_value and coverage_fraction == 1.0 and has_uncertainty:
        status = "MAPPING_PRECHECK_PARTIAL_READY"
    else:
        status = "MAPPING_BLOCKED"
    return status, ";".join(blockers), "physical_null_mapping_precheck_no_measurement_validation"


def main() -> None:
    manifest = pd.read_csv(MANIFEST)
    target = pd.read_csv(TARGET)
    z_grid = target["z_grid"].astype(float).tolist()
    usable_target_rows = int(target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"]).sum())

    rows: list[dict[str, object]] = []
    for _, source in manifest.iterrows():
        z_min, z_max = parse_range(source.get("RedshiftRange"))
        if z_min is None or z_max is None:
            covered = []
        else:
            covered = [z for z in z_grid if z_min <= z <= z_max]

        coverage_fraction = len(covered) / len(z_grid) if z_grid else 0.0
        usable_covered = 0
        if covered:
            covered_set = set(covered)
            usable_covered = int(
                target[
                    target["z_grid"].astype(float).isin(covered_set)
                    & target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])
                ].shape[0]
            )
        usable_coverage_fraction = usable_covered / usable_target_rows if usable_target_rows else 0.0

        quantity = str(source.get("Quantity", ""))
        has_value = is_number(source.get("Value"))
        has_uncertainty = is_number(source.get("LowerError")) and is_number(source.get("UpperError"))
        has_transform = False
        if quantity == "alpha_smoothness":
            transform_requirement = "alpha_to_source_split_response_model_missing"
        elif quantity == "distance_duality_delta":
            transform_requirement = "delta_to_optical_control_mapping_missing"
        else:
            transform_requirement = "backreaction_envelope_to_source_split_mapping_missing"

        status, blocking, claim = classify(
            quantity=quantity,
            coverage_fraction=coverage_fraction,
            has_value=has_value,
            has_uncertainty=has_uncertainty,
            has_transform=has_transform,
        )

        rows.append(
            {
                "ExtractionID": source["ExtractionID"],
                "CandidateID": source["CandidateID"],
                "NullID": source["NullID"],
                "Quantity": quantity,
                "Value": source.get("Value", ""),
                "ConfidenceLevel": source.get("ConfidenceLevel", ""),
                "SourceRedshiftRange": source.get("RedshiftRange", ""),
                "TargetZMin": min(z_grid) if z_grid else "",
                "TargetZMax": max(z_grid) if z_grid else "",
                "CoveredTargetRows": len(covered),
                "TotalTargetRows": len(z_grid),
                "CoverageFraction": coverage_fraction,
                "CoveredUsableRows": usable_covered,
                "TotalUsableRows": usable_target_rows,
                "UsableCoverageFraction": usable_coverage_fraction,
                "HasNumericValue": has_value,
                "HasSourceUncertainty": has_uncertainty,
                "HasTransformToSourceSplit": has_transform,
                "TransformRequirement": transform_requirement,
                "HasCovariancePropagation": False,
                "Status": status,
                "CanUseAsBenchmarkInputNow": False,
                "BlockingIssue": blocking,
                "RequiredNextCheck": "define_transform_and_covariance_propagation_before_scorecard_use",
                "ClaimBoundary": claim,
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_MAPPING_READINESS_SUMMARY",
                "RowsChecked": len(output),
                "RowsWithFullTargetCoverage": int(output["CoverageFraction"].eq(1.0).sum()),
                "RowsWithFullUsableCoverage": int(output["UsableCoverageFraction"].eq(1.0).sum()),
                "RowsWithNumericValue": int(output["HasNumericValue"].sum()),
                "RowsWithSourceUncertainty": int(output["HasSourceUncertainty"].sum()),
                "RowsWithTransformToSourceSplit": int(output["HasTransformToSourceSplit"].sum()),
                "RowsWithCovariancePropagation": int(output["HasCovariancePropagation"].sum()),
                "BenchmarkInputsReadyNow": int(output["CanUseAsBenchmarkInputNow"].sum()),
                "BestCoverageExtractionID": output.sort_values(
                    ["UsableCoverageFraction", "CoverageFraction"], ascending=False
                ).iloc[0]["ExtractionID"],
                "PrimaryBlockingIssue": "physical_to_source_split_transform_missing;covariance_propagation_missing",
                "Interpretation": "provisional source values have coverage metadata but remain mapping/covariance blocked",
                "ClaimBoundary": "physical_null_mapping_precheck_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
