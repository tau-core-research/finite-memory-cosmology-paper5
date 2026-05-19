"""Validation helpers for source-native backreaction exports."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .backreaction import REQUIRED_RECONSTRUCTION_COLUMNS, omega_r_plus_3omega_q


SOURCE_NATIVE_FAMILY_IDS = [
    "QR_CRITERIA_1",
    "QR_CRITERIA_2",
    "QR_CRITERIA_3",
    "QR_DESI",
    "QR_EBOSS",
]

RECONSTRUCTION_VECTOR_COLUMNS = [
    "FamilyID",
    "SampleID",
    "z",
    *REQUIRED_RECONSTRUCTION_COLUMNS[1:],
    "Source",
    "SelectionRule",
    "ClaimBoundary",
]

BACKREACTION_VECTOR_COLUMNS = [
    "FamilyID",
    "SampleID",
    "z",
    "Omega_R_plus_3Omega_Q",
    "Source",
    "ClaimBoundary",
]

BOOTSTRAP_SAMPLE_COLUMNS = [
    "FamilyID",
    "SampleID",
    "z",
    "Omega_R_plus_3Omega_Q",
    "Source",
    "ClaimBoundary",
]

OMEGA_COVARIANCE_LONG_COLUMNS = [
    "FamilyID",
    "z_i",
    "z_j",
    "Covariance",
    "Source",
    "ClaimBoundary",
]

SELECTION_METADATA_COLUMNS = [
    "FamilyID",
    "DataCombination",
    "CriteriaSet",
    "Algorithm",
    "ExpressionID",
    "SelectionRule",
    "UsesPublicSN",
    "UsesPublicBAO",
    "FittedInThisNote",
    "ClaimBoundary",
]


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def empty_reconstruction_vector_template() -> pd.DataFrame:
    """Return an empty template for source-native reconstruction exports."""
    return pd.DataFrame(columns=RECONSTRUCTION_VECTOR_COLUMNS)


def empty_selection_metadata_template() -> pd.DataFrame:
    """Return an empty template for source-native family metadata exports."""
    return pd.DataFrame(columns=SELECTION_METADATA_COLUMNS)


def empty_bootstrap_sample_template() -> pd.DataFrame:
    """Return an empty template for source-native omega bootstrap samples."""
    return pd.DataFrame(columns=BOOTSTRAP_SAMPLE_COLUMNS)


def empty_omega_covariance_template() -> pd.DataFrame:
    """Return an empty long-format template for source-native omega covariance."""
    return pd.DataFrame(columns=OMEGA_COVARIANCE_LONG_COLUMNS)


def validate_reconstruction_vector(df: pd.DataFrame) -> list[str]:
    """Return issues for a source-native reconstruction-vector export."""
    issues: list[str] = []
    missing = [col for col in RECONSTRUCTION_VECTOR_COLUMNS if col not in df.columns]
    if missing:
        issues.append("missing_columns:" + "|".join(missing))
        return issues
    if df.empty:
        issues.append("reconstruction_vector_empty")
        return issues

    family_ids = set(df["FamilyID"].astype(str))
    unknown = sorted(family_ids - set(SOURCE_NATIVE_FAMILY_IDS))
    if unknown:
        issues.append("unknown_family_ids:" + "|".join(unknown))

    for family_id in SOURCE_NATIVE_FAMILY_IDS:
        if family_id not in family_ids:
            issues.append(f"missing_family:{family_id}")

    numeric_cols = ["SampleID", "z", "D", "D_prime", "D_double_prime", "H_D", "H_D_prime"]
    for col in numeric_cols:
        numeric = pd.to_numeric(df[col], errors="coerce")
        if numeric.isna().any():
            issues.append(f"invalid_numeric_column:{col}")

    if (pd.to_numeric(df["D"], errors="coerce") == 0.0).any():
        issues.append("zero_D_values")
    if (pd.to_numeric(df["H_D"], errors="coerce") == 0.0).any():
        issues.append("zero_H_D_values")

    overclaim_terms = [
        r"observational\s+discovery",
        r"measurement\s+validation\s+allowed",
        r"tau\s+core\s+proven",
        r"detected\s+finite\s+memory",
        r"\bproven\b",
        r"\bconfirmed\b",
    ]
    overclaim_pattern = "|".join(overclaim_terms)
    if df["ClaimBoundary"].astype(str).str.contains(overclaim_pattern, case=False, regex=True).any():
        issues.append("claim_boundary_overclaim_language")

    return list(dict.fromkeys(issues))


def validate_selection_metadata(df: pd.DataFrame) -> list[str]:
    """Return issues for source-native selection metadata."""
    issues: list[str] = []
    missing = [col for col in SELECTION_METADATA_COLUMNS if col not in df.columns]
    if missing:
        issues.append("missing_columns:" + "|".join(missing))
        return issues
    if df.empty:
        issues.append("selection_metadata_empty")
        return issues
    family_ids = set(df["FamilyID"].astype(str))
    for family_id in SOURCE_NATIVE_FAMILY_IDS:
        if family_id not in family_ids:
            issues.append(f"missing_family_metadata:{family_id}")
    if df["FittedInThisNote"].map(truthy).any():
        issues.append("fitted_in_this_note_true")
    if not df["UsesPublicSN"].map(truthy).any():
        issues.append("no_family_uses_public_sn")
    if not df["UsesPublicBAO"].map(truthy).any():
        issues.append("no_family_uses_public_bao")
    return list(dict.fromkeys(issues))


def validate_bootstrap_samples(df: pd.DataFrame) -> list[str]:
    """Return issues for source-native omega bootstrap samples."""
    issues: list[str] = []
    missing = [col for col in BOOTSTRAP_SAMPLE_COLUMNS if col not in df.columns]
    if missing:
        issues.append("missing_columns:" + "|".join(missing))
        return issues
    if df.empty:
        issues.append("bootstrap_samples_empty")
        return issues
    family_ids = set(df["FamilyID"].astype(str))
    for family_id in SOURCE_NATIVE_FAMILY_IDS:
        if family_id not in family_ids:
            issues.append(f"missing_family_bootstrap:{family_id}")
    for col in ["SampleID", "z", "Omega_R_plus_3Omega_Q"]:
        numeric = pd.to_numeric(df[col], errors="coerce")
        if numeric.isna().any():
            issues.append(f"invalid_numeric_column:{col}")
    if df.groupby("FamilyID")["SampleID"].nunique().min() < 2:
        issues.append("less_than_two_samples_for_at_least_one_family")
    return list(dict.fromkeys(issues))


def validate_omega_covariance_long(df: pd.DataFrame) -> list[str]:
    """Return issues for a long-format source-native omega covariance export."""
    issues: list[str] = []
    missing = [col for col in OMEGA_COVARIANCE_LONG_COLUMNS if col not in df.columns]
    if missing:
        issues.append("missing_columns:" + "|".join(missing))
        return issues
    if df.empty:
        issues.append("omega_covariance_empty")
        return issues
    family_ids = set(df["FamilyID"].astype(str))
    for family_id in SOURCE_NATIVE_FAMILY_IDS:
        if family_id not in family_ids:
            issues.append(f"missing_family_covariance:{family_id}")
    for col in ["z_i", "z_j", "Covariance"]:
        numeric = pd.to_numeric(df[col], errors="coerce")
        if numeric.isna().any():
            issues.append(f"invalid_numeric_column:{col}")
    for family_id, group in df.groupby("FamilyID"):
        piv = group.pivot_table(index="z_i", columns="z_j", values="Covariance", aggfunc="first")
        if piv.shape[0] != piv.shape[1]:
            issues.append(f"family_{family_id}_covariance_not_square")
            continue
        matrix = piv.to_numpy(float)
        if not np.allclose(matrix, matrix.T, atol=1e-8, rtol=1e-8):
            issues.append(f"family_{family_id}_covariance_not_symmetric")
        eig_min = float(np.linalg.eigvalsh(0.5 * (matrix + matrix.T)).min())
        if eig_min < -1e-8:
            issues.append(f"family_{family_id}_covariance_negative_eigenvalue")
    return list(dict.fromkeys(issues))


def build_backreaction_vector(reconstruction: pd.DataFrame) -> pd.DataFrame:
    """Compute Omega_R + 3 Omega_Q for a valid source-native reconstruction."""
    issues = validate_reconstruction_vector(reconstruction)
    if issues:
        raise ValueError("invalid source-native reconstruction vector: " + ";".join(issues))
    out = reconstruction[["FamilyID", "SampleID", "z", "Source", "ClaimBoundary"]].copy()
    out["Omega_R_plus_3Omega_Q"] = omega_r_plus_3omega_q(
        reconstruction["z"],
        reconstruction["D"],
        reconstruction["D_prime"],
        reconstruction["D_double_prime"],
        reconstruction["H_D"],
        reconstruction["H_D_prime"],
    )
    return out[BACKREACTION_VECTOR_COLUMNS]


def load_csv_if_exists(path: str | Path) -> pd.DataFrame | None:
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return None
    return pd.read_csv(p)
