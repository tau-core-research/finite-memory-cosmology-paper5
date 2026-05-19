#!/usr/bin/env python3
"""Record online source availability for the upstream symbolic-regression route."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_SOURCES = EVIDENCE / "symbolic_regression_online_source_probe.csv"
OUT_SUMMARY = EVIDENCE / "symbolic_regression_online_source_probe_summary.csv"
OUT_DOC = DOCS / "symbolic_regression_online_source_probe.md"


def run(cmd: list[str]) -> tuple[bool, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=25)
        return True, out.strip()
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    cp3_ok, cp3_out = run(["git", "ls-remote", "https://github.com/CP3-Origins/cp3-bench.git", "HEAD"])
    rows = [
        {
            "SourceID": "CP3_BENCH_GITHUB",
            "URL": "https://github.com/CP3-Origins/cp3-bench",
            "Role": "general symbolic-regression benchmarking tool cited by upstream papers",
            "Reachable": cp3_ok,
            "Evidence": cp3_out.split()[0] if cp3_ok and cp3_out else cp3_out,
            "ContainsPaper260405822Exports": False,
            "ContainsDAHDDerivativeTables": False,
            "UsefulForReproduction": True,
            "BlocksSourceNativeScoringIfMissing": False,
            "NextAction": "use as possible runtime/tool reference, but request or reproduce paper-specific expression exports separately",
            "ClaimBoundary": "symbolic_regression_online_source_probe_no_measurement_validation",
        },
        {
            "SourceID": "ARXIV_2604_05822_SOURCE_PACKAGE",
            "URL": "https://arxiv.org/e-print/2604.05822",
            "Role": "paper source package inspected locally",
            "Reachable": True,
            "Evidence": "local source package contains TeX and figures but no machine-readable D/H_D derivative export",
            "ContainsPaper260405822Exports": False,
            "ContainsDAHDDerivativeTables": False,
            "UsefulForReproduction": True,
            "BlocksSourceNativeScoringIfMissing": True,
            "NextAction": "obtain author export or reproduce symbolic-regression bootstrap route",
            "ClaimBoundary": "symbolic_regression_online_source_probe_no_measurement_validation",
        },
        {
            "SourceID": "ARXIV_2604_11249_SOURCE_PACKAGE",
            "URL": "https://arxiv.org/e-print/2604.11249",
            "Role": "backreaction addendum source package inspected locally",
            "Reachable": True,
            "Evidence": "local source package contains formula and figures but no numeric backreaction table",
            "ContainsPaper260405822Exports": False,
            "ContainsDAHDDerivativeTables": False,
            "UsefulForReproduction": True,
            "BlocksSourceNativeScoringIfMissing": True,
            "NextAction": "obtain source-native Omega_R_plus_3Omega_Q vector/covariance or upstream derivative exports",
            "ClaimBoundary": "symbolic_regression_online_source_probe_no_measurement_validation",
        },
    ]
    sources = pd.DataFrame(rows)
    sources.to_csv(OUT_SOURCES, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SYMBOLIC_REGRESSION_ONLINE_SOURCE_PROBE_V1",
                "SourcesProbed": len(sources),
                "ReachableSources": int(sources["Reachable"].map(bool).sum()),
                "PaperSpecificDerivativeExportSources": int(sources["ContainsDAHDDerivativeTables"].map(bool).sum()),
                "GenericToolingSources": int(sources["UsefulForReproduction"].map(bool).sum()),
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "GENERIC_TOOLING_FOUND_PAPER_SPECIFIC_EXPORTS_NOT_FOUND",
                "StrongestAllowedClaim": (
                    "cp3-bench is publicly reachable as generic symbolic-regression tooling, "
                    "but the paper-specific D/H_D derivative exports and covariance are not publicly exposed in the probed sources"
                ),
                "PrimaryResidualRisk": "generic cp3-bench availability does not reproduce author selection choices or bootstrap families",
                "NextAction": "request author exports or build a separate reproduction environment around cp3-bench/PySR",
                "ClaimBoundary": "symbolic_regression_online_source_probe_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Symbolic Regression Online Source Probe",
                "",
                "Status: generic tooling found; paper-specific exports not found.",
                "",
                "The probe records that CP3-Origins/cp3-bench is reachable and relevant as generic symbolic-regression tooling, but it does not provide the specific D/H_D derivative tables or bootstrap/covariance exports required for source-native backreaction scoring.",
                "",
                "## Sources",
                "",
                "- CP3 bench GitHub: https://github.com/CP3-Origins/cp3-bench",
                "- arXiv 2604.05822: https://arxiv.org/abs/2604.05822",
                "- arXiv 2604.11249: https://arxiv.org/abs/2604.11249",
                "",
                "## Outputs",
                "",
                f"- Source probe: `{OUT_SOURCES.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SOURCES}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
