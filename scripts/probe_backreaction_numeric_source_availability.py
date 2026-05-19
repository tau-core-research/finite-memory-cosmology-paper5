#!/usr/bin/env python3
"""Audit whether the public backreaction sources expose numeric inputs.

The goal is narrow: determine whether the arXiv source packages contain
machine-readable numeric reconstruction/constraint data that can calibrate a
BACKREACTION_ONLY physical null without digitizing figures or fitting to K2.
"""

from __future__ import annotations

import re
import tarfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "physical_nulls" / "raw"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SOURCES = [
    {
        "SourceID": "KOKSBANG_BACKREACTION_ADDENDUM_2604_11249",
        "ArxivID": "2604.11249",
        "Role": "backreaction_formula_and_figures",
        "Package": RAW / "arxiv_2604_11249" / "source_package.bin",
    },
    {
        "SourceID": "KOKSBANG_HEINESEN_SYMBOLIC_RECON_2604_05822",
        "ArxivID": "2604.05822",
        "Role": "upstream_symbolic_regression_reconstruction",
        "Package": RAW / "arxiv_2604_05822" / "source_package.bin",
    },
]

NUMERIC_EXTENSIONS = {".csv", ".tsv", ".txt", ".dat", ".json", ".npy", ".npz", ".h5", ".hdf5", ".fits"}
PLOT_EXTENSIONS = {".pdf", ".eps", ".png", ".jpg", ".jpeg"}

BACKREACTION_FORMULA_PATTERNS = [
    r"Omega_R\s*\+\s*3\\Omega_Q",
    r"\\Omega_R\s*\+\s*3\\Omega_Q",
    r"H_D",
    r"D\\prime",
]

DEPENDENCY_PATTERNS = {
    "cp3_bench": r"cp3-bench|github\.com/CP3-Origins/cp3-bench",
    "pantheon": r"Pantheon\+|pantheon",
    "bao": r"BOSS|eBOSS|DESI|BAO",
    "symbolic_regression": r"symbolic regression|bootstrap",
}

OUT_AVAILABILITY = EVIDENCE / "backreaction_numeric_source_availability.csv"
OUT_SUMMARY = EVIDENCE / "backreaction_numeric_source_availability_summary.csv"
OUT_DOC = DOCS / "backreaction_numeric_source_availability.md"


def read_member_text(tf: tarfile.TarFile, name: str) -> str:
    member = tf.extractfile(name)
    if member is None:
        return ""
    return member.read().decode("utf-8", errors="replace")


def inspect_source(source: dict[str, object]) -> dict[str, object]:
    package = Path(source["Package"])
    if not package.exists():
        return {
            **source,
            "PackageExists": False,
            "MemberCount": 0,
            "NumericLikeMembers": "",
            "PlotMembers": "",
            "TexMembers": "",
            "HasMachineReadableNumericTable": False,
            "HasBackreactionFormula": False,
            "HasPublishedFigureOnlyRoute": False,
            "HasCp3BenchReference": False,
            "HasPantheonReference": False,
            "HasBAOReference": False,
            "HasSymbolicRegressionReference": False,
            "AllowedForBackreactionCalibrationNow": False,
            "BlockingIssue": "source_package_missing",
            "RequiredNextCheck": "acquire_source_package",
            "ClaimBoundary": "source_availability_audit_no_measurement_validation",
        }

    if not tarfile.is_tarfile(package):
        return {
            **source,
            "PackageExists": True,
            "MemberCount": 0,
            "NumericLikeMembers": "",
            "PlotMembers": "",
            "TexMembers": "",
            "HasMachineReadableNumericTable": False,
            "HasBackreactionFormula": False,
            "HasPublishedFigureOnlyRoute": False,
            "HasCp3BenchReference": False,
            "HasPantheonReference": False,
            "HasBAOReference": False,
            "HasSymbolicRegressionReference": False,
            "AllowedForBackreactionCalibrationNow": False,
            "BlockingIssue": "source_package_not_tar",
            "RequiredNextCheck": "manual_source_package_inspection",
            "ClaimBoundary": "source_availability_audit_no_measurement_validation",
        }

    with tarfile.open(package) as tf:
        names = tf.getnames()
        numeric = [n for n in names if Path(n).suffix.lower() in NUMERIC_EXTENSIONS and not n.endswith("00README.json")]
        plots = [n for n in names if Path(n).suffix.lower() in PLOT_EXTENSIONS]
        tex = [n for n in names if Path(n).suffix.lower() in {".tex", ".bib"}]
        all_text = "\n".join(read_member_text(tf, n) for n in tex)

    has_formula = any(re.search(p, all_text, flags=re.IGNORECASE) for p in BACKREACTION_FORMULA_PATTERNS)
    deps = {key: bool(re.search(pattern, all_text, flags=re.IGNORECASE)) for key, pattern in DEPENDENCY_PATTERNS.items()}
    has_numeric = len(numeric) > 0
    has_figures = len(plots) > 0

    if has_numeric:
        blocking = "numeric_like_members_present_manual_semantic_validation_required"
        next_check = "validate_numeric_members_against_backreaction_formula_and_covariance"
    elif has_formula or has_figures:
        blocking = "formula_or_figures_available_but_no_machine_readable_numeric_constraint_table"
        next_check = "obtain_author_reconstruction_table_or_reproduce_symbolic_regression_pipeline"
    else:
        blocking = "no_numeric_or_formula_route_detected"
        next_check = "manual_literature_followup"

    return {
        **source,
        "PackageExists": True,
        "MemberCount": len(names),
        "NumericLikeMembers": ";".join(numeric),
        "PlotMembers": ";".join(plots),
        "TexMembers": ";".join(tex),
        "HasMachineReadableNumericTable": has_numeric,
        "HasBackreactionFormula": has_formula,
        "HasPublishedFigureOnlyRoute": has_figures and not has_numeric,
        "HasCp3BenchReference": deps["cp3_bench"],
        "HasPantheonReference": deps["pantheon"],
        "HasBAOReference": deps["bao"],
        "HasSymbolicRegressionReference": deps["symbolic_regression"],
        "AllowedForBackreactionCalibrationNow": False,
        "BlockingIssue": blocking,
        "RequiredNextCheck": next_check,
        "ClaimBoundary": "source_availability_audit_no_measurement_validation",
    }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    rows = [inspect_source(src) for src in SOURCES]
    availability = pd.DataFrame(rows)
    availability.to_csv(OUT_AVAILABILITY, index=False)

    machine_numeric_sources = int(availability["HasMachineReadableNumericTable"].sum())
    formula_or_figure_sources = int(
        (
            availability["HasBackreactionFormula"].map(bool)
            | availability["HasPublishedFigureOnlyRoute"].map(bool)
        ).sum()
    )
    upstream_reconstruction_route_detected = bool(
        availability["HasCp3BenchReference"].map(bool).any()
        and availability["HasPantheonReference"].map(bool).any()
        and availability["HasBAOReference"].map(bool).any()
    )
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "BACKREACTION_NUMERIC_SOURCE_AVAILABILITY_V1",
                "SourcesAudited": len(availability),
                "MachineReadableNumericConstraintSources": machine_numeric_sources,
                "FormulaOrFigureRouteSources": formula_or_figure_sources,
                "UpstreamSymbolicRegressionRouteDetected": upstream_reconstruction_route_detected,
                "AllowedForBackreactionCalibrationNow": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "BACKREACTION_NUMERIC_CALIBRATION_BLOCKED_SOURCE_ROUTE_IDENTIFIED"
                    if machine_numeric_sources == 0
                    else "NUMERIC_CANDIDATE_PRESENT_REQUIRES_SEMANTIC_VALIDATION"
                ),
                "StrongestAllowedClaim": (
                    "public sources identify the backreaction formula and upstream symbolic-regression route, "
                    "but do not expose a machine-readable numeric backreaction constraint table in the arXiv source packages"
                ),
                "PrimaryResidualRisk": (
                    "using figure digitization would be a fallback, not source-native calibration; "
                    "measurement validation remains closed"
                ),
                "NextAction": (
                    "request or reproduce the D_A,H_D derivative reconstruction table from the upstream symbolic-regression pipeline"
                ),
                "ClaimBoundary": "backreaction_source_availability_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    lines = [
        "# Backreaction Numeric Source Availability",
        "",
        "Status: source route identified; numeric backreaction calibration remains blocked.",
        "",
        "This audit checks the arXiv source packages for machine-readable numeric tables that could calibrate a BACKREACTION_ONLY physical null. It does not digitize figures and does not fit amplitudes to K2.",
        "",
        "## Result",
        "",
        f"- Sources audited: {len(availability)}",
        f"- Machine-readable numeric constraint sources: {machine_numeric_sources}",
        f"- Formula/figure route sources: {formula_or_figure_sources}",
        f"- Upstream symbolic-regression route detected: {upstream_reconstruction_route_detected}",
        "",
        "## Interpretation",
        "",
        "The Koksbang addendum exposes the backreaction formula and figure route. The upstream Koksbang-Heinesen reconstruction source package exposes the symbolic-regression method and figures, plus a cp3-bench reference, but no source-native numeric reconstruction table in the arXiv source package.",
        "",
        "Therefore the backreaction null is not yet calibrated for the measurement gate. The next legitimate route is to obtain or reproduce the D_A, H_D and derivative reconstruction table with covariance, then map it into the locked A2/K2 preflight vector without changing the K2 kernel.",
        "",
        "## Outputs",
        "",
        f"- Availability: `{OUT_AVAILABILITY.relative_to(ROOT)}`",
        f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_AVAILABILITY}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
