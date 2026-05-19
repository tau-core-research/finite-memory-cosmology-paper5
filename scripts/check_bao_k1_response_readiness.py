#!/usr/bin/env python3
"""Check BAO K1 response readiness for K2 scoring."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.k1_response import k1_response_allowed, k1_response_issues, load_k1_response_registry

REGISTRY = ROOT / "evidence" / "bao_k1_response_registry.csv"
OUT = ROOT / "evidence" / "bao_k1_response_readiness.csv"


def main() -> None:
    registry = load_k1_response_registry(REGISTRY)
    rows = []
    for _, row in registry.iterrows():
        issues = k1_response_issues(row)
        rows.append(
            {
                "ResponseID": row["ResponseID"],
                "TargetSpace": row["TargetSpace"],
                "Status": row["Status"],
                "SourceBaseline": row["SourceBaseline"],
                "CoordinateNative": row["CoordinateNative"],
                "LikelihoodNative": row["LikelihoodNative"],
                "FittedInThisNote": row["FittedInThisNote"],
                "AllowedForK2Scoring": k1_response_allowed(row),
                "BlockingIssue": ";".join(dict.fromkeys(issues)),
                "RequiredNextCheck": row["RequiredNextCheck"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
