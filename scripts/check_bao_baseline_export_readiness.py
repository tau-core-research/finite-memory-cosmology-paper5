#!/usr/bin/env python3
"""Check BAO baseline exports for T1 measurement-gate eligibility."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.baseline_export import (
    baseline_export_allowed,
    baseline_export_issues,
    load_baseline_registry,
)

REGISTRY = ROOT / "evidence" / "bao_baseline_export_registry.csv"
OUT = ROOT / "evidence" / "bao_baseline_export_readiness.csv"


def main() -> None:
    registry = load_baseline_registry(REGISTRY)
    rows = []
    for _, row in registry.iterrows():
        issues = baseline_export_issues(row)
        rows.append(
            {
                "BaselineExportID": row["BaselineExportID"],
                "Status": row["Status"],
                "ProductScope": row["ProductScope"],
                "FittedInThisNote": row["FittedInThisNote"],
                "LikelihoodNative": row["LikelihoodNative"],
                "CoordinateNative": row["CoordinateNative"],
                "AbsorbsGlobalScaleOffset": row["AbsorbsGlobalScaleOffset"],
                "AllowedForT1Preflight": row["AllowedForT1Preflight"],
                "AllowedForMeasurementGate": baseline_export_allowed(row),
                "BlockingIssue": ";".join(dict.fromkeys(issues)),
                "RequiredNextCheck": row["RequiredNextCheck"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
