#!/usr/bin/env python3
"""Build a scoring firewall for the expanded parent-operator PSD artifact."""

from __future__ import annotations

from pathlib import Path

import hashlib

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

PREFLIGHT = EVIDENCE / "p_taucov_expanded_parent_operator_psd_preflight_summary.csv"
CANDIDATE = EVIDENCE / "p_taucov_expanded_parent_operator_psd_candidate.csv"
SOURCE = EVIDENCE / "p_taucov_expanded_parent_operator_source_matrix.csv"
DOMAIN = EVIDENCE / "p_taucov_expanded_parent_operator_domain_coordinates.csv"

OUT = EVIDENCE / "p_taucov_expanded_parent_operator_scoring_firewall.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_expanded_parent_operator_scoring_firewall_summary.csv"
DOC = DOCS / "p_taucov_expanded_parent_operator_scoring_firewall.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_FIREWALL_v1"
CLAIM_BOUNDARY = "expanded_parent_operator_scoring_firewall_no_scoring"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    preflight = pd.read_csv(PREFLIGHT).iloc[0]
    structural_ready = str(preflight["Status"]) == "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_PASS_NO_SCORING"
    candidate_exists = CANDIDATE.exists()
    source_exists = SOURCE.exists()
    domain_exists = DOMAIN.exists()

    items = [
        ("ESO-FW1_STRUCTURAL_PREFLIGHT_PASS", structural_ready, "expanded PSD structural preflight passes"),
        ("ESO-FW2_CANDIDATE_HASH_READY", candidate_exists, "expanded PSD candidate matrix exists and can be hashed"),
        ("ESO-FW3_SOURCE_HASH_READY", source_exists, "expanded parent-operator source matrix exists and can be hashed"),
        ("ESO-FW4_DOMAIN_HASH_READY", domain_exists, "expanded domain coordinates exist and can be hashed"),
        ("ESO-FW5_SCORECARD_SCRIPT_FROZEN", False, "expanded scorecard script must be frozen separately"),
        ("ESO-FW6_FOLD_POLICY_FROZEN", False, "fold policy must be explicitly frozen for the expanded object"),
        ("ESO-FW7_NULL_COMPARATORS_FROZEN", False, "null comparators must be frozen for expanded non-outcome axes"),
        ("ESO-FW8_DF_COVARIANCE_POLICY_FROZEN", False, "degrees-of-freedom and covariance policy must be frozen"),
        ("ESO-FW9_SURVIVAL_KILL_GATES_FROZEN", False, "survival and kill gates must be frozen before scoring"),
        ("ESO-FW10_FINAL_MANIFEST_READY", False, "final manifest must bind all hashes and policies"),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "FirewallItemID": item_id,
                "Satisfied": bool(satisfied),
                "Requirement": requirement,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for item_id, satisfied, requirement in items
        ]
    )
    table.to_csv(OUT, index=False)
    missing = ";".join(table.loc[~table["Satisfied"].astype(bool), "FirewallItemID"].astype(str))
    status = (
        "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_AUTHORIZATION_READY"
        if bool(table["Satisfied"].all())
        else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_BLOCKED_FREEZE_REQUIRED"
    )
    hashes = {
        "CandidateSHA256": sha256(CANDIDATE) if candidate_exists else "",
        "SourceSHA256": sha256(SOURCE) if source_exists else "",
        "DomainSHA256": sha256(DOMAIN) if domain_exists else "",
    }
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "SatisfiedItems": int(table["Satisfied"].sum()),
                "TotalItems": len(table),
                "MissingItems": missing,
                **hashes,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Expanded Parent-Operator Scoring Firewall

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

The expanded parent-operator PSD artifact passes structural no-score
specificity preflight. This firewall records what must still be frozen before
any empirical scorecard may be run.

## Current Ready Items

- structural preflight pass: `{structural_ready}`
- candidate hash ready: `{candidate_exists}`
- source hash ready: `{source_exists}`
- domain hash ready: `{domain_exists}`

## Missing Before Scoring

```text
{missing}
```

Required missing freezes:

- expanded scorecard script hash;
- fold policy;
- null comparator policy for expanded non-outcome axes;
- degrees-of-freedom and covariance policy;
- survival and kill gates;
- final manifest binding all hashes and policies.

## Claim Boundary

Allowed statement:

> The expanded parent-operator artifact is structurally ready for a future
> scoring-freeze packet.

Forbidden statement:

> This firewall authorizes empirical scoring, survival language, or Tau Core
> validation.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
