#!/usr/bin/env python3
"""Build final authorization for epsilon-P3 bridge-projected primary scorecard."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight.yaml"
SCORECARD_FREEZE = ROOT / "evidence/p_taucov_epsilon_p3_scorecard_script_freeze.yaml"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.yaml"
POLICY = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze.yaml"
DOC = ROOT / "docs/p_taucov_epsilon_p3_final_authorization.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUTH_ID = "P_TAUCOV_EPSILON_P3_FINAL_AUTHORIZATION_v1"
CLAIM_BOUNDARY = "epsilon_p3_primary_bridge_score_authorized_no_survival_claim"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def yread(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    required = [PREFLIGHT, SCORECARD_FREEZE, BRIDGE, POLICY]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing final authorization inputs: " + ", ".join(str(p.relative_to(ROOT)) for p in missing))

    preflight = yread(PREFLIGHT)
    scorecard = yread(SCORECARD_FREEZE)
    bridge = yread(BRIDGE)
    policy = yread(POLICY)
    blockers = list(preflight.get("BlockingItems", []))
    authorizable = (
        preflight.get("Status") == "BLOCKED_NO_SCORING_AUTHORIZATION"
        and blockers == ["final_authorization_manifest_ready"]
        and scorecard.get("Status") == "SCORECARD_SCRIPT_FROZEN_NO_SCORING_AUTHORIZATION"
        and bridge.get("Status") == "FROZEN_COORDINATE_BRIDGE_NO_SCORING"
        and policy.get("Status") == "SCORING_POLICIES_FROZEN_NO_AUTHORIZATION"
    )
    status = "PRIMARY_BRIDGE_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM" if authorizable else "BLOCKED"
    input_files = {
        "preflight": str(PREFLIGHT.relative_to(ROOT)),
        "scorecard_script_freeze": str(SCORECARD_FREEZE.relative_to(ROOT)),
        "coordinate_bridge": str(BRIDGE.relative_to(ROOT)),
        "scoring_policy": str(POLICY.relative_to(ROOT)),
    }
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "AuthorizationID": AUTH_ID,
        "Status": status,
        "PTauCovScoringAuthorized": bool(authorizable),
        "AuthorizedScorecard": "scripts/run_p_taucov_epsilon_p3_alignment_scorecard.py",
        "AuthorizedScope": "primary_bridge_projected_covariance_scorecard_only",
        "SurvivalClaimAuthorized": False,
        "MeasurementValidationAuthorized": False,
        "NullSurvivalSuiteAuthorized": False,
        "Reason": "all preflight gates are closed except the final authorization gate" if authorizable else "preflight or freeze inputs are incomplete",
        "InputFiles": input_files,
        "InputSHA256": {key: file_sha256(ROOT / rel) for key, rel in input_files.items()},
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(f"{file_sha256(MANIFEST)}  {MANIFEST.relative_to(ROOT)}\n", encoding="utf-8")
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuthorizationID": AUTH_ID,
                "Status": status,
                "PTauCovScoringAuthorized": bool(authorizable),
                "SurvivalClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "AuthorizedScope": manifest["AuthorizedScope"],
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Final Authorization

Status: `{status}`.

This manifest authorizes only the primary bridge-projected epsilon-P3
covariance scorecard. It does not authorize a survival claim, measurement
validation claim, or Tau Core validation claim.

```text
PTauCovScoringAuthorized: {str(bool(authorizable)).lower()}
SurvivalClaimAuthorized: false
MeasurementValidationAuthorized: false
AuthorizedScope: primary_bridge_projected_covariance_scorecard_only
```
""",
        encoding="utf-8",
    )
    for path in [MANIFEST, SHA256, SUMMARY, DOC]:
        print(f"Wrote {path.relative_to(ROOT)}")
    if not authorizable:
        print("P_TAUCOV_EPSILON_P3_FINAL_AUTHORIZATION_BLOCKED")
        return 1
    print("P_TAUCOV_EPSILON_P3_FINAL_AUTHORIZATION_PRIMARY_SCORECARD_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
