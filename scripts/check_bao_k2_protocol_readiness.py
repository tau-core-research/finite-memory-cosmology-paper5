#!/usr/bin/env python3
"""Check whether BAO K2 scoring is ready to run."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.k2_protocol import k2_protocol_issues, k2_protocol_ready, load_k2_protocol_registry

REGISTRY = ROOT / "evidence" / "bao_k2_protocol_registry.csv"
OUT = ROOT / "evidence" / "bao_k2_protocol_readiness.csv"


def main() -> None:
    registry = load_k2_protocol_registry(REGISTRY)
    rows = []
    for _, row in registry.iterrows():
        issues = k2_protocol_issues(row)
        rows.append(
            {
                "ProtocolID": row["ProtocolID"],
                "Target": row["Target"],
                "Status": row["Status"],
                "ReadyForK2Scoring": k2_protocol_ready(row),
                "BlockingIssue": ";".join(dict.fromkeys(issues)),
                "BaselineBracket": row["BaselineBracket"],
                "RequiredNulls": row["RequiredNulls"],
                "RhoPolicy": row["RhoPolicy"],
                "NextAction": row["NextAction"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
