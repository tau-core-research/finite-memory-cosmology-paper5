#!/usr/bin/env python3
"""Validate epsilon-P3 P-TauCov scoring policy freeze."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_scoring_policy_freeze.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze_summary.csv"
FOLDS = ROOT / "evidence/p_taucov_epsilon_p3_fold_policy.csv"
NULLS = ROOT / "evidence/p_taucov_epsilon_p3_null_policy.csv"
COV_DF = ROOT / "evidence/p_taucov_epsilon_p3_covariance_df_policy.csv"
GATES = ROOT / "evidence/p_taucov_epsilon_p3_survival_kill_gates.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze_validation.csv"


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
                "AuditID": "P_TAUCOV_EPSILON_P3_SCORING_POLICY_FREEZE_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    required = [DOC, MANIFEST, SHA256, SUMMARY, FOLDS, NULLS, COV_DF, GATES]
    for path in required:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in required):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_SCORING_POLICY_FREEZE_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    folds = pd.read_csv(FOLDS)
    nulls = pd.read_csv(NULLS)
    cov_df = pd.read_csv(COV_DF)
    gates = pd.read_csv(GATES)
    summary = pd.read_csv(SUMMARY).iloc[0]
    text = DOC.read_text(encoding="utf-8")

    add("status_frozen_no_auth", manifest.get("Status") == "SCORING_POLICIES_FROZEN_NO_AUTHORIZATION")
    add("fold_policy_frozen", manifest.get("FoldPolicyFrozen") is True)
    add("null_policy_frozen", manifest.get("NullPolicyFrozen") is True)
    add("cov_df_policy_frozen", manifest.get("CovarianceDFPolicyFrozen") is True)
    add("gates_frozen", manifest.get("SurvivalKillGatesFrozen") is True)
    add("branch_support_frozen", manifest.get("BranchSupportFrozen") is True)
    add("scorecard_not_frozen", manifest.get("ScorecardScriptFrozen") is False)
    add("scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False)
    add("summary_no_scoring", not bool_from_csv(summary["PTauCovScoringAuthorized"]))
    add("has_primary_folds", int(folds["Primary"].map(bool_from_csv).sum()) >= 2)
    add("random_shuffle_primary_forbidden", folds.loc[folds["Primary"].map(bool_from_csv), "RandomRowShufflePrimaryForbidden"].map(bool_from_csv).all())
    add("has_required_nulls", len(nulls) >= 9 and nulls["Required"].map(bool_from_csv).all())
    add("signed_diagnostic_only", cov_df["SignedDiagnosticPolicy"].astype(str).str.contains("diagnostic").any())
    add("has_survival_and_kill_gates", gates["GateID"].astype(str).str.startswith("G").any() and gates["GateID"].astype(str).str.startswith("K").any())
    add("required_gates_all_required", gates["Required"].map(bool_from_csv).all())

    for key, rel in manifest.get("InputFiles", {}).items():
        path = ROOT / rel
        add(f"input_exists_{key}", path.exists())
        if path.exists():
            add(f"input_hash_{key}", manifest.get("InputSHA256", {}).get(key) == file_sha256(path))

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    for path in [FOLDS, NULLS, COV_DF, GATES, MANIFEST]:
        rel = str(path.relative_to(ROOT))
        add(f"sha256_{rel}", hash_map.get(rel) == file_sha256(path))

    for phrase in [
        "scoring policies frozen",
        "PTauCovScoringAuthorized: false",
        "scorecard script and final authorization manifest are not frozen",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_SCORING_POLICY_FREEZE_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_SCORING_POLICY_FREEZE_VALID_NO_AUTHORIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
