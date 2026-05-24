#!/usr/bin/env python3
"""Build the compact spectral residue scoring firewall."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SOURCE_SUMMARY = EVIDENCE / "p_taucov_compact_spectral_residue_source_summary.csv"
SOURCE_OBJECT = EVIDENCE / "p_taucov_compact_spectral_residue_source.csv"
SOURCE_SPECTRUM = EVIDENCE / "p_taucov_compact_spectral_residue_source_spectrum.csv"
SOURCE_VALIDATION = EVIDENCE / "p_taucov_compact_spectral_residue_source_validation.csv"

SCORECARD_SCRIPT_FREEZE = EVIDENCE / "p_taucov_compact_spectral_scorecard_script_freeze_summary.csv"
FOLD_POLICY = EVIDENCE / "p_taucov_compact_spectral_fold_policy_summary.csv"
NULL_POLICY = EVIDENCE / "p_taucov_compact_spectral_null_comparators_summary.csv"
DF_POLICY = EVIDENCE / "p_taucov_compact_spectral_df_covariance_policy_summary.csv"
SURVIVAL_POLICY = EVIDENCE / "p_taucov_compact_spectral_survival_kill_gates_summary.csv"
FINAL_MANIFEST = EVIDENCE / "p_taucov_compact_spectral_final_manifest_summary.csv"

OUT = EVIDENCE / "p_taucov_compact_spectral_scoring_firewall.csv"
SUMMARY = EVIDENCE / "p_taucov_compact_spectral_scoring_firewall_summary.csv"
DOC = DOCS / "p_taucov_compact_spectral_scoring_firewall.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FIREWALL_ID = "P_TAUCOV_COMPACT_SPECTRAL_SCORING_FIREWALL_v1"
CLAIM_BOUNDARY = "compact_spectral_scoring_firewall_no_scoring"


def sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def status_is(path: Path, expected: str) -> bool:
    if not path.exists():
        return False
    try:
        return str(pd.read_csv(path).iloc[0]["Status"]) == expected
    except Exception:
        return False


def main() -> int:
    source_ready = status_is(SOURCE_SUMMARY, "P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_PREFLIGHT_PASS_NO_SCORING")
    validation_ready = SOURCE_VALIDATION.exists() and bool(pd.read_csv(SOURCE_VALIDATION)["Passed"].all())
    object_ready = SOURCE_OBJECT.exists()
    spectrum_ready = SOURCE_SPECTRUM.exists()

    items = [
        ("CS-FW1_SOURCE_PREFLIGHT_PASS", source_ready, "compact spectral residue source preflight must pass"),
        ("CS-FW2_SOURCE_OBJECT_HASH_READY", object_ready, "source object exists and can be hashed"),
        ("CS-FW3_SOURCE_SPECTRUM_HASH_READY", spectrum_ready, "source spectrum exists and can be hashed"),
        ("CS-FW4_SOURCE_VALIDATION_PASS", validation_ready, "source validation must pass"),
        ("CS-FW5_SCORECARD_SCRIPT_FROZEN", SCORECARD_SCRIPT_FREEZE.exists(), "scorecard script hash must be frozen"),
        ("CS-FW6_FOLD_POLICY_FROZEN", FOLD_POLICY.exists(), "fold policy must be frozen"),
        ("CS-FW7_NULL_COMPARATORS_FROZEN", NULL_POLICY.exists(), "null comparator policy must be frozen"),
        ("CS-FW8_DF_COVARIANCE_POLICY_FROZEN", DF_POLICY.exists(), "degrees-of-freedom and covariance policy must be frozen"),
        ("CS-FW9_SURVIVAL_KILL_GATES_FROZEN", SURVIVAL_POLICY.exists(), "survival and kill gates must be frozen"),
        ("CS-FW10_FINAL_MANIFEST_READY", FINAL_MANIFEST.exists(), "final manifest must bind hashes and policies"),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FirewallID": FIREWALL_ID,
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
        "P_TAUCOV_COMPACT_SPECTRAL_SCORING_AUTHORIZATION_READY"
        if bool(table["Satisfied"].all())
        else "P_TAUCOV_COMPACT_SPECTRAL_SCORING_BLOCKED_FREEZE_REQUIRED"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FirewallID": FIREWALL_ID,
                "Status": status,
                "SatisfiedItems": int(table["Satisfied"].sum()),
                "TotalItems": len(table),
                "MissingItems": missing,
                "SourceObjectSHA256": sha256(SOURCE_OBJECT),
                "SourceSpectrumSHA256": sha256(SOURCE_SPECTRUM),
                "SourceValidationSHA256": sha256(SOURCE_VALIDATION),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Compact Spectral Scoring Firewall",
                "",
                f"Status: `{status}`",
                "",
                "The compact spectral residue source passes no-score structural",
                "preflight, but empirical scoring remains blocked until all scoring",
                "policies, hashes, and final authorization artifacts are frozen.",
                "",
                "## Satisfied / Missing",
                "",
                f"- satisfied items: `{int(table['Satisfied'].sum())}/{len(table)}`",
                f"- missing items: `{missing}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: the compact spectral source is structurally ready for scoring",
                "policy freeze work.",
                "",
                "Forbidden: this firewall authorizes empirical scoring, survival",
                "language, or Tau Core validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
