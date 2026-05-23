#!/usr/bin/env python3
"""Freeze the epsilon-P3 P-TauCov scorecard script hash."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_p_taucov_epsilon_p3_alignment_scorecard.py"
DOC = ROOT / "docs/p_taucov_epsilon_p3_scorecard_script_freeze.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_scorecard_script_freeze.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_scorecard_script_freeze.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_scorecard_script_freeze_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EPSILON_P3_SCORECARD_SCRIPT_FREEZE_v1"
CLAIM_BOUNDARY = "epsilon_p3_scorecard_script_frozen_no_scoring_authorization"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not SCRIPT.exists():
        raise FileNotFoundError(f"Missing scorecard script: {SCRIPT.relative_to(ROOT)}")

    digest = file_sha256(SCRIPT)
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "Status": "SCORECARD_SCRIPT_FROZEN_NO_SCORING_AUTHORIZATION",
        "ScorecardScript": str(SCRIPT.relative_to(ROOT)),
        "ScorecardSHA256": digest,
        "ScriptRequiresFinalAuthorization": True,
        "PTauCovScoringAuthorized": False,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(f"{digest}  {SCRIPT.relative_to(ROOT)}\n{file_sha256(MANIFEST)}  {MANIFEST.relative_to(ROOT)}\n", encoding="utf-8")
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": manifest["Status"],
                "ScorecardScriptFrozen": True,
                "ScorecardSHA256": digest,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Scorecard Script Freeze

Status: `SCORECARD_SCRIPT_FROZEN_NO_SCORING_AUTHORIZATION`.

The scorecard script is frozen by hash:

```text
Script: {SCRIPT.relative_to(ROOT)}
SHA256: {digest}
```

The script is inert unless a final authorization manifest explicitly sets:

```text
PTauCovScoringAuthorized: true
```

This freeze does not run the scorecard and does not authorize empirical scoring.
""",
        encoding="utf-8",
    )
    for path in [MANIFEST, SHA256, SUMMARY, DOC]:
        print(f"Wrote {path.relative_to(ROOT)}")
    print("P_TAUCOV_EPSILON_P3_SCORECARD_SCRIPT_FROZEN_NO_SCORING_AUTHORIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
