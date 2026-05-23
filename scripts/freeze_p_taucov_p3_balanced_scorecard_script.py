#!/usr/bin/env python3
"""Freeze the P3 balanced P-TauCov scorecard script hash."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_p_taucov_p3_balanced_scorecard.py"
DOC = ROOT / "docs/p_taucov_p3_balanced_scorecard_script_freeze.md"
MANIFEST = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze.yaml"
SHA = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze.sha256"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FREEZE_v1"
STATUS = "P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FROZEN_NO_SCORING"
CLAIM_BOUNDARY = "p3_balanced_scorecard_script_frozen_no_scoring_authorization"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not SCRIPT.exists():
        raise FileNotFoundError(f"Missing scorecard script: {SCRIPT.relative_to(ROOT)}")
    digest = sha256(SCRIPT)
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "Status": STATUS,
        "ScorecardScript": str(SCRIPT.relative_to(ROOT)),
        "ScorecardSHA256": digest,
        "ScriptRequiresFinalAuthorization": True,
        "P3BalancedScoringAuthorized": False,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA.write_text(f"{digest}  {SCRIPT.relative_to(ROOT)}\n{sha256(MANIFEST)}  {MANIFEST.relative_to(ROOT)}\n", encoding="utf-8")
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "ScorecardScriptFrozen": True,
                "ScorecardSHA256": digest,
                "P3BalancedScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov P3 Balanced Scorecard Script Freeze

Freeze ID: `{FREEZE_ID}`

Status:

`{STATUS}`

The scorecard script is frozen by hash:

```text
Script = {SCRIPT.relative_to(ROOT)}
SHA256 = {digest}
```

The script is inert unless a final authorization manifest explicitly sets:

```text
P3BalancedScoringAuthorized: true
```

This freeze does not run the scorecard and does not authorize empirical scoring.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
