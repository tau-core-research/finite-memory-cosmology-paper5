#!/usr/bin/env python3
"""Check locked BAO K1 response target readiness."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.k1_locked_response import (
    load_locked_response_registry,
    locked_response_allowed,
    locked_response_issues,
)

REGISTRY = ROOT / "evidence" / "bao_k1_locked_response_registry.csv"
OUT = ROOT / "evidence" / "bao_k1_locked_response_readiness.csv"


def main() -> None:
    registry = load_locked_response_registry(REGISTRY)
    rows = []
    for _, row in registry.iterrows():
        issues = locked_response_issues(row)
        rows.append(
            {
                "ResponseTargetID": row["ResponseTargetID"],
                "TargetSpace": row["TargetSpace"],
                "Status": row["Status"],
                "BaselineBracket": row["BaselineBracket"],
                "AmplitudeNormalization": row["AmplitudeNormalization"],
                "SourceResidual": row["SourceResidual"],
                "SameDataDerived": row["SameDataDerived"],
                "AllowedForK2Scoring": locked_response_allowed(row),
                "BlockingIssue": ";".join(dict.fromkeys(issues)),
                "NextAction": row["NextAction"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
