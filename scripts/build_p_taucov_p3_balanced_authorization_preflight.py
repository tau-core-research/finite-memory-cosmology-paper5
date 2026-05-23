#!/usr/bin/env python3
"""Build authorization preflight for the P3 balanced P-TauCov object."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "p3_balanced_final_manifest": ROOT / "evidence/p_taucov_p3_balanced_final_manifest_summary.csv",
    "p3_balanced_structural_null_audit": ROOT / "evidence/p_taucov_p3_balanced_structural_null_audit_summary.csv",
    "p3_balanced_scoring_policy": ROOT / "evidence/p_taucov_p3_balanced_scoring_policy_summary.csv",
}
SCRIPT_FREEZE = ROOT / "evidence/p_taucov_p3_balanced_scorecard_script_freeze.yaml"
DOC = ROOT / "docs/p_taucov_p3_balanced_authorization_preflight.md"
MANIFEST = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight.yaml"
SHA = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight.sha256"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight_summary.csv"
CHECKLIST = ROOT / "evidence/p_taucov_p3_balanced_authorization_preflight_checklist.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PREFLIGHT_ID = "P_TAUCOV_P3_BALANCED_AUTHORIZATION_PREFLIGHT_v1"
STATUS_READY = "READY_FOR_FINAL_AUTHORIZATION_NO_SCORING"
STATUS_BLOCKED = "BLOCKED_NO_SCORING_AUTHORIZATION"
CLAIM_BOUNDARY = "p3_balanced_authorization_preflight_no_scoring"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    df = pd.read_csv(path)
    return str(df.iloc[0]["Status"]) if "Status" in df.columns else "NO_STATUS_COLUMN"


def yaml_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return str(data.get("Status", "NO_STATUS_FIELD"))


def main() -> int:
    expected = {
        "p3_balanced_final_manifest": "P_TAUCOV_P3_BALANCED_OBJECT_FROZEN_NO_SCORING_AUTHORIZATION",
        "p3_balanced_structural_null_audit": "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_PASS_NO_SCORING",
        "p3_balanced_scoring_policy": "P_TAUCOV_P3_BALANCED_SCORING_POLICY_FROZEN_NO_SCORING",
    }
    rows = []
    for key, path in INPUTS.items():
        observed = csv_status(path)
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "PreflightID": PREFLIGHT_ID,
                "CheckID": key,
                "Expected": expected[key],
                "Observed": observed,
                "Passed": observed == expected[key],
                "Required": True,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    rows.append(
        {
            "ProtocolID": PROTOCOL_ID,
            "PreflightID": PREFLIGHT_ID,
            "CheckID": "p3_balanced_scorecard_script_frozen",
            "Expected": "P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FROZEN_NO_SCORING",
            "Observed": yaml_status(SCRIPT_FREEZE),
            "Passed": yaml_status(SCRIPT_FREEZE) == "P_TAUCOV_P3_BALANCED_SCORECARD_SCRIPT_FROZEN_NO_SCORING",
            "Required": True,
            "PTauCovScoringAuthorized": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    rows.append(
        {
            "ProtocolID": PROTOCOL_ID,
            "PreflightID": PREFLIGHT_ID,
            "CheckID": "final_authorization_manifest_ready",
            "Expected": "separate final authorization manifest",
            "Observed": "NOT_THIS_ARTIFACT",
            "Passed": False,
            "Required": True,
            "PTauCovScoringAuthorized": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    checklist = pd.DataFrame(rows)
    checklist.to_csv(CHECKLIST, index=False)
    open_required = int((checklist["Required"].astype(bool) & ~checklist["Passed"].astype(bool)).sum())
    status = STATUS_READY if open_required == 1 and set(checklist.loc[~checklist["Passed"], "CheckID"]) == {"final_authorization_manifest_ready"} else STATUS_BLOCKED
    input_files = {key: str(path.relative_to(ROOT)) for key, path in INPUTS.items()}
    input_files["checklist"] = str(CHECKLIST.relative_to(ROOT))
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PreflightID": PREFLIGHT_ID,
        "Status": status,
        "ChecksTotal": int(len(checklist)),
        "ChecksPassed": int(checklist["Passed"].astype(bool).sum()),
        "OpenRequiredChecks": open_required,
        "BlockingItems": checklist.loc[checklist["Required"].astype(bool) & ~checklist["Passed"].astype(bool), "CheckID"].astype(str).tolist(),
        "PTauCovScoringAuthorized": False,
        "InputFiles": input_files,
        "InputSHA256": {key: sha256(ROOT / rel) for key, rel in input_files.items() if (ROOT / rel).exists()},
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA.write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(ROOT)}" for path in [CHECKLIST, MANIFEST]) + "\n",
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PreflightID": PREFLIGHT_ID,
                "Status": status,
                "ChecksPassed": f"{manifest['ChecksPassed']}/{manifest['ChecksTotal']}",
                "OpenRequiredChecks": open_required,
                "PTauCovScoringAuthorized": False,
                "NextStep": "build_p3_balanced_final_authorization_manifest_or_stop_before_scoring",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov P3 Balanced Authorization Preflight

Preflight ID: `{PREFLIGHT_ID}`

Status:

`{status}`

## Result

```text
ChecksPassed = {manifest['ChecksPassed']}/{manifest['ChecksTotal']}
OpenRequiredChecks = {open_required}
PTauCovScoringAuthorized = false
```

Blocking items:

```text
{chr(10).join(manifest['BlockingItems'])}
```

## Interpretation

The P3 balanced object, structural null audit, scoring policy, and scorecard
script are frozen. Empirical scoring remains blocked until a separate final
authorization manifest is created.

## Claim Boundary

Allowed statement:

> P3 balanced is ready up to the final-authorization gate.

Forbidden statement:

> P3 balanced has been scored, survived scoring, or validated Tau Core.
""",
        encoding="utf-8",
    )
    print(f"P_TAUCOV_P3_BALANCED_AUTHORIZATION_PREFLIGHT_{status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
