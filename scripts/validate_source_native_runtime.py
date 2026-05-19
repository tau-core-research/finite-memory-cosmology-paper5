#!/usr/bin/env python3
"""Validate runtime capabilities for source-native reproduction preflight."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_MODULES = EVIDENCE / "source_native_runtime_validation.csv"
OUT_SUMMARY = EVIDENCE / "source_native_runtime_validation_summary.csv"
OUT_DOC = DOCS / "source_native_runtime_validation.md"

MODULES = [
    ("numpy", "minimum_numeric_formula_stack", True),
    ("pandas", "minimum_numeric_formula_stack", True),
    ("scipy", "derivative_interpolation_and_optimization_stack", False),
    ("sympy", "symbolic_expression_handling_stack", False),
    ("sklearn", "model_selection_and_cv_stack", False),
    ("pysr", "source_native_symbolic_regression_stack", False),
]


def available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    rows = []
    for module, role, minimum in MODULES:
        rows.append(
            {
                "Module": module,
                "Role": role,
                "RequiredForCurrentPreflightFormulaAudit": minimum,
                "Available": available(module),
                "BlocksCurrentPreflightFormulaAudit": minimum and not available(module),
                "BlocksSourceNativeSymbolicReproduction": module in {"pysr"} and not available(module),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "source_native_runtime_validation_no_measurement_validation",
            }
        )
    modules = pd.DataFrame(rows)
    modules.to_csv(OUT_MODULES, index=False)

    minimum_ok = bool(
        modules[modules["RequiredForCurrentPreflightFormulaAudit"].map(bool)]["Available"].map(bool).all()
    )
    symbolic_ok = bool(modules.loc[modules["Module"].eq("pysr"), "Available"].iloc[0])
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_RUNTIME_VALIDATION_V1",
                "MinimumFormulaAuditRuntimeReady": minimum_ok,
                "DerivativeConvenienceStackReady": bool(modules.loc[modules["Module"].eq("scipy"), "Available"].iloc[0]),
                "SymbolicRegressionRuntimeReady": symbolic_ok,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "MINIMUM_RUNTIME_READY_SYMBOLIC_RUNTIME_MISSING"
                    if minimum_ok and not symbolic_ok
                    else "RUNTIME_BLOCKED"
                ),
                "StrongestAllowedClaim": (
                    "the current runtime can execute formula/input audits, but not a PySR/cp3-bench source-native symbolic-regression reproduction"
                ),
                "PrimaryResidualRisk": "without PySR/cp3-bench or author exports, source-native family reconstruction remains blocked",
                "NextAction": "use author export route or create a separate symbolic-regression runtime environment",
                "ClaimBoundary": "source_native_runtime_validation_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Runtime Validation",
                "",
                "Status: minimum formula-audit runtime ready; symbolic-regression runtime missing.",
                "",
                "This validates local Python module availability. It does not install packages and does not authorize measurement validation.",
                "",
                "## Outputs",
                "",
                f"- Module audit: `{OUT_MODULES.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_MODULES}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
