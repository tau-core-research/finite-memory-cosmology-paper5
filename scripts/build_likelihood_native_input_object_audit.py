#!/usr/bin/env python3
"""Audit public input objects needed for likelihood-native A2 scoring.

The audit inspects the local Pantheon+ and DESI DR2 files and records which
objects are present versus which residual-definition decisions still block a
measurement-grade transform.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SN_TABLE = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
SN_COV = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_MEAN = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
BAO_COV = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

OUT_AUDIT = EVIDENCE / "likelihood_native_input_object_audit.csv"
OUT_SUMMARY = EVIDENCE / "likelihood_native_input_object_summary.csv"
OUT_DOC = DOCS / "likelihood_native_input_object_audit.md"


def load_flat_covariance_size(path: Path) -> tuple[int, int]:
    values = np.loadtxt(path, max_rows=1)
    declared = int(values)
    total_values = sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore")) - 1
    return declared, total_values


def main() -> None:
    sn = pd.read_csv(SN_TABLE, sep=r"\s+", engine="python")
    sn_cov_declared, sn_cov_values = load_flat_covariance_size(SN_COV)
    bao = pd.read_csv(BAO_MEAN, comment="#", sep=r"\s+", engine="python", header=None, names=["z", "value", "quantity"])
    bao_cov = np.loadtxt(BAO_COV)

    sn_required = ["zHD", "zCMB", "MU_SH0ES", "MU_SH0ES_ERR_DIAG", "IS_CALIBRATOR", "USED_IN_SH0ES_HF"]
    sn_missing = [col for col in sn_required if col not in sn.columns]
    bao_quantities = sorted(bao["quantity"].astype(str).unique())

    rows = [
        {
            "ObjectID": "SN_TABLE_PANTHEON_PLUS",
            "ObjectClass": "sn_public_vector",
            "Artifact": str(SN_TABLE.relative_to(ROOT)),
            "Rows": len(sn),
            "ColumnsOrShape": f"{len(sn.columns)} columns",
            "RequiredFieldsPresent": len(sn_missing) == 0,
            "ObservedFields": ";".join([col for col in sn_required if col in sn.columns]),
            "MissingFields": ";".join(sn_missing),
            "PreflightUsable": True,
            "MeasurementUsable": False,
            "BlockingIssue": "SN residual definition requires frozen cosmology/nuisance centering and calibrator policy",
            "NextAction": "define r_SN and nuisance/marginalization policy before constructing L_SN",
        },
        {
            "ObjectID": "SN_COVARIANCE_PANTHEON_PLUS",
            "ObjectClass": "sn_public_covariance",
            "Artifact": str(SN_COV.relative_to(ROOT)),
            "Rows": sn_cov_declared,
            "ColumnsOrShape": f"{sn_cov_declared}x{sn_cov_declared}",
            "RequiredFieldsPresent": sn_cov_values == sn_cov_declared * sn_cov_declared,
            "ObservedFields": f"flat_values={sn_cov_values}",
            "MissingFields": "" if sn_cov_values == sn_cov_declared * sn_cov_declared else "flat_covariance_length_mismatch",
            "PreflightUsable": sn_cov_values == sn_cov_declared * sn_cov_declared,
            "MeasurementUsable": False,
            "BlockingIssue": "covariance is available but must be propagated through likelihood-native L_SN",
            "NextAction": "use only after SN residual transform is frozen",
        },
        {
            "ObjectID": "BAO_VECTOR_DESI_DR2",
            "ObjectClass": "bao_public_vector",
            "Artifact": str(BAO_MEAN.relative_to(ROOT)),
            "Rows": len(bao),
            "ColumnsOrShape": "z,value,quantity",
            "RequiredFieldsPresent": set(bao_quantities).issubset({"DH_over_rs", "DM_over_rs", "DV_over_rs"}),
            "ObservedFields": ";".join(bao_quantities),
            "MissingFields": "",
            "PreflightUsable": True,
            "MeasurementUsable": False,
            "BlockingIssue": "BAO residual definition requires frozen prediction vector and no nearest-anchor transform",
            "NextAction": "define r_BAO for each observable type before constructing L_BAO",
        },
        {
            "ObjectID": "BAO_COVARIANCE_DESI_DR2",
            "ObjectClass": "bao_public_covariance",
            "Artifact": str(BAO_COV.relative_to(ROOT)),
            "Rows": bao_cov.shape[0],
            "ColumnsOrShape": f"{bao_cov.shape[0]}x{bao_cov.shape[1]}",
            "RequiredFieldsPresent": bao_cov.shape == (len(bao), len(bao)),
            "ObservedFields": f"shape={bao_cov.shape}",
            "MissingFields": "" if bao_cov.shape == (len(bao), len(bao)) else "covariance_shape_mismatch",
            "PreflightUsable": bao_cov.shape == (len(bao), len(bao)),
            "MeasurementUsable": False,
            "BlockingIssue": "covariance is available but must be propagated through likelihood-native L_BAO",
            "NextAction": "use only after BAO residual transform is frozen",
        },
    ]

    audit = pd.DataFrame(rows)
    audit["ClaimBoundary"] = "likelihood_native_input_object_no_measurement_validation"
    audit.to_csv(OUT_AUDIT, index=False)

    preflight_ready = int(audit["PreflightUsable"].astype(bool).sum())
    measurement_ready = int(audit["MeasurementUsable"].astype(bool).sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "LIKELIHOOD_NATIVE_INPUT_OBJECT_AUDIT_V1",
                "Objects": len(audit),
                "PreflightUsableObjects": preflight_ready,
                "MeasurementUsableObjects": measurement_ready,
                "SNRows": len(sn),
                "SNCovarianceDimension": sn_cov_declared,
                "BAORows": len(bao),
                "BAOCovarianceDimension": bao_cov.shape[0],
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "PUBLIC_INPUT_OBJECTS_PRESENT_RESIDUAL_DEFINITIONS_BLOCKED",
                "StrongestAllowedClaim": "public SN and BAO input objects are locally present and dimensionally consistent for preflight planning",
                "PrimaryBlocker": "likelihood-native SN and BAO residual definitions are not frozen",
                "NextAction": "define r_SN and r_BAO contracts before building measurement-grade L_SN/L_BAO",
                "ClaimBoundary": "likelihood_native_input_object_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Likelihood-Native Input Object Audit",
        "",
        "Status: public inputs are present; residual definitions are not measurement-frozen.",
        "",
        "## Summary",
        "",
        f"- SN rows: {len(sn)}",
        f"- SN covariance dimension: {sn_cov_declared}",
        f"- BAO rows: {len(bao)}",
        f"- BAO covariance dimension: {bao_cov.shape[0]}",
        f"- Preflight usable objects: {preflight_ready}/{len(audit)}",
        f"- Measurement usable objects: {measurement_ready}/{len(audit)}",
        "",
        "## Objects",
        "",
    ]
    for _, row in audit.iterrows():
        lines.extend(
            [
                f"### {row['ObjectID']}",
                "",
                f"- Class: {row['ObjectClass']}",
                f"- Artifact: `{row['Artifact']}`",
                f"- Rows: {row['Rows']}",
                f"- Shape/columns: {row['ColumnsOrShape']}",
                f"- Preflight usable: {row['PreflightUsable']}",
                f"- Measurement usable: {row['MeasurementUsable']}",
                f"- Blocking issue: {row['BlockingIssue']}",
                f"- Next action: {row['NextAction']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "This audit only verifies local input availability and dimensional consistency. It does not construct a measurement-grade likelihood.",
            "",
        ]
    )
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
