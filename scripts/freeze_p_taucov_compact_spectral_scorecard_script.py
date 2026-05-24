#!/usr/bin/env python3
"""Freeze the compact spectral scorecard script hash."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_p_taucov_compact_spectral_scorecard.py"
OUT = ROOT / "evidence/p_taucov_compact_spectral_scorecard_script_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_scorecard_script_freeze_summary.csv"
DOC = ROOT / "docs/p_taucov_compact_spectral_scorecard_script_freeze.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_SCRIPT_FREEZE_v1"
CLAIM_BOUNDARY = "compact_spectral_scorecard_script_freeze_no_scoring"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    digest = sha256(SCRIPT)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "ScriptPath": str(SCRIPT.relative_to(ROOT)),
                "SHA256": digest,
                "ScriptMode": "blocked_until_compact_spectral_final_manifest",
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_SCRIPT_FROZEN_NO_SCORING",
                "ScriptPath": str(SCRIPT.relative_to(ROOT)),
                "SHA256": digest,
                "ScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov Compact Spectral Scorecard Script Freeze

Status: `P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_SCRIPT_FROZEN_NO_SCORING`.

- script: `{SCRIPT.relative_to(ROOT)}`
- SHA256: `{digest}`
- mode: `blocked_until_compact_spectral_final_manifest`

This freezes the compact spectral scorecard entrypoint before scoring
authorization. The script remains blocked unless a final authorization manifest
exists and explicitly authorizes the compact spectral primary covariance
scorecard scope.
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_SCRIPT_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
