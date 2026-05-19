#!/usr/bin/env python3
"""Check likelihood-native BAO baseline source readiness."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood_baseline import (
    likelihood_source_allowed,
    likelihood_source_issues,
    load_likelihood_baseline_sources,
)

REGISTRY = ROOT / "evidence" / "bao_likelihood_baseline_source_registry.csv"
OUT = ROOT / "evidence" / "bao_likelihood_baseline_source_readiness.csv"


def main() -> None:
    registry = load_likelihood_baseline_sources(REGISTRY)
    rows = []
    for _, row in registry.iterrows():
        issues = likelihood_source_issues(row)
        rows.append(
            {
                "SourceID": row["SourceID"],
                "SourceType": row["SourceType"],
                "ProductScope": row["ProductScope"],
                "Status": row["Status"],
                "HasPublicDataVector": row["HasPublicDataVector"],
                "HasPublicCovariance": row["HasPublicCovariance"],
                "HasBaselinePrediction": row["HasBaselinePrediction"],
                "HasFrozenCosmology": row["HasFrozenCosmology"],
                "HasReproducibleEvaluator": row["HasReproducibleEvaluator"],
                "AllowedForBaselineExport": likelihood_source_allowed(row),
                "BlockingIssue": ";".join(dict.fromkeys(issues)),
                "NextAction": row["NextAction"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
