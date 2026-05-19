#!/usr/bin/env python3
"""Build a compact scorecard from the null comparison results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "evidence" / "null_comparison_results.csv"
OUT = ROOT / "evidence" / "model_scorecard.csv"


def main() -> None:
    results = pd.read_csv(SRC)
    rows = []
    for model, group in results.groupby("Model", sort=False):
        nonviolating = group["Status"].eq("NON_VIOLATING_DIAGNOSTIC")
        rows.append(
            {
                "Model": model,
                "MappingsTested": len(group),
                "NonViolatingMappings": int(nonviolating.sum()),
                "EnvelopeFractionMean": f"{group['EnvelopeFraction'].mean():.10f}",
                "SignStableViolationsTotal": int(group["SignStableViolations"].sum()),
                "Chi2DiagProxyMean": f"{group['Chi2DiagProxy'].mean():.12g}",
                "AICMean": f"{group['AIC'].mean():.12g}",
                "BICMean": f"{group['BIC'].mean():.12g}",
                "DeltaAICvsK2Mean": f"{group['DeltaAIC_vs_K2'].mean():.12g}",
                "DeltaBICvsK2Mean": f"{group['DeltaBIC_vs_K2'].mean():.12g}",
                "BestMappingByChi2": group.loc[group["Chi2DiagProxy"].idxmin(), "Mapping"],
                "BestChi2DiagProxy": f"{group['Chi2DiagProxy'].min():.12g}",
                "WorstStatus": "HAS_WARNINGS" if not nonviolating.all() else "NON_VIOLATING_ALL_MAPPINGS",
            }
        )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
