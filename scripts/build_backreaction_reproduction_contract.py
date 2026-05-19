#!/usr/bin/env python3
"""Build the backreaction reproduction contract.

This script turns the source-availability audit into a concrete reproduction
contract. It extracts the upstream BAO table from arXiv:2604.05822 when
available, defines the required reconstruction-vector schema, and reports which
items block a source-native BACKREACTION_ONLY benchmark.
"""

from __future__ import annotations

import re
import tarfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "physical_nulls" / "raw"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SRC_05822 = RAW / "arxiv_2604_05822" / "source_package.bin"
SRC_11249 = RAW / "arxiv_2604_11249" / "source_package.bin"
PANTHEON = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
PANTHEON_COV = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
DESI_DR1_MEAN = ROOT / "data" / "public_ingest" / "desi_dr1" / "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR1_COV = ROOT / "data" / "public_ingest" / "desi_dr1" / "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt"
DESI_DR2_MEAN = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR2_COV = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

OUT_BAO_TABLE = DATA / "upstream_2604_05822_bao_radial_table.csv"
OUT_SCHEMA = DATA / "backreaction_reconstruction_vector_schema.csv"
OUT_CONTRACT = EVIDENCE / "backreaction_reproduction_contract.csv"
OUT_READINESS = EVIDENCE / "backreaction_reproduction_readiness.csv"
OUT_DOC = DOCS / "backreaction_reproduction_contract.md"

REQUIRED_SCHEMA = [
    {
        "Column": "z",
        "Meaning": "redshift grid used for source-native reconstruction",
        "RequiredForFormula": True,
        "CurrentStatus": "missing_source_native_grid",
    },
    {
        "Column": "D",
        "Meaning": "D=(1+z)<D_A> on the reconstruction grid",
        "RequiredForFormula": True,
        "CurrentStatus": "missing_source_native_reconstruction",
    },
    {
        "Column": "D_prime",
        "Meaning": "dD/dz on the reconstruction grid",
        "RequiredForFormula": True,
        "CurrentStatus": "missing_source_native_reconstruction",
    },
    {
        "Column": "D_double_prime",
        "Meaning": "d2D/dz2 on the reconstruction grid",
        "RequiredForFormula": True,
        "CurrentStatus": "missing_source_native_reconstruction",
    },
    {
        "Column": "H_D",
        "Meaning": "domain expansion rate reconstruction",
        "RequiredForFormula": True,
        "CurrentStatus": "missing_source_native_reconstruction",
    },
    {
        "Column": "H_D_prime",
        "Meaning": "dH_D/dz on the reconstruction grid",
        "RequiredForFormula": True,
        "CurrentStatus": "missing_source_native_reconstruction",
    },
    {
        "Column": "covariance_or_samples",
        "Meaning": "source-native covariance matrix or bootstrap samples for propagated uncertainty",
        "RequiredForFormula": False,
        "CurrentStatus": "missing_source_native_uncertainty",
    },
]


def read_tex(package: Path) -> str:
    if not package.exists() or not tarfile.is_tarfile(package):
        return ""
    with tarfile.open(package) as tf:
        member = tf.extractfile("main.tex")
        if member is None:
            return ""
        return member.read().decode("utf-8", errors="replace")


def extract_bao_table(tex: str) -> pd.DataFrame:
    """Extract the radial BAO table printed in arXiv:2604.05822."""
    rows: list[dict[str, object]] = []
    pattern = re.compile(
        r"\$([0-9.]+)\$\s*&\s*\$([0-9.]+)\s*\\pm\s*([0-9.]+)\$\s*&\s*\\cite\{([^}]+)\}",
        flags=re.MULTILINE,
    )
    for match in pattern.finditer(tex):
        z, value, err, ref = match.groups()
        rows.append(
            {
                "SourceID": "UPSTREAM_2604_05822_TABLE_BAO",
                "z_eff": float(z),
                "c_over_H_rs": float(value),
                "sigma": float(err),
                "ReferenceKey": ref,
                "SourceLocation": "arXiv:2604.05822 main.tex BAO table",
                "UseInBackreactionFormulaDirectly": False,
                "Role": "input_to_reconstruct_H_D_not_derivative_vector",
                "ClaimBoundary": "backreaction_reproduction_contract_no_measurement_validation",
            }
        )
    return pd.DataFrame(rows)


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    tex_05822 = read_tex(SRC_05822)
    tex_11249 = read_tex(SRC_11249)
    bao_table = extract_bao_table(tex_05822)
    bao_table.to_csv(OUT_BAO_TABLE, index=False)

    schema = pd.DataFrame(REQUIRED_SCHEMA)
    schema.to_csv(OUT_SCHEMA, index=False)

    contract_rows = [
        {
            "ContractItemID": "BR_FORMULA",
            "ItemType": "formula",
            "Required": True,
            "Available": "\\Omega_R + 3\\Omega_Q" in tex_11249 or "Omega_R + 3" in tex_11249,
            "Source": "arXiv:2604.11249 main.tex Eq. test",
            "CurrentArtifact": "src/fmc/backreaction.py",
            "BlockingIssue": "none" if ("\\Omega_R + 3\\Omega_Q" in tex_11249 or "Omega_R + 3" in tex_11249) else "formula_not_detected",
            "NextAction": "keep formula fixed; do not fit to K2",
        },
        {
            "ContractItemID": "BR_UPSTREAM_BAO_TABLE",
            "ItemType": "input_data",
            "Required": True,
            "Available": len(bao_table) > 0,
            "Source": "arXiv:2604.05822 main.tex BAO table",
            "CurrentArtifact": str(OUT_BAO_TABLE.relative_to(ROOT)),
            "BlockingIssue": "none" if len(bao_table) > 0 else "bao_table_not_extracted",
            "NextAction": "use only as upstream H_D reconstruction input, not as final backreaction vector",
        },
        {
            "ContractItemID": "BR_PUBLIC_PANTHEON_INPUT",
            "ItemType": "input_data",
            "Required": True,
            "Available": exists(PANTHEON) and exists(PANTHEON_COV),
            "Source": "local public_ingest Pantheon+ files",
            "CurrentArtifact": "data/public_ingest/pantheon_plus/",
            "BlockingIssue": "none" if exists(PANTHEON) and exists(PANTHEON_COV) else "pantheon_data_or_covariance_missing",
            "NextAction": "use only for source-native D_A reconstruction route",
        },
        {
            "ContractItemID": "BR_PUBLIC_BAO_INPUTS",
            "ItemType": "input_data",
            "Required": True,
            "Available": exists(DESI_DR1_MEAN) and exists(DESI_DR1_COV) and exists(DESI_DR2_MEAN) and exists(DESI_DR2_COV),
            "Source": "local public_ingest DESI DR1/DR2 files",
            "CurrentArtifact": "data/public_ingest/desi_dr1/;data/public_ingest/desi_dr2/",
            "BlockingIssue": "none"
            if exists(DESI_DR1_MEAN) and exists(DESI_DR1_COV) and exists(DESI_DR2_MEAN) and exists(DESI_DR2_COV)
            else "bao_public_mean_or_covariance_missing",
            "NextAction": "decide DR1-vs-DR2 route before reproducing H_D",
        },
        {
            "ContractItemID": "BR_RECONSTRUCTION_VECTOR",
            "ItemType": "derived_vector",
            "Required": True,
            "Available": False,
            "Source": "not present in arXiv source packages",
            "CurrentArtifact": str(OUT_SCHEMA.relative_to(ROOT)),
            "BlockingIssue": "D_Dprime_Ddoubleprime_HD_HDprime_vector_missing",
            "NextAction": "obtain author table or reproduce symbolic-regression/bootstrap reconstruction",
        },
        {
            "ContractItemID": "BR_RECONSTRUCTION_COVARIANCE",
            "ItemType": "uncertainty",
            "Required": True,
            "Available": False,
            "Source": "not present in arXiv source packages",
            "CurrentArtifact": str(OUT_SCHEMA.relative_to(ROOT)),
            "BlockingIssue": "source_native_covariance_or_bootstrap_samples_missing",
            "NextAction": "obtain bootstrap samples or propagate covariance through reconstruction",
        },
        {
            "ContractItemID": "BR_FIGURE_DIGITIZATION_FALLBACK",
            "ItemType": "fallback",
            "Required": False,
            "Available": "QR_criteria1.pdf" in tex_11249 or exists(SRC_11249),
            "Source": "QR_*.pdf figures",
            "CurrentArtifact": "data/physical_nulls/raw/arxiv_2604_11249/source_package.bin",
            "BlockingIssue": "not_source_native_numeric_calibration",
            "NextAction": "use only as explicitly labeled fallback, not for measurement validation",
        },
    ]
    contract = pd.DataFrame(contract_rows)
    contract["AllowedForMeasurementValidation"] = False
    contract["ClaimBoundary"] = "backreaction_reproduction_contract_no_measurement_validation"
    contract.to_csv(OUT_CONTRACT, index=False)

    required = contract[contract["Required"].map(bool)]
    blockers = required[~required["Available"].map(bool)]
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "BACKREACTION_REPRODUCTION_CONTRACT_V1",
                "RequiredItems": len(required),
                "AvailableRequiredItems": int(required["Available"].map(bool).sum()),
                "BlockingRequiredItems": len(blockers),
                "ExtractedUpstreamBAORows": len(bao_table),
                "FormulaImplemented": bool(contract.loc[contract["ContractItemID"].eq("BR_FORMULA"), "Available"].iloc[0]),
                "SourceNativeBackreactionVectorReady": False,
                "AllowedForBackreactionScoringNow": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "BACKREACTION_REPRODUCTION_BLOCKED_ON_DERIVATIVE_VECTOR_AND_COVARIANCE",
                "StrongestAllowedClaim": (
                    "the formula and upstream input-data route are identified, but the source-native derivative "
                    "reconstruction vector and covariance are still missing"
                ),
                "NextAction": "reproduce or obtain z,D,D_prime,D_double_prime,H_D,H_D_prime plus covariance or bootstrap samples",
                "ClaimBoundary": "backreaction_reproduction_contract_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)

    lines = [
        "# Backreaction Reproduction Contract",
        "",
        "Status: formula and upstream input route identified; scoring blocked until the derivative reconstruction vector and covariance are available.",
        "",
        "## Fixed Formula",
        "",
        "`Omega_R + 3 Omega_Q = ((1+z)^2 / D) * (H_D_prime * D_prime / H_D + D_double_prime)`",
        "",
        "The formula is implemented in `src/fmc/backreaction.py`. The implementation does not fit, smooth, digitize figures, or infer covariance.",
        "",
        "## What Is Available",
        "",
        f"- Upstream BAO table rows extracted from arXiv:2604.05822: {len(bao_table)}",
        f"- Pantheon+ local files available: {exists(PANTHEON) and exists(PANTHEON_COV)}",
        f"- DESI DR1/DR2 local BAO mean/covariance files available: {exists(DESI_DR1_MEAN) and exists(DESI_DR1_COV) and exists(DESI_DR2_MEAN) and exists(DESI_DR2_COV)}",
        "",
        "## What Is Still Missing",
        "",
        "- `z,D,D_prime,D_double_prime,H_D,H_D_prime` on a source-native reconstruction grid.",
        "- Source-native covariance or bootstrap samples for those reconstructed quantities.",
        "- A declared mapping from the reconstructed backreaction vector into the locked A2/K2 preflight score vector.",
        "",
        "## Claim Boundary",
        "",
        "This contract does not authorize a backreaction-null rejection claim or measurement validation. Figure digitization remains fallback-only.",
        "",
        "## Outputs",
        "",
        f"- BAO table: `{OUT_BAO_TABLE.relative_to(ROOT)}`",
        f"- Schema: `{OUT_SCHEMA.relative_to(ROOT)}`",
        f"- Contract: `{OUT_CONTRACT.relative_to(ROOT)}`",
        f"- Readiness: `{OUT_READINESS.relative_to(ROOT)}`",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_BAO_TABLE}")
    print(f"Wrote {OUT_SCHEMA}")
    print(f"Wrote {OUT_CONTRACT}")
    print(f"Wrote {OUT_READINESS}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
