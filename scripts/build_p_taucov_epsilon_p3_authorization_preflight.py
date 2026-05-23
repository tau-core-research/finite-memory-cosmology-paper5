#!/usr/bin/env python3
"""Build epsilon-P3 P-TauCov final authorization preflight.

This preflight is intentionally conservative: it records which gates are ready
and blocks empirical scoring until a scorecard script and observed-residual
input contract are frozen.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_authorization_preflight.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight_summary.csv"
CHECKLIST = ROOT / "evidence/p_taucov_epsilon_p3_authorization_preflight_checklist.csv"

FREEZE = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest.yaml"
BRANCH = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.yaml"
POLICY = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze.yaml"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PREFLIGHT_ID = "P_TAUCOV_EPSILON_P3_AUTHORIZATION_PREFLIGHT_v1"
CLAIM_BOUNDARY = "epsilon_p3_authorization_preflight_blocks_scoring_until_scorecard_and_input_contract"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def yaml_read(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    required_inputs = [FREEZE, BRANCH, POLICY]
    missing = [path for path in required_inputs if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing preflight inputs: " + ", ".join(str(p.relative_to(ROOT)) for p in missing))

    freeze = yaml_read(FREEZE)
    branch = yaml_read(BRANCH)
    policy = yaml_read(POLICY)

    checks = [
        ("epsilon_p3_candidate_frozen", freeze.get("CandidateFrozen") is True, True, "epsilon-P3 specificity candidate frozen"),
        ("branch_support_frozen", branch.get("Status") == "FROZEN_BRANCH_SUPPORT_NO_SCORING", True, "branch support frozen from delta_C_Tau only"),
        ("scoring_policies_frozen", policy.get("Status") == "SCORING_POLICIES_FROZEN_NO_AUTHORIZATION", True, "fold/null/covariance/df/gate policies frozen"),
        ("scorecard_script_frozen", False, True, "missing frozen scorecard script hash"),
        ("observed_residual_input_contract_frozen", False, True, "missing observed S_obs / residual-covariance input contract"),
        ("final_authorization_manifest_ready", False, True, "this preflight is not final authorization"),
    ]
    checklist = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PreflightID": PREFLIGHT_ID,
                "CheckID": check_id,
                "Passed": passed,
                "Required": required,
                "Evidence": evidence,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for check_id, passed, required, evidence in checks
        ]
    )
    checklist.to_csv(CHECKLIST, index=False)
    open_required = int((checklist["Required"] & ~checklist["Passed"]).sum())
    status = "BLOCKED_NO_SCORING_AUTHORIZATION" if open_required else "READY_FOR_FINAL_AUTHORIZATION"

    input_files = {
        "epsilon_p3_freeze": str(FREEZE.relative_to(ROOT)),
        "branch_support": str(BRANCH.relative_to(ROOT)),
        "scoring_policy": str(POLICY.relative_to(ROOT)),
        "checklist": str(CHECKLIST.relative_to(ROOT)),
    }
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PreflightID": PREFLIGHT_ID,
        "Status": status,
        "ChecksTotal": len(checks),
        "ChecksPassed": int(checklist["Passed"].sum()),
        "OpenRequiredChecks": open_required,
        "PTauCovScoringAuthorized": False,
        "BlockingItems": checklist.loc[checklist["Required"] & ~checklist["Passed"], "CheckID"].astype(str).tolist(),
        "InputFiles": input_files,
        "InputSHA256": {key: file_sha256(ROOT / rel) for key, rel in input_files.items()},
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(
        "\n".join(f"{file_sha256(path)}  {path.relative_to(ROOT)}" for path in [CHECKLIST, MANIFEST]) + "\n",
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
                "NextStep": "freeze_scorecard_script_and_observed_residual_input_contract",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Authorization Preflight

Status: `{status}`.

This artifact checks whether epsilon-P3 P-TauCov empirical scoring can be
authorized.

## Result

```text
ChecksPassed: {manifest['ChecksPassed']}/{manifest['ChecksTotal']}
OpenRequiredChecks: {open_required}
PTauCovScoringAuthorized: false
```

Blocking items:

```text
{chr(10).join(manifest['BlockingItems'])}
```

## Interpretation

The theoretical/protocol side is now much cleaner than before:

- epsilon-P3 specificity candidate is frozen;
- branch support is frozen from `delta_C_tau` only;
- fold/null/covariance/df/survival policies are frozen.

However, empirical scoring remains blocked until the scorecard script and the
observed residual/covariance input contract are frozen by hash.

Allowed statement:

```text
P-TauCov epsilon-P3 has passed pre-scoring protocol readiness up to the
scorecard/input-contract gate.
```

Forbidden statement:

```text
P-TauCov epsilon-P3 has produced an empirical Tau signal.
```
""",
        encoding="utf-8",
    )

    for path in [CHECKLIST, MANIFEST, SHA256, SUMMARY, DOC]:
        print(f"Wrote {path.relative_to(ROOT)}")
    print(f"P_TAUCOV_EPSILON_P3_AUTHORIZATION_PREFLIGHT_{status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
