#!/usr/bin/env python3
"""Check diagnostic-transform readiness for the measurement gate."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.diagnostic_transform import (
    load_transform_registry,
    transform_allowed,
    transform_contract_issues,
)

REGISTRY = ROOT / "evidence" / "diagnostic_transform_registry.csv"
OUT = ROOT / "evidence" / "diagnostic_transform_readiness.csv"


def main() -> None:
    registry = load_transform_registry(REGISTRY)
    rows = []
    for _, row in registry.iterrows():
        issues = transform_contract_issues(row)
        rows.append(
            {
                "TransformID": row["TransformID"],
                "Status": row["Status"],
                "OutputTarget": row["OutputTarget"],
                "UsesPublicCovariance": row["UsesPublicCovariance"],
                "CoordinateNative": row["CoordinateNative"],
                "LikelihoodNative": row["LikelihoodNative"],
                "AllowedForMeasurementGate": transform_allowed(row),
                "BlockingIssue": ";".join(dict.fromkeys(issues)),
                "NextAction": row["NextAction"],
            }
        )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
