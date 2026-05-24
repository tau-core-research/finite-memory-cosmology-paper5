#!/usr/bin/env python3
"""Validate the compact spectral residue scoring firewall."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_compact_spectral_scoring_firewall.csv"
SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_scoring_firewall_summary.csv"
DOC = ROOT / "docs/p_taucov_compact_spectral_scoring_firewall.md"
OUT = ROOT / "evidence/p_taucov_compact_spectral_scoring_firewall_validation.csv"

AUDIT_ID = "P_TAUCOV_COMPACT_SPECTRAL_SCORING_FIREWALL_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_COMPACT_SPECTRAL_SCORING_AUTHORIZATION_READY"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": True,
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        missing_value = summary["MissingItems"]
        missing = set() if pd.isna(missing_value) else set(str(missing_value).split(";"))
        add("status_authorization_ready", str(summary["Status"]) == EXPECTED_STATUS)
        add("ten_of_ten_satisfied", int(summary["SatisfiedItems"]) == 10 and int(summary["TotalItems"]) == 10)
        add("no_missing_items", missing == set())
        add("source_items_satisfied", bool(table.loc[table["FirewallItemID"].isin(["CS-FW1_SOURCE_PREFLIGHT_PASS", "CS-FW2_SOURCE_OBJECT_HASH_READY", "CS-FW3_SOURCE_SPECTRUM_HASH_READY", "CS-FW4_SOURCE_VALIDATION_PASS"]), "Satisfied"].all()))
        add("scoring_false", bool(summary["ScoringAuthorized"]) is False)
        add("survival_false", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_false", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("hashes_present", all(str(summary[col]) for col in ["SourceObjectSHA256", "SourceSpectrumSHA256", "SourceValidationSHA256"]))
        add("doc_forbids_scoring", "Forbidden" in doc and "authorizes empirical scoring" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_COMPACT_SPECTRAL_SCORING_FIREWALL_VALID" if ok else "P_TAUCOV_COMPACT_SPECTRAL_SCORING_FIREWALL_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
