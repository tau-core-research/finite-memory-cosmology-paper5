#!/usr/bin/env python3
"""Build a provisional extraction manifest for physical-null source candidates.

This is an acquisition artifact, not a benchmark-ingestion script. It records
candidate values visible in source packages and keeps every row blocked until a
declared mapping and covariance route exists.
"""

from __future__ import annotations

import io
import re
import tarfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "physical_nulls" / "raw"
EVIDENCE = ROOT / "evidence"

OUT = EVIDENCE / "physical_null_provisional_extraction_manifest.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_provisional_extraction_summary.csv"


def read_tar_text(arxiv_id: str, member_name: str) -> str:
    package = RAW / f"arxiv_{arxiv_id.replace('.', '_')}" / "source_package.bin"
    with tarfile.open(fileobj=io.BytesIO(package.read_bytes()), mode="r:*") as archive:
        extracted = archive.extractfile(member_name)
        if extracted is None:
            return ""
        return extracted.read().decode("utf-8", errors="ignore")


def clean_tex(value: str) -> str:
    value = value.replace("\\", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def row(
    *,
    extraction_id: str,
    candidate_id: str,
    arxiv_id: str,
    null_id: str,
    quantity: str,
    value: str,
    lower_error: str = "",
    upper_error: str = "",
    confidence: str = "",
    redshift_range: str = "",
    source_location: str,
    extraction_route: str,
    potential_use: str,
    status: str = "provisional_extracted_not_mapped",
    blocking_issue: str = "mapping_and_covariance_missing",
) -> dict[str, object]:
    return {
        "ExtractionID": extraction_id,
        "CandidateID": candidate_id,
        "ArxivID": arxiv_id,
        "NullID": null_id,
        "Quantity": quantity,
        "Value": value,
        "LowerError": lower_error,
        "UpperError": upper_error,
        "ConfidenceLevel": confidence,
        "RedshiftRange": redshift_range,
        "SourceLocation": source_location,
        "ExtractionRoute": extraction_route,
        "PotentialUse": potential_use,
        "Status": status,
        "CanUseAsBenchmarkInputNow": False,
        "BlockingIssue": blocking_issue,
        "RequiredNextCheck": "map_to_source_split_vector_and_attach_source_uncertainty_or_covariance",
        "ClaimBoundary": "provisional_source_extraction_no_measurement_validation",
    }


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    # Koksbang 2604.11249: the source has figures and formulas, but no
    # source-native numeric table in the package. Keep it as a figure/formula
    # extraction target rather than inventing values.
    koksbang_text = read_tar_text("2604.11249", "main.tex")
    has_qr_formula = "\\Omega_R + 3\\Omega_Q" in koksbang_text or "Omega_R + 3" in koksbang_text
    rows.append(
        row(
            extraction_id="PX_BACKREACTION_KOKSBANG_FORMULA_ROUTE",
            candidate_id="PNC_BACKREACTION_KOKSBANG_2604_11249",
            arxiv_id="2604.11249",
            null_id="BACKREACTION_ONLY",
            quantity="Omega_R_plus_3Omega_Q_constraint_route",
            value="not_extracted",
            source_location="main.tex Eq. test and QR_*.pdf figures",
            extraction_route="formula_plus_figure_or_external_reconstruction",
            potential_use="backreaction physical-null amplitude/envelope source",
            status="route_identified_values_not_extracted",
            blocking_issue=(
                "no_source_native_numeric_constraint_table_detected;"
                f"qr_formula_detected={str(has_qr_formula).lower()}"
            ),
        )
    )

    # Breton-Montiel 1303.1574: source tables contain alpha constraints.
    rows.extend(
        [
            row(
                extraction_id="PX_ZKDR_1303_TABLE1_SNE_ALPHA_PRIOR",
                candidate_id="PNC_DYER_ROEDER_SNE_GRB_1303_1574",
                arxiv_id="1303.1574",
                null_id="DYER_ROEDER_OPTICAL",
                quantity="alpha_smoothness",
                value="0.856",
                lower_error="0.176",
                upper_error="0.106",
                confidence="68.3_percent",
                redshift_range="0.015<=z<=1.414",
                source_location="SmoothDraft4.tex Table 1 / abstract",
                extraction_route="tex_table",
                potential_use="Dyer-Roeder optical physical-null sensitivity",
            ),
            row(
                extraction_id="PX_ZKDR_1303_TABLE1_GRB_ALPHA_PRIOR",
                candidate_id="PNC_DYER_ROEDER_SNE_GRB_1303_1574",
                arxiv_id="1303.1574",
                null_id="DYER_ROEDER_OPTICAL",
                quantity="alpha_smoothness",
                value="0.587",
                lower_error="0.202",
                upper_error="0.201",
                confidence="68.3_percent",
                redshift_range="1.547<=z<=3.57",
                source_location="SmoothDraft4.tex Table 1 / abstract",
                extraction_route="tex_table",
                potential_use="Dyer-Roeder optical physical-null sensitivity",
            ),
            row(
                extraction_id="PX_ZKDR_1303_TABLE1_JOINT_ALPHA_PRIOR",
                candidate_id="PNC_DYER_ROEDER_SNE_GRB_1303_1574",
                arxiv_id="1303.1574",
                null_id="DYER_ROEDER_OPTICAL",
                quantity="alpha_smoothness",
                value="0.685",
                lower_error="0.171",
                upper_error="0.164",
                confidence="68.3_percent",
                redshift_range="0.015<=z<=3.57",
                source_location="SmoothDraft4.tex Table 1 / abstract",
                extraction_route="tex_table",
                potential_use="Dyer-Roeder optical physical-null sensitivity",
            ),
            row(
                extraction_id="PX_ZKDR_1303_TABLE7_JOINT_ALPHA_WITH_HUBBLE",
                candidate_id="PNC_DYER_ROEDER_SNE_GRB_1303_1574",
                arxiv_id="1303.1574",
                null_id="DYER_ROEDER_OPTICAL",
                quantity="alpha_smoothness",
                value="0.821",
                lower_error="0.129",
                upper_error="0.110",
                confidence="68.3_percent",
                redshift_range="0.015<=z<=3.57",
                source_location="SmoothDraft4.tex Table 7",
                extraction_route="tex_table",
                potential_use="Dyer-Roeder optical physical-null sensitivity with Hubble data",
            ),
        ]
    )

    # Yang-Yu-Zhang 1305.6989: source text reports alpha and distance-duality
    # delta constraints. These are useful optical controls, not direct K2 data.
    rows.extend(
        [
            row(
                extraction_id="PX_DR_DD_1305_ALPHA_1SIGMA",
                candidate_id="PNC_DYER_ROEDER_SMOOTHNESS_DD_1305_6989",
                arxiv_id="1305.6989",
                null_id="DYER_ROEDER_OPTICAL",
                quantity="alpha_smoothness",
                value="0.92",
                lower_error="0.32",
                upper_error="0.08",
                confidence="1_sigma",
                redshift_range="0.015<=z<=1.414",
                source_location="mypaper.tex abstract/results",
                extraction_route="tex_text",
                potential_use="Dyer-Roeder optical physical-null sensitivity",
            ),
            row(
                extraction_id="PX_DR_DD_1305_ALPHA_2SIGMA",
                candidate_id="PNC_DYER_ROEDER_SMOOTHNESS_DD_1305_6989",
                arxiv_id="1305.6989",
                null_id="DYER_ROEDER_OPTICAL",
                quantity="alpha_smoothness",
                value="0.92",
                lower_error="0.65",
                upper_error="0.08",
                confidence="2_sigma",
                redshift_range="0.015<=z<=1.414",
                source_location="mypaper.tex abstract/results",
                extraction_route="tex_text",
                potential_use="Dyer-Roeder optical physical-null sensitivity",
            ),
            row(
                extraction_id="PX_DR_DD_1305_DELTA_2SIGMA",
                candidate_id="PNC_DYER_ROEDER_SMOOTHNESS_DD_1305_6989",
                arxiv_id="1305.6989",
                null_id="DYER_ROEDER_OPTICAL",
                quantity="distance_duality_delta",
                value="0.0",
                lower_error="0.01",
                upper_error="0.01",
                confidence="2_sigma",
                redshift_range="0.015<=z<=1.414",
                source_location="mypaper.tex results",
                extraction_route="tex_text",
                potential_use="distance-duality optical consistency control",
            ),
        ]
    )

    return rows


def main() -> None:
    rows = pd.DataFrame(build_rows())
    rows.to_csv(OUT, index=False)

    usable_now = int(rows["CanUseAsBenchmarkInputNow"].sum())
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_PROVISIONAL_EXTRACTION_SUMMARY",
                "RowsExtracted": len(rows),
                "BackreactionRows": int(rows["NullID"].eq("BACKREACTION_ONLY").sum()),
                "DyerRoederRows": int(rows["NullID"].eq("DYER_ROEDER_OPTICAL").sum()),
                "BenchmarkInputsReadyNow": usable_now,
                "RowsBlockedForBenchmark": int(len(rows) - usable_now),
                "RowsBlockedForMappingOrCovariance": int(
                    rows["BlockingIssue"].astype(str).str.contains("mapping|covariance").sum()
                ),
                "RecommendedNextAction": "select one optical alpha route and one backreaction extraction route for mapping-readiness checks",
                "PrimaryBlockingIssue": "mapping_and_covariance_missing",
                "Interpretation": "candidate values/routes are recorded for acquisition planning only",
                "ClaimBoundary": "provisional_source_extraction_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
