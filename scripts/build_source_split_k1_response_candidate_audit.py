#!/usr/bin/env python3
"""Build nonzero source-split K1 response candidate audit from family export."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CANDIDATE = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
OUT = EVIDENCE / "source_split_k1_response_candidate_audit.csv"
SUMMARY = EVIDENCE / "source_split_k1_response_candidate_summary.csv"


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def candidate_rows(target: pd.DataFrame, families: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    for _, target_row in usable.sort_values("GridIndex").iterrows():
        grid_index = int(target_row["GridIndex"])
        group = families[families["GridIndex"].astype(int).eq(grid_index)]
        values = {
            str(row["FamilyID"]): float(row["ResponseValue"])
            for _, row in group.iterrows()
        }
        sn = values.get("RFAM_SN_RESIDUAL_BRANCH", np.nan)
        bao = values.get("RFAM_BAO_RESIDUAL_BRANCH", np.nan)
        common_mean = float(np.mean([sn, bao]))
        candidates = [
            {
                "K1CandidateID": "K1_ZERO_CONTRAST_CURRENT",
                "K1Response": 0.0,
                "CandidateClass": "fair_null",
                "AllowedAsPrimaryK1": True,
                "Definition": "zero source-split branch contrast",
                "Risk": "degenerate_for_multiplicative_k2",
            },
            {
                "K1CandidateID": "K1_FAMILY_COMMON_MODE_MEAN",
                "K1Response": common_mean,
                "CandidateClass": "candidate_k1_sensitivity",
                "AllowedAsPrimaryK1": False,
                "Definition": "mean of SN and BAO reconstruction-family responses",
                "Risk": "uses same exported family responses; needs predeclared physical interpretation before primary use",
            },
            {
                "K1CandidateID": "K1_SN_BRANCH_RESPONSE",
                "K1Response": sn,
                "CandidateClass": "diagnostic_control",
                "AllowedAsPrimaryK1": False,
                "Definition": "SN residual branch response",
                "Risk": "single-branch control, not source-split no-memory target",
            },
            {
                "K1CandidateID": "K1_BAO_BRANCH_RESPONSE",
                "K1Response": bao,
                "CandidateClass": "diagnostic_control",
                "AllowedAsPrimaryK1": False,
                "Definition": "BAO residual branch response",
                "Risk": "single-branch control, not source-split no-memory target",
            },
        ]
        for candidate in candidates:
            value = float(candidate["K1Response"])
            rows.append(
                {
                    "AuditID": "SOURCE_SPLIT_K1_RESPONSE_CANDIDATE_AUDIT_V1",
                    "K1CandidateID": candidate["K1CandidateID"],
                    "CandidateClass": candidate["CandidateClass"],
                    "TargetID": target_row["TargetID"],
                    "GridIndex": grid_index,
                    "z_grid": float(target_row["z_grid"]),
                    "x_coordinate": float(target_row["x_coordinate"]),
                    "SourceSplitResponse": float(target_row["SourceSplitResponse"]),
                    "SNFamilyResponse": sn,
                    "BAOFamilyResponse": bao,
                    "K1Response": value,
                    "K1ResponseSign": sign(value),
                    "K1Nonzero": not np.isclose(value, 0.0),
                    "AllowedAsPrimaryK1": bool(candidate["AllowedAsPrimaryK1"]),
                    "Definition": candidate["Definition"],
                    "Risk": candidate["Risk"],
                    "RequiredNextCheck": "score as sensitivity only unless AllowedAsPrimaryK1 is true and provenance is predeclared",
                    "ClaimBoundary": "k1_candidate_audit_only_no_measurement_validation",
                }
            )
    return rows


def main() -> None:
    target = pd.read_csv(TARGET)
    families = pd.read_csv(CANDIDATE)
    output = pd.DataFrame(candidate_rows(target, families))
    output.to_csv(OUT, index=False)

    summary_rows = []
    for candidate_id, group in output.groupby("K1CandidateID", sort=False):
        summary_rows.append(
            {
                "AuditID": "SOURCE_SPLIT_K1_RESPONSE_CANDIDATE_AUDIT_V1",
                "K1CandidateID": candidate_id,
                "Rows": len(group),
                "NonzeroRows": int(group["K1Nonzero"].sum()),
                "MeanAbsK1Response": float(np.mean(np.abs(group["K1Response"].astype(float)))),
                "AllowedAsPrimaryK1": bool(group["AllowedAsPrimaryK1"].all()),
                "CandidateClass": group["CandidateClass"].iloc[0],
                "Risk": group["Risk"].iloc[0],
                "ClaimBoundary": "k1_candidate_audit_only_no_measurement_validation",
            }
        )
    pd.DataFrame(summary_rows).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
