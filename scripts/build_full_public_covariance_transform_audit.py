#!/usr/bin/env python3
"""Audit the full-public-covariance transform route for locked A2.

This checks what is already available from public Pantheon+/DESI inputs and
what still blocks a measurement-grade covariance route. It is a readiness audit,
not a scorecard rescue and not measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PANTHEON_TABLE = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
PANTHEON_COV = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
DESI_MEAN = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_COV = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
L_SN = DATA / "transforms" / "k2_a2_l_sn_transform_v1.csv"
L_BAO = DATA / "transforms" / "k2_a2_l_bao_transform_v1.csv"
PUBLIC_PROXY = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy_summary.csv"
CROSS_SENS = EVIDENCE / "source_split_likelihood_native_cross_covariance_summary.csv"
SUPPORT = EVIDENCE / "source_split_likelihood_native_support_ladder_summary.csv"

OUT = EVIDENCE / "full_public_covariance_transform_audit.csv"
SUMMARY = EVIDENCE / "full_public_covariance_transform_summary.csv"
DOC = DOCS / "full_public_covariance_transform_audit.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_flat_covariance_with_size(path: Path) -> np.ndarray:
    values = np.loadtxt(path)
    declared = int(values[0])
    flat = values[1:]
    if len(flat) != declared * declared:
        raise ValueError(f"flat covariance length mismatch: declared={declared}, values={len(flat)}")
    return flat.reshape((declared, declared))


def load_transform(path: Path, prefix: str) -> tuple[list[int], np.ndarray]:
    df = pd.read_csv(path)
    cols = [col for col in df.columns if col.startswith(prefix)]
    return df["GridIndex"].astype(int).to_list(), df[cols].to_numpy(float)


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def pd_status(matrix: np.ndarray) -> tuple[bool, float, float]:
    eig = np.linalg.eigvalsh(np.asarray(matrix, dtype=float))
    return bool(float(np.min(eig)) > 0.0), float(np.min(eig)), float(np.max(eig))


def main() -> None:
    pantheon_table = pd.read_csv(PANTHEON_TABLE, sep=r"\s+", engine="python")
    pantheon_cov = load_flat_covariance_with_size(PANTHEON_COV)
    desi_mean = pd.read_csv(DESI_MEAN, comment="#", sep=r"\s+", engine="python", header=None)
    desi_cov = np.loadtxt(DESI_COV)
    sn_grid, l_sn = load_transform(L_SN, "SN_")
    bao_grid, l_bao = load_transform(L_BAO, "BAO_")
    public = first(PUBLIC_PROXY)
    support = first(SUPPORT)
    cross = pd.read_csv(CROSS_SENS)

    sn_cov_transformed = l_sn @ pantheon_cov @ l_sn.T
    bao_cov_transformed = l_bao @ desi_cov @ l_bao.T
    block_zero_cross = sn_cov_transformed + bao_cov_transformed
    block_ok, block_min, block_max = pd_status(block_zero_cross + np.eye(len(block_zero_cross)) * 1e-12)

    cross_valid = cross.copy()
    cross_valid["K2BeatsBestPoly"] = cross_valid["K2BeatsBestPoly"].map(truthy)
    cross_valid["K2ImprovesOverK1"] = cross_valid["K2ImprovesOverK1"].map(truthy)
    cross_poly_count = int(cross_valid["K2BeatsBestPoly"].sum())
    cross_k1_count = int(cross_valid["K2ImprovesOverK1"].sum())

    checks = [
        {
            "CheckID": "FPCOV_1_PUBLIC_SN_VECTOR_AND_COVARIANCE",
            "Status": "PASS" if PANTHEON_TABLE.exists() and PANTHEON_COV.exists() else "BLOCKED",
            "Evidence": f"Pantheon rows={len(pantheon_table)}; covariance shape={pantheon_cov.shape}",
            "BlocksMeasurementValidation": True,
            "Interpretation": "public SN covariance input is locally available",
        },
        {
            "CheckID": "FPCOV_2_PUBLIC_BAO_VECTOR_AND_COVARIANCE",
            "Status": "PASS" if DESI_MEAN.exists() and DESI_COV.exists() else "BLOCKED",
            "Evidence": f"DESI mean rows={len(desi_mean)}; covariance shape={desi_cov.shape}",
            "BlocksMeasurementValidation": True,
            "Interpretation": "public BAO covariance input is locally available",
        },
        {
            "CheckID": "FPCOV_3_TRANSFORM_MATRICES_AVAILABLE",
            "Status": "PASS" if L_SN.exists() and L_BAO.exists() and sn_grid == bao_grid else "BLOCKED",
            "Evidence": f"L_SN shape={l_sn.shape}; L_BAO shape={l_bao.shape}; aligned_grid={sn_grid == bao_grid}",
            "BlocksMeasurementValidation": True,
            "Interpretation": "SN and BAO transform matrices are exported and row-aligned",
        },
        {
            "CheckID": "FPCOV_4_ZERO_CROSS_COVARIANCE_POSITIVE_DEFINITE",
            "Status": "PASS" if block_ok else "BLOCKED",
            "Evidence": f"zero-cross propagated covariance eig_min={block_min}; eig_max={block_max}",
            "BlocksMeasurementValidation": False,
            "Interpretation": "the propagated zero-cross covariance is numerically usable as preflight covariance",
        },
        {
            "CheckID": "FPCOV_5_PUBLIC_PROXY_SCORECARD_STATUS",
            "Status": "WARNING" if not truthy(public["K2BeatsBestPoly"]) else "PASS",
            "Evidence": (
                f"K2 improves over K1={public['K2ImprovesOverK1']}; "
                f"K2 beats best polynomial={public['K2BeatsBestPoly']}; "
                f"best model={public['BestModel']}"
            ),
            "BlocksMeasurementValidation": True,
            "Interpretation": "public covariance route remains mixed because polynomial controls dominate in proxy scorecard",
        },
        {
            "CheckID": "FPCOV_6_CROSS_COVARIANCE_ROUTE",
            "Status": "WARNING",
            "Evidence": (
                f"cross-cov sensitivity K2 improves over K1={cross_k1_count}/{len(cross_valid)}; "
                f"K2 beats polynomial={cross_poly_count}/{len(cross_valid)}"
            ),
            "BlocksMeasurementValidation": True,
            "Interpretation": "SN-BAO cross-covariance is not likelihood-native and cannot be tuned into a validation route",
        },
        {
            "CheckID": "FPCOV_7_FULL_LIKELIHOOD_NATIVE_TRANSFORM",
            "Status": "BLOCKED",
            "Evidence": "current transform is binned/anchored diagnostic transform, not full SN+BAO likelihood-native joint transform",
            "BlocksMeasurementValidation": True,
            "Interpretation": "full measurement route is still missing",
        },
        {
            "CheckID": "FPCOV_8_CLAIM_BOUNDARY",
            "Status": "PASS",
            "Evidence": f"support ladder measurement status={support['MeasurementValidationStatus']}",
            "BlocksMeasurementValidation": False,
            "Interpretation": "claim remains bounded to preflight support",
        },
    ]
    detail = pd.DataFrame(checks)
    detail["ClaimBoundary"] = "full_public_covariance_transform_no_measurement_validation"
    detail.to_csv(OUT, index=False)

    passed = int(detail["Status"].eq("PASS").sum())
    warnings = int(detail["Status"].eq("WARNING").sum())
    blocked = int(detail["Status"].eq("BLOCKED").sum())
    measurement_blockers = int((detail["BlocksMeasurementValidation"].map(truthy) & ~detail["Status"].eq("PASS")).sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "FULL_PUBLIC_COVARIANCE_TRANSFORM_AUDIT_V1",
                "Checks": len(detail),
                "PassedChecks": passed,
                "WarningChecks": warnings,
                "BlockedChecks": blocked,
                "MeasurementBlockingChecks": measurement_blockers,
                "RawPublicSNCovarianceAvailable": True,
                "RawPublicBAOCovarianceAvailable": True,
                "TransformMatricesAvailable": True,
                "ZeroCrossCovariancePreflightUsable": block_ok,
                "K2ImprovesOverK1UnderPublicProxy": truthy(public["K2ImprovesOverK1"]),
                "K2BeatsBestPolyUnderPublicProxy": truthy(public["K2BeatsBestPoly"]),
                "FullPublicCovarianceTransformReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "PUBLIC_COVARIANCE_INPUTS_AVAILABLE_FULL_TRANSFORM_BLOCKED",
                "StrongestAllowedClaim": "public covariance inputs are available and propagatable, but full likelihood-native covariance route remains blocked",
                "PrimaryResidualRisk": "polynomial controls dominate the current public proxy and SN-BAO cross-covariance is not likelihood-native",
                "NextAction": "replace binned/anchored diagnostic transform with full likelihood-native joint SN+BAO transform or keep result at calibrated preflight level",
                "ClaimBoundary": "full_public_covariance_transform_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Full Public Covariance Transform Audit",
        "",
        "Status: public covariance inputs are available, but measurement validation remains blocked.",
        "",
        "## Summary",
        "",
        f"- Passed checks: {passed}/{len(detail)}",
        f"- Warnings: {warnings}",
        f"- Blocked: {blocked}",
        f"- Measurement blockers: {measurement_blockers}",
        f"- Zero-cross preflight covariance usable: {block_ok}",
        f"- Full public covariance transform ready: False",
        "",
        "## Findings",
        "",
    ]
    for _, row in detail.iterrows():
        lines.extend(
            [
                f"### {row['CheckID']}",
                "",
                f"- Status: {row['Status']}",
                f"- Evidence: {row['Evidence']}",
                f"- Interpretation: {row['Interpretation']}",
                "",
            ]
        )
    DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
