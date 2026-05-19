#!/usr/bin/env python3
"""Build the PySR criteria-set-3 reproduction contract.

This is a runtime/readiness artifact for the source-native backreaction branch.
It records a locked, non-fitting route for reproducing the upstream
criteria-set-3 symbolic-regression path. It does not change K2, refit K1, or
authorize measurement validation.
"""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FROZEN = ROOT / "frozen"

PROTOCOL_SUMMARY = EVIDENCE / "source_native_symbolic_protocol_extract_summary.csv"
BAO_TABLE = EVIDENCE / "source_native_symbolic_protocol_bao_table_extract.csv"
TRAINING_SUMMARY = EVIDENCE / "source_native_training_dataset_summary.csv"
SN_TRAINING = DATA / "source_native_training_sn_distance_proxy.csv"
BAO_TRAINING = DATA / "source_native_training_bao_hd_proxy.csv"

OUT_CONFIG = DATA / "pysr_criteria3_reproduction_config.yaml"
OUT_CONTRACT = EVIDENCE / "pysr_criteria3_reproduction_contract.csv"
OUT_READINESS = EVIDENCE / "pysr_criteria3_reproduction_readiness.csv"
OUT_SUMMARY = EVIDENCE / "pysr_criteria3_reproduction_contract_summary.csv"
OUT_DOC = DOCS / "pysr_criteria3_reproduction_contract.md"

CLAIM_BOUNDARY = "pysr_criteria3_reproduction_contract_no_measurement_validation"


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def private_julia_available() -> bool:
    candidates = [
        Path.home()
        / ".julia"
        / "environments"
        / "pyjuliapkg"
        / "pyjuliapkg"
        / "install"
        / "bin"
        / "julia",
        Path.home()
        / ".julia"
        / "environments"
        / "pyjuliapkg"
        / "pyjuliapkg"
        / "install"
        / "Julia.app"
        / "Contents"
        / "Resources"
        / "julia"
        / "bin"
        / "julia",
    ]
    return any(path.exists() for path in candidates)


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def rows_available(path: Path) -> tuple[bool, int]:
    if not path.exists():
        return False, 0
    df = pd.read_csv(path)
    return not df.empty, int(len(df))


def write_yaml_like(path: Path, content: dict[str, object]) -> None:
    lines: list[str] = []
    for key, value in content.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    lines.append(f"  {sub_key}:")
                    for item in sub_value:
                        lines.append(f"    - {item}")
                else:
                    lines.append(f"  {sub_key}: {sub_value}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    FROZEN.mkdir(parents=True, exist_ok=True)

    protocol_ready = PROTOCOL_SUMMARY.exists()
    bao_ready, bao_rows = rows_available(BAO_TABLE)
    sn_ready, sn_rows = rows_available(SN_TRAINING)
    hd_ready, hd_rows = rows_available(BAO_TRAINING)
    training_summary_ready = TRAINING_SUMMARY.exists()

    pysr_ready = module_available("pysr")
    sympy_ready = module_available("sympy")
    sklearn_ready = module_available("sklearn")
    scipy_ready = module_available("scipy")
    yaml_ready = module_available("yaml")
    julia_on_path = shutil.which("julia") is not None
    julia_private = private_julia_available()
    julia_ready = julia_on_path or julia_private
    runtime_ready = pysr_ready and sympy_ready and sklearn_ready and scipy_ready and julia_ready
    inputs_ready = protocol_ready and bao_ready and sn_ready and hd_ready and training_summary_ready
    execution_ready = runtime_ready and inputs_ready

    config = {
        "route_id": "PYSR_CRITERIA_SET_3_REPRODUCTION_V1",
        "status": "runtime_available" if execution_ready else "contract_only",
        "claim_boundary": CLAIM_BOUNDARY,
        "locked_tau_core_flags": {
            "change_k2_kernel_allowed": "false",
            "rho_greater_than_4_allowed": "false",
            "k1_refit_allowed": "false",
            "target_sign_gate_allowed": "false",
            "amplitude_fit_allowed": "false",
            "measurement_validation_allowed": "false",
        },
        "inputs": {
            "sn_distance_proxy": str(SN_TRAINING.relative_to(ROOT)),
            "bao_hd_proxy": str(BAO_TRAINING.relative_to(ROOT)),
            "upstream_bao_table_extract": str(BAO_TABLE.relative_to(ROOT)),
            "upstream_protocol_extract": str(PROTOCOL_SUMMARY.relative_to(ROOT)),
        },
        "targets": {
            "sn_route": "d_A_proxy and log-distance proxy from public SN training input",
            "bao_route": "H_D proxy from radial BAO c_over_Hrs table",
            "future_required_export": "D, D_prime, D_double_prime, H_D, H_D_prime on the shared redshift grid",
        },
        "criteria_set_3": {
            "selector": "single expression minimizing Loss + 1.0 * Complexity",
            "operator_set": "PySR/SymbolicRegression hall-of-fame route",
            "manual_hof_rejection": "not used in criteria-set-3 MVP",
            "bootstrap_target": "200 accepted expressions when runtime budget allows",
        },
        "required_outputs": [
            "source_native_reconstruction_vector.csv",
            "source_native_selection_metadata.csv",
            "source_native_backreaction_vector.csv",
            "source_native_backreaction_family_covariance.csv",
            "source_native_bootstrap_samples.csv",
        ],
    }
    write_yaml_like(OUT_CONFIG, config)

    contract_rows = [
        {
            "ContractID": "PYSR_CRITERIA_SET_3_REPRODUCTION_V1",
            "StepID": "C3_INPUTS",
            "Requirement": "SN and BAO training inputs plus upstream protocol extract are available",
            "Ready": inputs_ready,
            "BlockingIssue": "" if inputs_ready else "missing input extract or training table",
            "NextAction": "run criteria-set-3 reproduction route",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ContractID": "PYSR_CRITERIA_SET_3_REPRODUCTION_V1",
            "StepID": "C3_RUNTIME",
            "Requirement": "PySR stack and Julia runtime are available",
            "Ready": runtime_ready,
            "BlockingIssue": "" if runtime_ready else "install PySR stack and Julia runtime",
            "NextAction": "run a small PySR smoke route before long bootstrap",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ContractID": "PYSR_CRITERIA_SET_3_REPRODUCTION_V1",
            "StepID": "C3_SELECTION",
            "Requirement": "Use criteria set 3: minimize Loss + 1.0 * Complexity",
            "Ready": execution_ready,
            "BlockingIssue": "" if execution_ready else "inputs or runtime not ready",
            "NextAction": "export selected expressions and derivatives on shared grid",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ContractID": "PYSR_CRITERIA_SET_3_REPRODUCTION_V1",
            "StepID": "C3_CLAIM_LOCK",
            "Requirement": "Do not alter K2, rho, p, A_tau, or K1 while running reproduction",
            "Ready": True,
            "BlockingIssue": "",
            "NextAction": "keep reproduction outputs separate from measurement language",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
    ]
    pd.DataFrame(contract_rows).to_csv(OUT_CONTRACT, index=False)

    current_status = (
        "PYSR_CRITERIA3_CONTRACT_READY_RUNTIME_AVAILABLE"
        if execution_ready
        else "PYSR_CRITERIA3_CONTRACT_READY_RUNTIME_BLOCKED"
    )
    strongest_claim = (
        "the upstream criteria-set-3 symbolic-regression route is specified and locally executable"
        if execution_ready
        else "the upstream criteria-set-3 symbolic-regression route is specified but not yet executable locally"
    )
    residual_risk = (
        "criteria-set-3 can be run, but source-native covariance and author derivative exports remain unavailable"
        if execution_ready
        else "runtime or input availability still blocks even the criteria-set-3 reproduction route"
    )

    readiness = pd.DataFrame(
        [
            {
                "AuditID": "PYSR_CRITERIA3_REPRODUCTION_CONTRACT_V1",
                "ProtocolExtractReady": protocol_ready,
                "BAOTableExtractReady": bao_ready,
                "BAOTableRows": bao_rows,
                "SNTrainingInputReady": sn_ready,
                "SNTrainingRows": sn_rows,
                "HDTrainingInputReady": hd_ready,
                "HDTrainingRows": hd_rows,
                "TrainingSummaryReady": training_summary_ready,
                "PySRAvailable": pysr_ready,
                "SympyAvailable": sympy_ready,
                "SklearnAvailable": sklearn_ready,
                "ScipyAvailable": scipy_ready,
                "PyYAMLAvailable": yaml_ready,
                "JuliaOnPath": julia_on_path,
                "PrivateJuliaAvailable": julia_private,
                "JuliaAvailable": julia_ready,
                "InputsReady": inputs_ready,
                "RuntimeReady": runtime_ready,
                "ExecutionReady": execution_ready,
                "CriteriaSet3ExecutableByProtocol": True,
                "SourceNativeExportReady": False,
                "SourceNativeCovarianceReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": current_status,
                "StrongestAllowedClaim": strongest_claim,
                "PrimaryResidualRisk": residual_risk,
                "NextAction": (
                    "run a small criteria-set-3 smoke reproduction, then scale to bootstrap derivative exports"
                    if execution_ready
                    else "install the missing runtime dependency, then rerun this contract"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    readiness.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# PySR Criteria-Set-3 Reproduction Contract",
                "",
                f"Status: {current_status}.",
                "",
                "This contract turns the upstream criteria-set-3 symbolic-regression route into a local execution target. It is a reproduction preflight, not measurement validation.",
                "",
                "## Runtime",
                "",
                f"- PySR available: {pysr_ready}",
                f"- SymPy available: {sympy_ready}",
                f"- scikit-learn available: {sklearn_ready}",
                f"- SciPy available: {scipy_ready}",
                f"- Julia on PATH: {julia_on_path}",
                f"- Private Julia available through juliacall: {julia_private}",
                f"- Execution ready: {execution_ready}",
                "",
                "## Locked Constraints",
                "",
                "- Do not change the K2 kernel.",
                "- Do not allow rho > 4.",
                "- Do not refit K1.",
                "- Do not use target-sign gates.",
                "- Do not use amplitude fitting.",
                "- Do not treat this route as measurement validation.",
                "",
                "## Next Action",
                "",
                str(readiness.iloc[0]["NextAction"]),
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_READINESS.relative_to(ROOT)}")
    print(f"Wrote {OUT_CONTRACT.relative_to(ROOT)}")
    print(f"Wrote {OUT_CONFIG.relative_to(ROOT)}")
    print(f"Wrote {OUT_DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
