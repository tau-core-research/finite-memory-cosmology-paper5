#!/usr/bin/env python3
"""Smoke-test the source-native backreaction ingestion and bridge scoring path.

The generated fixture is artificial and is never used as evidence for a
measurement claim. Its only purpose is to verify that a validly shaped
source-native export can pass validation, produce the fixed-formula
backreaction vector, and enter the locked-K2 bridge scorer without changing K2.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_native_backreaction import (
    SOURCE_NATIVE_FAMILY_IDS,
    build_backreaction_vector,
    validate_reconstruction_vector,
    validate_selection_metadata,
)

EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROUTES = [
    {
        "RouteID": "PUBLIC_PROXY_WHITENED_STANDARDIZED",
        "Vector": EVIDENCE / "whitened_standardized_branch_contrast_vector.csv",
        "Whitening": EVIDENCE / "whitened_standardized_branch_contrast_matrix.csv",
        "Covariance": None,
    },
    {
        "RouteID": "REGISTERED_SHRINKAGE_WHITENED",
        "Vector": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_vector.csv",
        "Whitening": None,
        "Covariance": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_covariance.csv",
    },
]

OUT_RECON = EVIDENCE / "source_native_backreaction_fixture_reconstruction_vector.csv"
OUT_META = EVIDENCE / "source_native_backreaction_fixture_selection_metadata.csv"
OUT_OMEGA = EVIDENCE / "source_native_backreaction_fixture_omega_vector.csv"
OUT_SCORE = EVIDENCE / "source_native_backreaction_fixture_bridge_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "source_native_backreaction_fixture_smoke_summary.csv"
OUT_DOC = DOCS / "source_native_backreaction_fixture_smoke_test.md"


def load_whitening(route: dict[str, object], grid_indices: list[int]) -> np.ndarray:
    if route["Whitening"] is not None:
        matrix = pd.read_csv(Path(str(route["Whitening"])))
        return matrix[[str(idx) for idx in grid_indices]].to_numpy(float)
    cov_df = pd.read_csv(Path(str(route["Covariance"])))
    cov = cov_df[[str(idx) for idx in grid_indices]].to_numpy(float)
    eigvals, eigvecs = np.linalg.eigh(0.5 * (cov + cov.T))
    return eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T


def chi2(y: np.ndarray, pred: np.ndarray) -> float:
    residual = y - pred
    return float(residual @ residual)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) == 0.0 or np.std(b) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def make_fixture_reconstruction(z_grid: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for family_index, family_id in enumerate(SOURCE_NATIVE_FAMILY_IDS):
        for sample_id in [0, 1]:
            amp = 1.0 + 0.04 * family_index + 0.02 * sample_id
            for z in z_grid:
                # Smooth positive toy functions; not cosmological claims.
                D = amp * z / (1.0 + 0.25 * z)
                Dp = amp / ((1.0 + 0.25 * z) ** 2)
                Dpp = -0.5 * amp / ((1.0 + 0.25 * z) ** 3)
                hd = 1.0 + 0.55 * z + 0.04 * z * z
                hdp = 0.55 + 0.08 * z
                rows.append(
                    {
                        "FamilyID": family_id,
                        "SampleID": sample_id,
                        "z": float(z),
                        "D": float(D),
                        "D_prime": float(Dp),
                        "D_double_prime": float(Dpp),
                        "H_D": float(hd),
                        "H_D_prime": float(hdp),
                        "Source": "fixture_smoke_test_not_observational_data",
                        "SelectionRule": "fixture_only",
                        "ClaimBoundary": "source_native_fixture_smoke_test_no_measurement_validation",
                    }
                )
    return pd.DataFrame(rows)


def make_fixture_metadata() -> pd.DataFrame:
    rows = []
    for family_id in SOURCE_NATIVE_FAMILY_IDS:
        rows.append(
            {
                "FamilyID": family_id,
                "DataCombination": "fixture_only",
                "CriteriaSet": family_id,
                "Algorithm": "fixture_generator",
                "ExpressionID": f"{family_id}_fixture_expression",
                "SelectionRule": "fixture_only_no_selection_claim",
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "FittedInThisNote": False,
                "ClaimBoundary": "source_native_fixture_smoke_test_no_measurement_validation",
            }
        )
    return pd.DataFrame(rows)


def bridge_score(omega: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        grid_indices = vector["GridIndex"].astype(int).to_list()
        whitening = load_whitening(route, grid_indices)
        z = vector["z_grid"].to_numpy(float)
        target = vector["WhitenedTarget"].to_numpy(float)
        k2 = vector["K2LockedWhitened"].to_numpy(float)
        for (family_id, sample_id), group in omega.groupby(["FamilyID", "SampleID"]):
            group = group.sort_values("z")
            interpolated = np.interp(z, group["z"].to_numpy(float), group["Omega_R_plus_3Omega_Q"].to_numpy(float))
            pred = whitening @ interpolated
            rows.append(
                {
                    "AuditID": "SOURCE_NATIVE_BACKREACTION_FIXTURE_SMOKE_TEST_V1",
                    "RouteID": route["RouteID"],
                    "FamilyID": family_id,
                    "SampleID": sample_id,
                    "Rows": len(target),
                    "Chi2AgainstTarget": chi2(target, pred),
                    "K2Chi2AgainstTarget": chi2(target, k2),
                    "CorrelationWithTarget": corr(target, pred),
                    "CorrelationWithK2": corr(k2, pred),
                    "LockedK2Changed": False,
                    "ScaleFitAllowed": False,
                    "FixtureDataOnly": True,
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "source_native_fixture_smoke_test_no_measurement_validation",
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    route_vector = pd.read_csv(ROUTES[0]["Vector"])
    z_grid = route_vector["z_grid"].to_numpy(float)
    recon = make_fixture_reconstruction(z_grid)
    meta = make_fixture_metadata()
    recon_issues = validate_reconstruction_vector(recon)
    meta_issues = validate_selection_metadata(meta)
    omega = build_backreaction_vector(recon) if not recon_issues else pd.DataFrame()
    score = bridge_score(omega) if not omega.empty else pd.DataFrame()

    recon.to_csv(OUT_RECON, index=False)
    meta.to_csv(OUT_META, index=False)
    omega.to_csv(OUT_OMEGA, index=False)
    score.to_csv(OUT_SCORE, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_FIXTURE_SMOKE_TEST_V1",
                "FixtureReconstructionRows": len(recon),
                "FixtureMetadataRows": len(meta),
                "ReconstructionValidationIssues": ";".join(recon_issues),
                "MetadataValidationIssues": ";".join(meta_issues),
                "OmegaRowsWritten": len(omega),
                "BridgeScoreRowsWritten": len(score),
                "FixturePipelinePasses": not recon_issues and not meta_issues and not omega.empty and not score.empty,
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "FixtureDataOnly": True,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_PIPELINE_FIXTURE_SMOKE_PASSED"
                if not recon_issues and not meta_issues and not omega.empty and not score.empty
                else "SOURCE_NATIVE_PIPELINE_FIXTURE_SMOKE_FAILED",
                "StrongestAllowedClaim": "source-native ingestion and bridge scoring code path works on artificial fixture data",
                "PrimaryResidualRisk": "fixture data are not observational data and do not reduce the need for author exports or reproduced symbolic-regression outputs",
                "NextAction": "replace fixture with real source_native_reconstruction_vector.csv and selection metadata",
                "ClaimBoundary": "source_native_fixture_smoke_test_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Backreaction Fixture Smoke Test",
                "",
                "Status: artificial fixture only; no measurement validation.",
                "",
                "This smoke test proves the ingestion -> fixed formula -> bridge scorecard path can execute when a validly shaped source-native export exists. The fixture is not observational data.",
                "",
                "## Outputs",
                "",
                f"- Fixture reconstruction: `{OUT_RECON.relative_to(ROOT)}`",
                f"- Fixture metadata: `{OUT_META.relative_to(ROOT)}`",
                f"- Fixture omega vector: `{OUT_OMEGA.relative_to(ROOT)}`",
                f"- Fixture scorecard: `{OUT_SCORE.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_RECON}")
    print(f"Wrote {OUT_META}")
    print(f"Wrote {OUT_OMEGA}")
    print(f"Wrote {OUT_SCORE}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
