#!/usr/bin/env python3
"""Validate the Q-native route registry."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_v1"


def main() -> None:
    registry_path = EVIDENCE / "p_taucov_q_native_route_registry.csv"
    summary_path = EVIDENCE / "p_taucov_q_native_route_registry_summary.csv"
    doc_path = DOCS / "p_taucov_q_native_route_registry.md"
    for path in [registry_path, summary_path, doc_path]:
        if not path.exists():
            raise SystemExit(f"Missing required artifact: {path}")
    registry = pd.read_csv(registry_path)
    summary = pd.read_csv(summary_path)
    if len(summary) != 1:
        raise SystemExit("Expected one summary row")
    if summary.iloc[0]["FreezeID"] != FREEZE_ID:
        raise SystemExit("Unexpected FreezeID")
    if len(registry) != 4:
        raise SystemExit("Expected four Q-native routes")
    forbidden = [
        "ObjectConstructed",
        "SupportAuditAuthorized",
        "ScoringAuthorized",
        "SurvivalClaimAuthorized",
        "TauCoreValidationClaimAuthorized",
    ]
    for col in forbidden:
        if registry[col].astype(bool).any():
            raise SystemExit(f"{col} must be false for every route")
    if bool(summary.iloc[0]["ScoringAuthorized"]) or bool(summary.iloc[0]["SurvivalClaimAuthorized"]):
        raise SystemExit("Summary must not authorize scoring or survival")
    pd.DataFrame(
        [
            {
                "FreezeID": FREEZE_ID,
                "ValidationStatus": "P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_VALID",
                "RoutesDefined": len(registry),
                "ScoringAuthorized": False,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_native_route_registry_validation.csv", index=False)
    print("P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_VALID")


if __name__ == "__main__":
    main()
