#!/usr/bin/env python3
"""Validate the backreaction formula engine and optional source-native input.

This is a non-scoring gate. It proves the repository can compute
Omega_R + 3 Omega_Q from an externally supplied reconstruction vector, while
refusing measurement-level status when that vector or its covariance is absent.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fmc.backreaction import (
    REQUIRED_RECONSTRUCTION_COLUMNS,
    omega_r_plus_3omega_q,
    propagate_omega_covariance,
    validate_reconstruction_columns,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

INPUT_VECTOR = DATA / "source_native_backreaction_reconstruction_vector.csv"
INPUT_COVARIANCE = DATA / "source_native_backreaction_reconstruction_covariance.csv"
TEMPLATE = DATA / "source_native_backreaction_reconstruction_vector_template.csv"
OUTPUT_VECTOR = DATA / "source_native_backreaction_formula_output.csv"
OUTPUT_COVARIANCE = DATA / "source_native_backreaction_formula_covariance.csv"

OUT_READINESS = EVIDENCE / "backreaction_formula_engine_readiness.csv"
OUT_SMOKE = EVIDENCE / "backreaction_formula_engine_smoke_test.csv"
OUT_DOC = DOCS / "backreaction_formula_engine.md"


def write_template() -> None:
    if TEMPLATE.exists():
        return
    rows = [
        {
            "z": "",
            "D": "",
            "D_prime": "",
            "D_double_prime": "",
            "H_D": "",
            "H_D_prime": "",
            "SourceRowID": "",
            "Source": "author_table_or_reproduced_symbolic_regression",
            "ClaimBoundary": "backreaction_formula_engine_no_measurement_validation",
        }
    ]
    pd.DataFrame(rows).to_csv(TEMPLATE, index=False)


def run_smoke_test() -> tuple[bool, float]:
    z = np.array([0.5, 1.0, 1.5], dtype=float)
    D = 1.0 + z
    Dp = np.ones_like(z)
    Dpp = np.zeros_like(z)
    H = 1.0 + 0.2 * z
    Hp = np.full_like(z, 0.2)
    expected = ((1.0 + z) ** 2 / D) * (Hp * Dp / H + Dpp)
    actual = omega_r_plus_3omega_q(z, D, Dp, Dpp, H, Hp)
    max_abs_err = float(np.max(np.abs(actual - expected)))
    return max_abs_err < 1e-12, max_abs_err


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    write_template()

    smoke_passed, smoke_err = run_smoke_test()
    pd.DataFrame(
        [
            {
                "SmokeTestID": "BACKREACTION_FORMULA_ALGEBRA_SMOKE_TEST",
                "FormulaEngineAlgebraPassed": smoke_passed,
                "MaxAbsError": smoke_err,
                "UsesSourceNativeData": False,
                "AllowedForScoring": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "backreaction_formula_engine_no_measurement_validation",
            }
        ]
    ).to_csv(OUT_SMOKE, index=False)

    vector_exists = INPUT_VECTOR.exists() and INPUT_VECTOR.stat().st_size > 0
    covariance_exists = INPUT_COVARIANCE.exists() and INPUT_COVARIANCE.stat().st_size > 0
    missing_columns: list[str] = REQUIRED_RECONSTRUCTION_COLUMNS.copy()
    rows = 0
    vector_computed = False
    covariance_computed = False
    blocking = []

    if vector_exists:
        vector = pd.read_csv(INPUT_VECTOR)
        rows = len(vector)
        missing_columns = validate_reconstruction_columns(vector.columns)
        if not missing_columns and rows > 0:
            omega = omega_r_plus_3omega_q(
                vector["z"],
                vector["D"],
                vector["D_prime"],
                vector["D_double_prime"],
                vector["H_D"],
                vector["H_D_prime"],
            )
            out = vector[["z"]].copy()
            out["Omega_R_plus_3Omega_Q"] = omega
            out["SourceVector"] = str(INPUT_VECTOR.relative_to(ROOT))
            out["ClaimBoundary"] = "backreaction_formula_engine_no_measurement_validation"
            out.to_csv(OUTPUT_VECTOR, index=False)
            vector_computed = True

            if covariance_exists:
                cov = np.loadtxt(INPUT_COVARIANCE, delimiter=",")
                omega_cov = propagate_omega_covariance(
                    cov,
                    vector["z"],
                    vector["D"],
                    vector["D_prime"],
                    vector["D_double_prime"],
                    vector["H_D"],
                    vector["H_D_prime"],
                )
                np.savetxt(OUTPUT_COVARIANCE, omega_cov, delimiter=",")
                covariance_computed = True
            else:
                blocking.append("source_native_reconstruction_covariance_missing")
        else:
            if rows <= 0:
                blocking.append("source_native_reconstruction_vector_empty")
            if missing_columns:
                blocking.append("missing_required_columns:" + ";".join(missing_columns))
    else:
        blocking.append("source_native_reconstruction_vector_missing")

    if not covariance_exists:
        blocking.append("source_native_reconstruction_covariance_missing")

    allowed_for_backreaction_scoring = vector_computed and covariance_computed
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "BACKREACTION_FORMULA_ENGINE_V1",
                "FormulaEngineAlgebraPassed": smoke_passed,
                "SourceNativeVectorExists": vector_exists,
                "SourceNativeCovarianceExists": covariance_exists,
                "SourceNativeRows": rows,
                "MissingColumns": ";".join(missing_columns),
                "FormulaOutputComputed": vector_computed,
                "FormulaCovarianceComputed": covariance_computed,
                "AllowedForBackreactionScoringNow": allowed_for_backreaction_scoring,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "BACKREACTION_FORMULA_READY_FOR_SCORING_INPUTS"
                    if allowed_for_backreaction_scoring
                    else "BACKREACTION_FORMULA_ENGINE_READY_INPUTS_MISSING"
                ),
                "BlockingIssue": ";".join(dict.fromkeys(blocking)),
                "NextAction": (
                    "score source-native backreaction output against locked K2"
                    if allowed_for_backreaction_scoring
                    else "fill source-native reconstruction vector and covariance; do not digitize figures unless explicitly fallback-labeled"
                ),
                "ClaimBoundary": "backreaction_formula_engine_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)

    lines = [
        "# Backreaction Formula Engine",
        "",
        "Status: algebra validated; source-native scoring input still required.",
        "",
        "The engine computes `Omega_R + 3 Omega_Q` from an externally supplied reconstruction vector. It does not reconstruct the vector, fit amplitudes, or digitize figures.",
        "",
        "## Inputs",
        "",
        f"- Required vector: `{INPUT_VECTOR.relative_to(ROOT)}`",
        f"- Required covariance: `{INPUT_COVARIANCE.relative_to(ROOT)}`",
        f"- Template: `{TEMPLATE.relative_to(ROOT)}`",
        "",
        "## Current Readiness",
        "",
        f"- Algebra smoke test passed: {smoke_passed}",
        f"- Source-native vector exists: {vector_exists}",
        f"- Source-native covariance exists: {covariance_exists}",
        f"- Allowed for backreaction scoring now: {allowed_for_backreaction_scoring}",
        "",
        "Measurement validation remains closed.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {TEMPLATE}")
    print(f"Wrote {OUT_SMOKE}")
    print(f"Wrote {OUT_READINESS}")
    print(f"Wrote {OUT_DOC}")
    if vector_computed:
        print(f"Wrote {OUTPUT_VECTOR}")
    if covariance_computed:
        print(f"Wrote {OUTPUT_COVARIANCE}")


if __name__ == "__main__":
    main()
