#!/usr/bin/env python3
"""Validate PB zero-diagonal final authorization manifest."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

MANIFEST = EVIDENCE / "p_taucov_pb_zero_diagonal_final_manifest.yaml"
SUMMARY = EVIDENCE / "p_taucov_pb_zero_diagonal_final_manifest_summary.csv"
DOC = DOCS / "p_taucov_pb_zero_diagonal_final_manifest.md"
OUT = EVIDENCE / "p_taucov_pb_zero_diagonal_final_manifest_validation.csv"

FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_FINAL_MANIFEST_v1"
EXPECTED_STATUS = "P_TAUCOV_PB_ZERO_DIAGONAL_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append({"FreezeID": FREEZE_ID, "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for key, path in {"manifest": MANIFEST, "summary": SUMMARY, "doc": DOC}.items():
        add(f"exists_{key}", path.exists())
    if MANIFEST.exists() and SUMMARY.exists() and DOC.exists():
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_expected", manifest["Status"] == EXPECTED_STATUS and str(summary["Status"]) == EXPECTED_STATUS)
        add("scoring_authorized", bool(manifest["PTauCovScoringAuthorized"]) and bool(summary["PTauCovScoringAuthorized"]))
        add("survival_not_authorized", not bool(manifest["SurvivalClaimAuthorized"]) and not bool(summary["SurvivalClaimAuthorized"]))
        add("measurement_not_authorized", not bool(manifest["MeasurementValidationAuthorized"]) and not bool(summary["MeasurementValidationAuthorized"]))
        add("tau_validation_not_authorized", not bool(manifest["TauCoreValidationClaimAuthorized"]) and not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("object_validation_passes", bool(manifest["ObjectValidationPasses"]))
        add("scorecard_entrypoint_declared", manifest["AuthorizedScorecard"] == "scripts/run_p_taucov_pb_zero_diagonal_scorecard.py")
        add("doc_forbids_survival", "does not authorize survival" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PB_ZERO_DIAGONAL_FINAL_MANIFEST_VALID" if ok else "P_TAUCOV_PB_ZERO_DIAGONAL_FINAL_MANIFEST_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
