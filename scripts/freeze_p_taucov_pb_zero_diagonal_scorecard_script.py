#!/usr/bin/env python3
"""Freeze PB zero-diagonal scorecard script hash."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_p_taucov_pb_zero_diagonal_scorecard.py"
OUT = ROOT / "evidence/p_taucov_pb_zero_diagonal_scorecard_script_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_pb_zero_diagonal_scorecard_script_freeze_summary.csv"
DOC = ROOT / "docs/p_taucov_pb_zero_diagonal_scorecard_script_freeze.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_SCRIPT_FREEZE_v1"
CLAIM_BOUNDARY = "pb_zero_diagonal_scorecard_script_freeze_no_scoring"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    digest = sha256(SCRIPT)
    row = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "ScriptPath": str(SCRIPT.relative_to(ROOT)),
        "SHA256": digest,
        "ScriptMode": "blocked_until_pb_zero_diagonal_final_manifest",
        "UsesTargetResiduals": False,
        "UsesScoreOutcome": False,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    pd.DataFrame([row]).to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                **row,
                "Status": "P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_SCRIPT_FROZEN_NO_SCORING",
                "MeasurementValidationAllowed": False,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov PB Zero-Diagonal Scorecard Script Freeze",
                "",
                "Status: `P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_SCRIPT_FROZEN_NO_SCORING`.",
                "",
                f"- script: `{SCRIPT.relative_to(ROOT)}`",
                f"- SHA256: `{digest}`",
                "- mode: `blocked_until_pb_zero_diagonal_final_manifest`",
                "",
                "The script remains blocked unless a later final manifest explicitly",
                "authorizes the PB zero-diagonal primary covariance scorecard scope.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_SCRIPT_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
