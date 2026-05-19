#!/usr/bin/env python3
"""Extract reproducible protocol clues from the upstream symbolic source.

The arXiv source package does not contain the finished derivative vectors, but
it does contain method constraints, data-table values, and selection rules.
This script turns those clues into a machine-readable protocol extract for the
next source-native reproduction attempt.
"""

from __future__ import annotations

import re
import tarfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "physical_nulls" / "raw" / "arxiv_2604_05822" / "source_package.bin"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_PROTOCOL = EVIDENCE / "source_native_symbolic_protocol_extract.csv"
OUT_BAO = EVIDENCE / "source_native_symbolic_protocol_bao_table_extract.csv"
OUT_SUMMARY = EVIDENCE / "source_native_symbolic_protocol_extract_summary.csv"
OUT_DOC = DOCS / "source_native_symbolic_protocol_extract.md"

CLAIM_BOUNDARY = "source_native_symbolic_protocol_extract_no_measurement_validation"


def clean_tex(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def strip_tex(text: str) -> str:
    text = clean_tex(text)
    replacements = {
        r"\mathcal{H}": "H_D",
        r"$": "",
        r"\,": " ",
        r"\newline": " ",
        r"\indent": " ",
        r"\textbf": "",
        r"\underline": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"[{}]", "", text)
    return clean_tex(text)


def first_match(text: str, pattern: str, flags: int = re.IGNORECASE | re.DOTALL) -> str:
    match = re.search(pattern, text, flags=flags)
    return "" if match is None else match.group(1)


def extract_items(block: str) -> list[str]:
    return [strip_tex(item) for item in re.findall(r"\\item\s+(.*?)(?=\\item|$)", block, flags=re.DOTALL)]


def extract_bao_rows(tex: str) -> pd.DataFrame:
    table = first_match(tex, r"\\begin\{tabular\}\{c c c\}(.*?)\\end\{tabular\}")
    rows = []
    for z, value, sigma, ref in re.findall(
        r"\$([0-9.]+)\$\s*&\s*\$([0-9.]+)\s*\\pm\s*([0-9.]+)\$\s*&\s*\\cite\{([^{}]+)\}",
        table,
    ):
        rows.append(
            {
                "SourceID": "KOKSBANG_HEINESEN_SYMBOLIC_RECON_2604_05822",
                "Observable": "c_over_Hrs",
                "z_eff": float(z),
                "Value": float(value),
                "Sigma": float(sigma),
                "ReferenceKey": ref,
                "Role": "BAO radial H_D training input table from upstream source tex",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    with tarfile.open(RAW) as tf:
        tex = tf.extractfile("main.tex").read().decode("utf-8", errors="replace")

    da_criteria_block = first_match(tex, r"\$d_A\$ criteria:.*?\\begin\{enumerate\}(.+?)\\end\{enumerate\}")
    da_procedure_block = first_match(tex, r"\$d_A\$ Procedure:.*?\\begin\{enumerate\}(.+?)\\end\{enumerate\}")
    criteria1 = first_match(
        tex,
        r"Criteria set 1:\}\}\s*(.*?)\\\\\s*\{\\underline\{\\bf Criteria set 2:",
    )
    criteria2 = first_match(
        tex,
        r"Criteria set 2:\}\}\s*(.*?)\\\\\s*\{\\underline\{\\bf Criteria set 3:",
    )
    criteria3 = first_match(tex, r"Criteria set 3:\}\}\s*(.*?)\\\\\s*In practice")

    protocol_rows = []
    for idx, item in enumerate(extract_items(da_criteria_block), start=1):
        protocol_rows.append(
            {
                "ProtocolID": "UPSTREAM_SYMBOLIC_RECON_PROTOCOL_2604_05822",
                "Section": "d_A_selection_criteria",
                "ItemID": f"DA_CRITERION_{idx}",
                "ExtractedText": item,
                "MachineAction": (
                    "implement_mse_threshold"
                    if idx == 1
                    else "manual_or_algorithmic_shape_rejection"
                ),
                "DirectlyExecutable": idx == 1,
                "RequiresManualJudgment": idx in {2, 3},
                "BlocksExactReproduction": idx in {2, 3},
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    for idx, item in enumerate(extract_items(da_procedure_block), start=1):
        protocol_rows.append(
            {
                "ProtocolID": "UPSTREAM_SYMBOLIC_RECON_PROTOCOL_2604_05822",
                "Section": "d_A_procedure",
                "ItemID": f"DA_PROCEDURE_{idx}",
                "ExtractedText": item,
                "MachineAction": (
                    "cp3_bench_bootstrap_run"
                    if idx == 1
                    else "retain_expressions_or_export_grid"
                ),
                "DirectlyExecutable": idx in {3, 4},
                "RequiresManualJudgment": idx in {1, 2},
                "BlocksExactReproduction": idx in {1, 2},
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    criteria_sets = [
        ("HD_CRITERIA_SET_1", criteria1, "choose_three_simplest_nonconstant_nonlinear_from_pysr_hof"),
        ("HD_CRITERIA_SET_2", criteria2, "choose_up_to_three_lowest_loss_nonpathological_from_pysr_hof"),
        ("HD_CRITERIA_SET_3", criteria3, "choose_single_min_loss_plus_penalty_times_complexity"),
    ]
    for item_id, text, action in criteria_sets:
        protocol_rows.append(
            {
                "ProtocolID": "UPSTREAM_SYMBOLIC_RECON_PROTOCOL_2604_05822",
                "Section": "H_D_DR2_selection_criteria",
                "ItemID": item_id,
                "ExtractedText": strip_tex(text),
                "MachineAction": action,
                "DirectlyExecutable": item_id == "HD_CRITERIA_SET_3",
                "RequiresManualJudgment": item_id in {"HD_CRITERIA_SET_1", "HD_CRITERIA_SET_2"},
                "BlocksExactReproduction": item_id in {"HD_CRITERIA_SET_1", "HD_CRITERIA_SET_2"},
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    protocol = pd.DataFrame(protocol_rows)
    protocol.to_csv(OUT_PROTOCOL, index=False)

    bao = extract_bao_rows(tex)
    bao.to_csv(OUT_BAO, index=False)

    manual_blockers = int(protocol["RequiresManualJudgment"].sum())
    executable_items = int(protocol["DirectlyExecutable"].sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_SYMBOLIC_PROTOCOL_EXTRACT_V1",
                "ProtocolItems": len(protocol),
                "BAOTableRowsExtracted": len(bao),
                "DirectlyExecutableItems": executable_items,
                "ManualJudgmentItems": manual_blockers,
                "ExactReproductionBlockedItems": int(protocol["BlocksExactReproduction"].sum()),
                "Cp3BenchRouteIdentified": True,
                "PySRCriteriaSet3Executable": True,
                "AuthorDerivativeVectorsAvailable": False,
                "SourceNativeExportReady": False,
                "SourceNativeCovarianceReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "UPSTREAM_PROTOCOL_EXTRACTED_SOURCE_NATIVE_VECTOR_STILL_MISSING",
                "StrongestAllowedClaim": (
                    "the upstream symbolic-regression protocol is partially machine-readable, but final derivative vectors are not exposed"
                ),
                "PrimaryResidualRisk": (
                    "manual hall-of-fame rejection criteria and missing author expression exports block exact reproduction"
                ),
                "NextAction": (
                    "implement the executable PySR criteria-set-3 reproduction route and keep manual criteria sets as non-exact follow-up"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Symbolic Protocol Extract",
                "",
                "Status: upstream protocol extracted; final derivative vectors still missing.",
                "",
                "The 2604.05822 source package contains the BAO table and symbolic-regression selection rules, but not the exported `D, D_prime, D_double_prime, H_D, H_D_prime` reconstruction vectors. This extract identifies what is machine-executable and what remains manual.",
                "",
                "## Result",
                "",
                f"- Protocol items: {len(protocol)}",
                f"- BAO rows extracted: {len(bao)}",
                f"- Directly executable items: {executable_items}",
                f"- Manual judgment items: {manual_blockers}",
                "",
                "## Outputs",
                "",
                f"- Protocol extract: `{OUT_PROTOCOL.relative_to(ROOT)}`",
                f"- BAO table extract: `{OUT_BAO.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_PROTOCOL}")
    print(f"Wrote {OUT_BAO}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
