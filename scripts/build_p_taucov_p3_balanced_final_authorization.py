#!/usr/bin/env python3
"""Build final authorization for the P3 balanced signed alignment scorecard."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight.yaml"
SCORECARD_FREEZE = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze.yaml"
POLICY = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy.yaml"
OBJECT_MANIFEST = ROOT / "evidence/p_taucov_p3_balanced_final_manifest.yaml"
STRUCTURAL_NULL = ROOT / "evidence/p_taucov_p3_balanced_structural_null_audit_summary.csv"
DOC = ROOT / "docs/p_taucov_p3_balanced_final_authorization.md"
MANIFEST = ROOT / "evidence/p_taucov_p3_balanced_final_authorization.yaml"
SHA = ROOT / "evidence/p_taucov_p3_balanced_final_authorization.sha256"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_final_authorization_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUTH_ID = "P_TAUCOV_P3_BALANCED_FINAL_AUTHORIZATION_v1"
STATUS_AUTH = "P_TAUCOV_P3_BALANCED_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM"
STATUS_BLOCKED = "P_TAUCOV_P3_BALANCED_FINAL_AUTHORIZATION_BLOCKED"
CLAIM_BOUNDARY = "p3_balanced_scorecard_authorized_no_survival_claim"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def yread(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def csv_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    df = pd.read_csv(path)
    return str(df.iloc[0]["Status"]) if "Status" in df.columns else "NO_STATUS_COLUMN"


def main() -> int:
    required = [PREFLIGHT, SCORECARD_FREEZE, POLICY, OBJECT_MANIFEST, STRUCTURAL_NULL]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing final authorization inputs: " + ", ".join(str(p.relative_to(ROOT)) for p in missing))

    preflight = yread(PREFLIGHT)
    scorecard = yread(SCORECARD_FREEZE)
    policy = yread(POLICY)
    obj = yread(OBJECT_MANIFEST)
    structural_status = csv_status(STRUCTURAL_NULL)
    blockers = list(preflight.get("BlockingItems", []))
    authorizable = (
        preflight.get("Status") == "READY_FOR_FINAL_AUTHORIZATION_NO_SCORING"
        and blockers == ["final_authorization_manifest_ready"]
        and scorecard.get("Status") == "P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FROZEN_NO_SCORING"
        and policy.get("Status") == "P_TAUCOV_P3_BALANCED_SCORING_POLICY_FROZEN_NO_SCORING"
        and obj.get("Status") == "P_TAUCOV_P3_BALANCED_OBJECT_FROZEN_NO_SCORING_AUTHORIZATION"
        and structural_status == "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_PASS_NO_SCORING"
    )
    status = STATUS_AUTH if authorizable else STATUS_BLOCKED
    input_files = {
        "preflight": str(PREFLIGHT.relative_to(ROOT)),
        "scorecard_script_freeze": str(SCORECARD_FREEZE.relative_to(ROOT)),
        "scoring_policy": str(POLICY.relative_to(ROOT)),
        "object_manifest": str(OBJECT_MANIFEST.relative_to(ROOT)),
        "structural_null_audit": str(STRUCTURAL_NULL.relative_to(ROOT)),
    }
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "AuthorizationID": AUTH_ID,
        "Status": status,
        "P3BalancedScoringAuthorized": bool(authorizable),
        "AuthorizedScorecard": "scripts/run_p_taucov_p3_balanced_scorecard.py",
        "AuthorizedScope": "p3_balanced_signed_alignment_scorecard_only",
        "SurvivalClaimAuthorized": False,
        "CovarianceSurvivalClaimAuthorized": False,
        "TauCoreValidationClaimAuthorized": False,
        "MeasurementValidationAuthorized": False,
        "Reason": "all frozen P3 balanced gates are closed except the final authorization gate" if authorizable else "preflight or freeze inputs are incomplete",
        "InputFiles": input_files,
        "InputSHA256": {key: sha256(ROOT / rel) for key, rel in input_files.items()},
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA.write_text(f"{sha256(MANIFEST)}  {MANIFEST.relative_to(ROOT)}\n", encoding="utf-8")
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuthorizationID": AUTH_ID,
                "Status": status,
                "P3BalancedScoringAuthorized": bool(authorizable),
                "SurvivalClaimAuthorized": False,
                "CovarianceSurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "AuthorizedScope": manifest["AuthorizedScope"],
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov P3 Balanced Final Authorization

Authorization ID: `{AUTH_ID}`

Status:

`{status}`

This manifest authorizes only the P3 balanced signed-alignment scorecard.

```text
P3BalancedScoringAuthorized = {str(bool(authorizable)).lower()}
SurvivalClaimAuthorized = false
CovarianceSurvivalClaimAuthorized = false
TauCoreValidationClaimAuthorized = false
MeasurementValidationAuthorized = false
AuthorizedScope = p3_balanced_signed_alignment_scorecard_only
```

It does not authorize a survival claim, measurement validation claim, or Tau Core validation claim.
""",
        encoding="utf-8",
    )
    print(status)
    return 0 if authorizable else 1


if __name__ == "__main__":
    raise SystemExit(main())
