#!/usr/bin/env python3
"""Validate concrete epsilon-P3 branch-support freeze."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.csv"
WEIGHTS = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_weights.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_summary.csv"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.sha256"
DOC = ROOT / "docs/p_taucov_epsilon_p3_branch_support_freeze.md"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_validation.csv"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bool_from_csv(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_EPSILON_P3_BRANCH_SUPPORT_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required = [FREEZE, WEIGHTS, SUMMARY, MANIFEST, SHA256, DOC]
    for path in required:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in required):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_BRANCH_SUPPORT_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    freeze = pd.read_csv(FREEZE)
    weights = pd.read_csv(WEIGHTS)
    summary = pd.read_csv(SUMMARY).iloc[0]
    text = DOC.read_text(encoding="utf-8")

    add("status_frozen", manifest.get("Status") == "FROZEN_BRANCH_SUPPORT_NO_SCORING")
    add("summary_status_frozen", str(summary["Status"]) == "FROZEN_BRANCH_SUPPORT_NO_SCORING")
    add("q_branch_fixed_080", abs(float(manifest.get("q_branch")) - 0.80) < 1e-12)
    add("support_source_delta_only", manifest.get("BranchSupportSource") == "delta_C_Tau_only")
    add("target_residuals_not_used", manifest.get("TargetResidualsUsed") is False)
    add("p5c_outcome_not_used", manifest.get("P5CV3OutcomeUsed") is False)
    add("scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add("selected_mass_meets_q", float(summary["SelectedMass"]) >= 0.80)
    add("label_or_convention_mass_zero", float(summary["LabelOrConventionMass"]) == 0.0)
    add("freeze_rows_selected", len(freeze) == int(summary["SelectedCells"]))
    add("weights_sum_one", abs(float(weights["WBranch"].sum()) - 1.0) < 1e-9)
    add("omega_mass_matches_summary", abs(float(weights.loc[weights["OmegaBranch"].map(bool_from_csv), "WBranch"].sum()) - float(summary["SelectedMass"])) < 1e-9)

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    for path in [FREEZE, WEIGHTS, SUMMARY, MANIFEST]:
        rel = str(path.relative_to(ROOT))
        add(f"sha256_{rel}", hash_map.get(rel) == file_sha256(path))

    for phrase in [
        "delta_C_tau = P3 P3^T",
        "q_branch = 0.8",
        "PTauCovScoringAuthorized: false",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_BRANCH_SUPPORT_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_BRANCH_SUPPORT_VALID_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
