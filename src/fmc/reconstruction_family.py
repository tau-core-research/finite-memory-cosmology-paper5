"""Source-split reconstruction-family source readiness helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_RECONSTRUCTION_FAMILY_FIELDS = [
    "FamilySourceID",
    "TargetSpace",
    "Status",
    "UsesPublicSN",
    "UsesPublicBAO",
    "CoordinateNative",
    "RowAlignedToTarget",
    "FamilyResponseExported",
    "FamilySignRuleDeclared",
    "AllowedForK2Scoring",
    "BlockingIssue",
    "NextAction",
]

RECONSTRUCTION_FAMILY_EXPORT_COLUMNS = [
    "ExportID",
    "FamilyID",
    "FamilyType",
    "SourceProductID",
    "TargetID",
    "GridIndex",
    "z_grid",
    "x_coordinate",
    "x_mapping",
    "ResponseValue",
    "ResponseSigma",
    "ResponseSign",
    "CoordinateNative",
    "UsesPublicSN",
    "UsesPublicBAO",
    "FittedInThisNote",
    "ClaimBoundary",
]


def load_reconstruction_family_registry(path: str | Path) -> pd.DataFrame:
    """Load and validate the reconstruction-family source registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_RECONSTRUCTION_FAMILY_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"reconstruction-family registry missing columns: {missing}")
    return df


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def reconstruction_family_issues(row: pd.Series) -> list[str]:
    """Return issues blocking scoring-grade reconstruction-family use."""
    issues: list[str] = []
    if str(row.get("Status", "")).strip().lower() != "available":
        issues.append("family_source_not_available")
    for field, issue in [
        ("UsesPublicSN", "public_sn_not_used"),
        ("UsesPublicBAO", "public_bao_not_used"),
        ("CoordinateNative", "coordinate_native_false"),
        ("RowAlignedToTarget", "not_row_aligned_to_target"),
        ("FamilyResponseExported", "family_response_not_exported"),
        ("FamilySignRuleDeclared", "family_sign_rule_not_declared"),
    ]:
        if not _truthy(row.get(field, "")):
            issues.append(issue)
    blocking = str(row.get("BlockingIssue", "")).strip()
    if blocking:
        issues.extend(part for part in blocking.split(";") if part)
    if _truthy(row.get("AllowedForK2Scoring", "")) and issues:
        issues.append("allowed_despite_blocking_issues")
    return list(dict.fromkeys(issues))


def reconstruction_family_allowed(row: pd.Series) -> bool:
    """Return whether a reconstruction-family source is scoring-grade."""
    return _truthy(row.get("AllowedForK2Scoring", "")) and not reconstruction_family_issues(row)


def reconstruction_family_export_schema() -> pd.DataFrame:
    """Return the required long-format reconstruction-family export schema."""
    descriptions = {
        "ExportID": "Stable identifier for the exported reconstruction-family response table.",
        "FamilyID": "Public reconstruction-family identifier; at least two families are required.",
        "FamilyType": "Family class, such as SN_branch, BAO_branch, joint_reconstruction, or backreaction_control.",
        "SourceProductID": "Public source product or manifest identifier used to derive the response.",
        "TargetID": "Coordinate-native source-split target identifier.",
        "GridIndex": "Integer row key matching the coordinate-native target rows.",
        "z_grid": "Target-row redshift.",
        "x_coordinate": "Coordinate-native depth coordinate used by the source-split target.",
        "x_mapping": "Coordinate mapping identifier; must match the target-space mapping.",
        "ResponseValue": "Family response value in the source-split benchmark space.",
        "ResponseSigma": "Uncertainty proxy or covariance-derived marginal sigma for the response.",
        "ResponseSign": "Sign of the response value: -1, 0, or 1.",
        "CoordinateNative": "True only if the response is exported in the coordinate-native target space.",
        "UsesPublicSN": "True when the family uses public SN input products.",
        "UsesPublicBAO": "True when the family uses public BAO input products.",
        "FittedInThisNote": "Must be false for scoring-grade locked benchmark inputs.",
        "ClaimBoundary": "Must state that the export is benchmark input only, not measurement validation.",
    }
    validation = {
        "ExportID": "nonempty string",
        "FamilyID": "nonempty string; count distinct FamilyID >= 2",
        "FamilyType": "nonempty string",
        "SourceProductID": "nonempty string",
        "TargetID": "must match target rows",
        "GridIndex": "integer; every usable target GridIndex must appear for every FamilyID",
        "z_grid": "numeric; must match target row",
        "x_coordinate": "numeric; must match target row",
        "x_mapping": "must match target row x_mapping",
        "ResponseValue": "finite numeric",
        "ResponseSigma": "positive finite numeric",
        "ResponseSign": "one of -1, 0, 1 and consistent with ResponseValue",
        "CoordinateNative": "must be true",
        "UsesPublicSN": "boolean",
        "UsesPublicBAO": "boolean",
        "FittedInThisNote": "must be false",
        "ClaimBoundary": "must not contain discovery or validation claim",
    }
    return pd.DataFrame(
        [
            {
                "ColumnName": column,
                "Required": True,
                "Type": "boolean" if column in {"CoordinateNative", "UsesPublicSN", "UsesPublicBAO", "FittedInThisNote"} else "string_or_numeric",
                "Description": descriptions[column],
                "ValidationRule": validation[column],
            }
            for column in RECONSTRUCTION_FAMILY_EXPORT_COLUMNS
        ]
    )


def reconstruction_family_export_template() -> pd.DataFrame:
    """Return an empty template with the required export columns."""
    return pd.DataFrame(columns=RECONSTRUCTION_FAMILY_EXPORT_COLUMNS)


def response_sign(value: object) -> int:
    """Return the canonical response sign for a numeric value."""
    number = float(value)
    if number > 0.0:
        return 1
    if number < 0.0:
        return -1
    return 0


def family_sign_status(signs: list[int]) -> str:
    """Classify a row-level reconstruction-family sign set."""
    nonzero = [int(sign) for sign in signs if int(sign) != 0]
    if not nonzero:
        return "FAMILY_SIGN_ZERO_OR_MISSING_WARNING"
    if len(set(nonzero)) == 1:
        return "FAMILY_SIGN_STABLE"
    return "FAMILY_SIGN_UNSTABLE_WARNING"


def validate_reconstruction_family_export(candidate: pd.DataFrame, target: pd.DataFrame) -> list[str]:
    """Validate a future reconstruction-family export against target rows."""
    issues: list[str] = []
    missing = [column for column in RECONSTRUCTION_FAMILY_EXPORT_COLUMNS if column not in candidate.columns]
    if missing:
        issues.append("missing_columns:" + "|".join(missing))
        return issues

    if candidate.empty:
        issues.append("candidate_empty")
        return issues

    family_count = candidate["FamilyID"].nunique()
    if family_count < 2:
        issues.append("less_than_two_reconstruction_families")

    usable_target = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")]
    target_keys = set(usable_target["GridIndex"].astype(int).tolist())
    for family_id, group in candidate.groupby("FamilyID"):
        family_keys = set(group["GridIndex"].astype(int).tolist())
        missing_keys = sorted(target_keys - family_keys)
        extra_keys = sorted(family_keys - target_keys)
        if missing_keys:
            issues.append(f"family_{family_id}_missing_target_rows:{'|'.join(map(str, missing_keys))}")
        if extra_keys:
            issues.append(f"family_{family_id}_extra_target_rows:{'|'.join(map(str, extra_keys))}")

    if not candidate["CoordinateNative"].map(_truthy).all():
        issues.append("coordinate_native_false")
    if candidate["FittedInThisNote"].map(_truthy).any():
        issues.append("fitted_in_this_note_true")

    signs = pd.to_numeric(candidate["ResponseSign"], errors="coerce")
    if not signs.isin([-1, 0, 1]).all():
        issues.append("invalid_response_sign")
    values_for_sign = pd.to_numeric(candidate["ResponseValue"], errors="coerce")
    expected_signs = values_for_sign.map(lambda value: response_sign(value) if pd.notna(value) else None)
    if not signs.equals(expected_signs):
        issues.append("response_sign_mismatch")

    sigmas = pd.to_numeric(candidate["ResponseSigma"], errors="coerce")
    if sigmas.isna().any() or (sigmas <= 0).any():
        issues.append("invalid_response_sigma")

    if values_for_sign.isna().any():
        issues.append("invalid_response_value")

    return list(dict.fromkeys(issues))
