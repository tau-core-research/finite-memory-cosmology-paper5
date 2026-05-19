#!/usr/bin/env python3
"""Validate an external nonzero source-split K1 export."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
CANDIDATE = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
OUT = EVIDENCE / "source_split_external_k1_export_readiness.csv"
LIKELIHOOD_BASELINE = ROOT / "data" / "k1" / "source_split_likelihood_native_baseline_prediction.csv"
LIKELIHOOD_COORDINATE = ROOT / "data" / "k1" / "source_split_likelihood_native_coordinate_map.csv"

REQUIRED_COLUMNS = [
    "K1TargetID",
    "SourceTargetID",
    "GridIndex",
    "z_grid",
    "x_coordinate",
    "x_mapping",
    "K1Response",
    "K1Sigma",
    "K1SourceID",
    "ProvenanceType",
    "CoordinateNative",
    "LikelihoodNative",
    "UsesPublicSN",
    "UsesPublicBAO",
    "UsesJointCovariance",
    "SameDataAmplitudeFit",
    "FittedInThisNote",
    "AmplitudePolicy",
    "Predeclared",
    "AllowedAsPrimaryK1Candidate",
    "ClaimBoundary",
]

ALLOWED_PROVENANCE_TYPES = {
    "external_reconstruction_family_mean",
    "likelihood_native_baseline",
    "independent_public_model_response",
    "external_public_response_operator",
}

FORBIDDEN_PROVENANCE_TYPES = {
    "diagnostic_control",
    "same_exported_family_response_sensitivity",
    "single_branch_response",
    "same_data_amplitude_rescue",
}


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def likelihood_native_expected() -> pd.DataFrame | None:
    if not (LIKELIHOOD_BASELINE.exists() and LIKELIHOOD_COORDINATE.exists()):
        return None
    baseline = pd.read_csv(LIKELIHOOD_BASELINE)
    coordinate = pd.read_csv(LIKELIHOOD_COORDINATE)
    merged = baseline.merge(
        coordinate[["GridIndex", "x_likelihood_native", "CoordinateMapID"]],
        on="GridIndex",
        how="inner",
    )
    return pd.DataFrame(
        {
            "TargetID": merged["BaselineVectorID"],
            "GridIndex": merged["GridIndex"].astype(int),
            "z_grid": merged["z_grid"].astype(float),
            "x_coordinate": merged["x_likelihood_native"].astype(float),
            "x_mapping": merged["CoordinateMapID"].astype(str),
        }
    )


def validate(candidate: pd.DataFrame, target: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    missing = [column for column in REQUIRED_COLUMNS if column not in candidate.columns]
    if missing:
        return [f"missing_columns:{'|'.join(missing)}"]

    provenance_values = set(candidate.get("ProvenanceType", pd.Series(dtype=str)).astype(str).str.strip())
    likelihood_native_mode = provenance_values == {"likelihood_native_baseline"}
    if likelihood_native_mode:
        expected = likelihood_native_expected()
        if expected is None:
            issues.append("likelihood_native_expected_artifacts_missing")
            usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
        else:
            usable = expected.copy()
    else:
        usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    expected_indices = set(usable["GridIndex"].astype(int))
    candidate_indices = set(candidate["GridIndex"].astype(int))
    if candidate_indices != expected_indices:
        missing_rows = sorted(expected_indices - candidate_indices)
        extra_rows = sorted(candidate_indices - expected_indices)
        if missing_rows:
            issues.append(f"missing_grid_indices:{'|'.join(map(str, missing_rows))}")
        if extra_rows:
            issues.append(f"extra_grid_indices:{'|'.join(map(str, extra_rows))}")

    if candidate["K1TargetID"].nunique() != 1:
        issues.append("multiple_k1_target_ids")
    if candidate["K1SourceID"].astype(str).str.strip().isin({"", "TO_BE_DECLARED"}).any():
        issues.append("k1_source_id_not_declared")
    if candidate["AmplitudePolicy"].astype(str).str.strip().isin({"", "TO_BE_DECLARED"}).any():
        issues.append("amplitude_policy_not_declared")

    provenance = set(candidate["ProvenanceType"].astype(str).str.strip())
    if not provenance <= ALLOWED_PROVENANCE_TYPES:
        invalid = sorted(provenance - ALLOWED_PROVENANCE_TYPES)
        issues.append(f"invalid_provenance_type:{'|'.join(invalid)}")
    if provenance & FORBIDDEN_PROVENANCE_TYPES:
        issues.append(f"forbidden_provenance_type:{'|'.join(sorted(provenance & FORBIDDEN_PROVENANCE_TYPES))}")

    for field, issue in [
        ("CoordinateNative", "coordinate_native_false"),
        ("UsesPublicSN", "public_sn_not_used"),
        ("UsesPublicBAO", "public_bao_not_used"),
        ("UsesJointCovariance", "joint_covariance_not_used"),
        ("Predeclared", "not_predeclared"),
        ("AllowedAsPrimaryK1Candidate", "not_marked_primary_candidate"),
    ]:
        if not candidate[field].map(truthy).all():
            issues.append(issue)
    for field, issue in [
        ("SameDataAmplitudeFit", "same_data_amplitude_fit"),
        ("FittedInThisNote", "fitted_in_this_note"),
    ]:
        if candidate[field].map(truthy).any():
            issues.append(issue)

    k1_response = pd.to_numeric(candidate["K1Response"], errors="coerce")
    k1_sigma = pd.to_numeric(candidate["K1Sigma"], errors="coerce")
    if k1_response.isna().any() or not np.isfinite(k1_response.to_numpy(float)).all():
        issues.append("k1_response_not_finite")
    if k1_sigma.isna().any() or not np.isfinite(k1_sigma.to_numpy(float)).all() or (k1_sigma <= 0).any():
        issues.append("k1_sigma_not_positive_finite")
    if np.isclose(k1_response.fillna(0.0).to_numpy(float), 0.0).all():
        issues.append("k1_response_identically_zero")

    merged = candidate.merge(
        usable[["TargetID", "GridIndex", "z_grid", "x_coordinate", "x_mapping"]],
        left_on="GridIndex",
        right_on="GridIndex",
        how="left",
        suffixes=("", "_expected"),
    )
    if not merged["SourceTargetID"].astype(str).eq(merged["TargetID"].astype(str)).all():
        issues.append("source_target_id_mismatch")
    for column in ["z_grid", "x_coordinate"]:
        observed = pd.to_numeric(merged[column], errors="coerce")
        expected = pd.to_numeric(merged[f"{column}_expected"], errors="coerce")
        if not np.allclose(observed.to_numpy(float), expected.to_numpy(float), rtol=0.0, atol=1e-12):
            issues.append(f"{column}_mismatch")
    if not merged["x_mapping"].astype(str).eq(merged["x_mapping_expected"].astype(str)).all():
        issues.append("x_mapping_mismatch")

    return list(dict.fromkeys(issues))


def main() -> None:
    target = pd.read_csv(TARGET)
    usable_rows = int(target["HasSNAndBAO"].astype(str).str.lower().eq("true").sum())
    if not CANDIDATE.exists():
        rows = [
            {
                "CandidatePath": str(CANDIDATE.relative_to(ROOT)),
                "Available": False,
                "AllowedForPrimaryK1": False,
                "Rows": 0,
                "UsableTargetRows": usable_rows,
                "NonzeroRows": 0,
                "K1TargetID": "",
                "ProvenanceType": "",
                "BlockingIssue": "external_k1_export_missing",
                "NextAction": "Create data/k1/source_split_external_k1_response.csv from evidence/source_split_external_k1_export_template.csv.",
                "ClaimBoundary": "external_k1_validation_gate_only_no_measurement_validation",
            }
        ]
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print(f"Wrote {OUT}")
        return

    candidate = pd.read_csv(CANDIDATE)
    issues = validate(candidate, target)
    k1_response = pd.to_numeric(candidate.get("K1Response", pd.Series(dtype=float)), errors="coerce")
    rows = [
        {
            "CandidatePath": str(CANDIDATE.relative_to(ROOT)),
            "Available": True,
            "AllowedForPrimaryK1": not issues,
            "Rows": len(candidate),
            "UsableTargetRows": usable_rows,
            "NonzeroRows": int((~np.isclose(k1_response.fillna(0.0).to_numpy(float), 0.0)).sum()),
            "K1TargetID": candidate["K1TargetID"].iloc[0] if "K1TargetID" in candidate.columns and not candidate.empty else "",
            "ProvenanceType": ";".join(sorted(set(candidate["ProvenanceType"].astype(str)))) if "ProvenanceType" in candidate.columns else "",
            "BlockingIssue": ";".join(issues),
            "NextAction": "Use as primary K1 only if validation is clean; otherwise keep source-split K2 in preflight status.",
            "ClaimBoundary": "external_k1_validation_gate_only_no_measurement_validation",
        }
    ]
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
