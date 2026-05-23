#!/usr/bin/env python3
"""Validate epsilon-P3 coordinate bridge freeze."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge_summary.csv"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.sha256"
DOC = ROOT / "docs/p_taucov_epsilon_p3_coordinate_bridge.md"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge_validation.csv"


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
        records.append({"AuditID": "P_TAUCOV_EPSILON_P3_COORDINATE_BRIDGE_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [BRIDGE, SUMMARY, MANIFEST, SHA256, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [BRIDGE, SUMMARY, MANIFEST, SHA256, DOC]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_COORDINATE_BRIDGE_INVALID")
        return 1

    bridge = pd.read_csv(BRIDGE)
    summary = pd.read_csv(SUMMARY).iloc[0]
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    text = DOC.read_text(encoding="utf-8")
    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}

    add("status_frozen", manifest.get("Status") == "FROZEN_COORDINATE_BRIDGE_NO_SCORING")
    add("summary_status_frozen", str(summary["Status"]) == "FROZEN_COORDINATE_BRIDGE_NO_SCORING")
    add("empirical_rows_36", int(summary["EmpiricalRows"]) == 36)
    add("tau_coordinates_8", int(summary["TauCoordinates"]) == 8)
    add("active_columns_4", int(summary["ActiveBridgeColumns"]) == 4)
    add("bridge_rank_at_least_3", int(summary["BridgeRank"]) >= 3)
    add("no_target_residuals", manifest.get("TargetResidualsUsed") is False and not bridge["UsesTargetResiduals"].map(bool_from_csv).any())
    add("no_p5c_outcome", manifest.get("P5CV3OutcomeUsed") is False and not bridge["UsesP5Cv3Outcome"].map(bool_from_csv).any())
    add("scoring_not_authorized", manifest.get("PTauCovScoringAuthorized") is False and not bridge["PTauCovScoringAuthorized"].map(bool_from_csv).any())
    add("sha_bridge", hash_map.get(str(BRIDGE.relative_to(ROOT))) == file_sha256(BRIDGE))
    add("sha_summary", hash_map.get(str(SUMMARY.relative_to(ROOT))) == file_sha256(SUMMARY))
    add("sha_manifest", hash_map.get(str(MANIFEST.relative_to(ROOT))) == file_sha256(MANIFEST))
    for phrase in ["target-blind bridge", "PHI_PARENT_SOURCE", "P_MORPH_PROJECTION", "does not use target residuals", "Forbidden statement"]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_COORDINATE_BRIDGE_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_COORDINATE_BRIDGE_VALID_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
