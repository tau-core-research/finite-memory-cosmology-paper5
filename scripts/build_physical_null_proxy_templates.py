#!/usr/bin/env python3
"""Build non-scoring physical-null proxy templates for the source-split vector."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.physical_nulls import backreaction_broadband_shape, dyer_roeder_optical_shape

TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
OUT = ROOT / "evidence" / "physical_null_proxy_templates.csv"
OUT_READINESS = ROOT / "evidence" / "physical_null_proxy_template_readiness.csv"


def main() -> None:
    target = pd.read_csv(TARGET)
    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    usable = usable.sort_values("GridIndex").reset_index(drop=True)
    x = usable["x_coordinate"].to_numpy(float)
    backreaction = backreaction_broadband_shape(x)
    optical = dyer_roeder_optical_shape(x)

    rows = []
    for idx, row in usable.iterrows():
        rows.extend(
            [
                {
                    "TemplateID": "BACKREACTION_BROADBAND_UNIT_NORM_V1",
                    "NullID": "BACKREACTION_ONLY",
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "x_coordinate": float(row["x_coordinate"]),
                    "ProxyValue": float(backreaction[idx]),
                    "ShapeDefinition": "unit_norm(centered[x^2*(1-0.5*x)])",
                    "AmplitudePolicy": "not_fit_in_template",
                    "ScoringAllowed": False,
                    "RequiredBeforeScoring": "predeclare amplitude policy and covariance route",
                    "ClaimBoundary": "physical_null_proxy_template_no_measurement_validation",
                },
                {
                    "TemplateID": "DYER_ROEDER_OPTICAL_UNIT_NORM_V1",
                    "NullID": "DYER_ROEDER_OPTICAL",
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "x_coordinate": float(row["x_coordinate"]),
                    "ProxyValue": float(optical[idx]),
                    "ShapeDefinition": "unit_norm(centered[x^2])",
                    "AmplitudePolicy": "not_fit_in_template",
                    "ScoringAllowed": False,
                    "RequiredBeforeScoring": "predeclare optical amplitude/clumpiness policy and covariance route",
                    "ClaimBoundary": "physical_null_proxy_template_no_measurement_validation",
                },
            ]
        )
    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PHYSICAL_NULL_PROXY_TEMPLATE_READINESS",
                "Templates": int(output["TemplateID"].nunique()),
                "RowsPerTemplate": int(len(usable)),
                "BackreactionTemplateAvailable": True,
                "DyerRoederOpticalTemplateAvailable": True,
                "AmplitudePolicyDeclared": False,
                "ScoringAllowed": False,
                "MeasurementValidationAllowed": False,
                "PrimaryBlockingIssue": "physical_null_amplitude_policy_not_declared",
                "NextAction": "predeclare amplitude policy for physical nulls before adding them to any scorecard",
                "Interpretation": "physical null shapes are now available as non-scoring templates only",
                "ClaimBoundary": "physical_null_proxy_template_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
