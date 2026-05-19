#!/usr/bin/env python3
"""Build a concrete task queue for source-native backreaction reproduction.

The queue translates the missing source-native objects into executable stages:
input validation, reconstruction-family generation, derivative export,
covariance/bootstrap export, and bridge scoring. It is intentionally not a
cosmology likelihood pipeline and does not claim measurement validation.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PUBLIC = DATA / "public_ingest"
BR = DATA / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PANTHEON = PUBLIC / "pantheon_plus" / "Pantheon_SH0ES.dat"
PANTHEON_COV = PUBLIC / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
DESI_DR1_MEAN = PUBLIC / "desi_dr1" / "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR1_COV = PUBLIC / "desi_dr1" / "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt"
DESI_DR2_MEAN = PUBLIC / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
DESI_DR2_COV = PUBLIC / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
UPSTREAM_BAO = BR / "upstream_2604_05822_bao_radial_table.csv"
SN_VALIDATION = EVIDENCE / "source_native_sn_input_validation.csv"
BAO_VALIDATION = EVIDENCE / "source_native_bao_input_validation.csv"
RUNTIME_VALIDATION = EVIDENCE / "source_native_runtime_validation_summary.csv"
ONLINE_SOURCE_SUMMARY = EVIDENCE / "symbolic_regression_online_source_probe_summary.csv"
EXPORT_TEMPLATE_SUMMARY = EVIDENCE / "source_native_backreaction_template_summary.csv"
EXPORT_VALIDATION_SUMMARY = EVIDENCE / "source_native_backreaction_export_validation_summary.csv"
UNCERTAINTY_VALIDATION_SUMMARY = EVIDENCE / "source_native_backreaction_uncertainty_validation_summary.csv"
BRIDGE_SCORE_SUMMARY = EVIDENCE / "source_native_backreaction_bridge_summary.csv"
TRAINING_DATASET_SUMMARY = EVIDENCE / "source_native_training_dataset_summary.csv"
DERIVATIVE_PILOT_SUMMARY = EVIDENCE / "source_native_derivative_pilot_summary.csv"
DERIVATIVE_PILOT_UNCERTAINTY_SUMMARY = EVIDENCE / "source_native_derivative_pilot_uncertainty_summary.csv"

OUT_QUEUE = EVIDENCE / "source_native_reproduction_task_queue.csv"
OUT_READINESS = EVIDENCE / "source_native_reproduction_task_readiness.csv"
OUT_DOC = DOCS / "source_native_reproduction_task_queue.md"


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def validated_sn_inputs() -> bool:
    if not SN_VALIDATION.exists():
        return False
    df = pd.read_csv(SN_VALIDATION)
    return bool(df["AvailableForDInputValidation"].map(bool).all())


def validated_bao_inputs() -> bool:
    if not BAO_VALIDATION.exists():
        return False
    df = pd.read_csv(BAO_VALIDATION)
    return bool(df["AvailableForHDInputValidation"].map(bool).all())


def runtime_minimum_ready() -> bool:
    if not RUNTIME_VALIDATION.exists():
        return False
    df = pd.read_csv(RUNTIME_VALIDATION)
    return bool(df["MinimumFormulaAuditRuntimeReady"].map(bool).all())


def symbolic_runtime_ready() -> bool:
    if not RUNTIME_VALIDATION.exists():
        return False
    df = pd.read_csv(RUNTIME_VALIDATION)
    return bool(df["SymbolicRegressionRuntimeReady"].map(bool).all())


def generic_symbolic_tooling_found() -> bool:
    if not ONLINE_SOURCE_SUMMARY.exists():
        return False
    df = pd.read_csv(ONLINE_SOURCE_SUMMARY)
    return int(df["GenericToolingSources"].iloc[0]) > 0


def export_templates_ready() -> bool:
    if not EXPORT_TEMPLATE_SUMMARY.exists():
        return False
    df = pd.read_csv(EXPORT_TEMPLATE_SUMMARY)
    return bool(df["ReconstructionTemplateCreated"].map(bool).all() and df["SelectionMetadataTemplateCreated"].map(bool).all())


def source_native_exports_ready() -> bool:
    if not EXPORT_VALIDATION_SUMMARY.exists():
        return False
    df = pd.read_csv(EXPORT_VALIDATION_SUMMARY)
    return bool(df["SourceNativeBackreactionExportsReady"].map(bool).all())


def source_native_uncertainty_ready() -> bool:
    if not UNCERTAINTY_VALIDATION_SUMMARY.exists():
        return False
    df = pd.read_csv(UNCERTAINTY_VALIDATION_SUMMARY)
    return bool(df["AnySourceNativeUncertaintyReady"].map(bool).all())


def bridge_score_ready() -> bool:
    if not BRIDGE_SCORE_SUMMARY.exists():
        return False
    df = pd.read_csv(BRIDGE_SCORE_SUMMARY)
    return bool(df["SourceNativeBridgeScoringReady"].map(bool).all())


def training_datasets_ready() -> bool:
    if not TRAINING_DATASET_SUMMARY.exists():
        return False
    df = pd.read_csv(TRAINING_DATASET_SUMMARY)
    return bool(df["TrainingDatasetsReady"].map(bool).all())


def derivative_pilot_ready() -> bool:
    if not DERIVATIVE_PILOT_SUMMARY.exists():
        return False
    df = pd.read_csv(DERIVATIVE_PILOT_SUMMARY)
    return bool(df["DerivativePilotReady"].map(bool).all())


def derivative_pilot_uncertainty_ready() -> bool:
    if not DERIVATIVE_PILOT_UNCERTAINTY_SUMMARY.exists():
        return False
    df = pd.read_csv(DERIVATIVE_PILOT_UNCERTAINTY_SUMMARY)
    return bool(df["BootstrapUncertaintyReady"].map(bool).all())


def task(
    task_id: str,
    stage: str,
    required: bool,
    available: bool,
    blocker: str,
    action: str,
    output: str,
    claim_boundary: str = "source_native_reproduction_task_queue_no_measurement_validation",
) -> dict[str, object]:
    return {
        "TaskID": task_id,
        "Stage": stage,
        "Required": required,
        "CurrentlyAvailable": available,
        "BlocksSourceNativeScoring": required and not available,
        "BlockingIssue": "none" if available else blocker,
        "NextAction": action,
        "ExpectedOutput": output,
        "LockedK2Changed": False,
        "RhoGreaterThan4Allowed": False,
        "K1RefitAllowed": False,
        "MeasurementValidationAllowed": False,
        "ClaimBoundary": claim_boundary,
    }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    has_pantheon = validated_sn_inputs() or (exists(PANTHEON) and exists(PANTHEON_COV))
    has_desi = validated_bao_inputs() or (
        exists(DESI_DR1_MEAN) and exists(DESI_DR1_COV) and exists(DESI_DR2_MEAN) and exists(DESI_DR2_COV)
    )
    has_upstream_bao = exists(UPSTREAM_BAO)
    has_numpy = module_available("numpy")
    has_pandas = module_available("pandas")
    has_pysr = symbolic_runtime_ready() or module_available("pysr")
    has_generic_tooling = generic_symbolic_tooling_found()
    minimum_runtime = runtime_minimum_ready() or (has_numpy and has_pandas)
    templates_ready = export_templates_ready()
    exports_ready = source_native_exports_ready()
    uncertainty_ready = source_native_uncertainty_ready()
    source_bridge_ready = bridge_score_ready()
    training_ready = training_datasets_ready()
    pilot_ready = derivative_pilot_ready()
    pilot_uncertainty_ready = derivative_pilot_uncertainty_ready()

    tasks = [
        task(
            "SN_INPUT_VALIDATE",
            "input_validation",
            True,
            has_pantheon,
            "pantheon_plus_data_or_covariance_missing",
            "validate Pantheon+ redshift, distance-modulus, and covariance columns",
            "evidence/source_native_sn_input_validation.csv",
        ),
        task(
            "BAO_INPUT_VALIDATE",
            "input_validation",
            True,
            has_desi and has_upstream_bao,
            "desi_or_upstream_bao_inputs_missing",
            "validate DESI DR1/DR2 BAO covariance and upstream radial BAO table",
            "evidence/source_native_bao_input_validation.csv",
        ),
        task(
            "RUNTIME_NUMERIC_STACK",
            "runtime_validation",
            True,
            minimum_runtime,
            "minimum_numpy_pandas_stack_missing",
            "install or select runtime with numpy and pandas",
            "evidence/source_native_runtime_validation.csv",
        ),
        task(
            "SYMBOLIC_REGRESSION_ENGINE",
            "runtime_validation",
            True,
            has_pysr or has_generic_tooling,
            "pysr_or_cp3_bench_runtime_missing",
            "choose PySR/cp3-bench route or request author expression exports",
            "evidence/source_native_symbolic_regression_runtime.csv",
        ),
        task(
            "SOURCE_NATIVE_TRAINING_DATASETS",
            "training_input_export",
            True,
            training_ready,
            "source_native_training_datasets_missing",
            "export public SN D-proxy and radial BAO H_D-proxy training inputs for the reproduction route",
            "data/physical_nulls/backreaction_reproduction/source_native_training_sn_distance_proxy.csv;data/physical_nulls/backreaction_reproduction/source_native_training_bao_hd_proxy.csv",
        ),
        task(
            "DERIVATIVE_PILOT_PREFLIGHT",
            "formula_path_stress_test",
            False,
            pilot_ready,
            "derivative_pilot_missing",
            "build fixed polynomial derivative pilot from public SN/BAO training inputs without fitting K2",
            "data/physical_nulls/backreaction_reproduction/source_native_derivative_pilot_reconstruction_vector.csv",
        ),
        task(
            "DERIVATIVE_PILOT_UNCERTAINTY",
            "formula_path_stress_test",
            False,
            pilot_uncertainty_ready,
            "derivative_pilot_bootstrap_uncertainty_missing",
            "bootstrap the fixed polynomial derivative pilot using public diagonal training-input errors",
            "data/physical_nulls/backreaction_reproduction/source_native_derivative_pilot_bootstrap_omega_samples.csv",
        ),
        task(
            "D_RECONSTRUCTION_FAMILY",
            "reconstruction",
            True,
            False,
            "D_Dprime_Ddoubleprime_symbolic_family_missing",
            "reproduce or obtain symbolic expressions for D,D_prime,D_double_prime from Pantheon+",
            "data/physical_nulls/backreaction_reproduction/source_native_D_family_samples.csv",
        ),
        task(
            "HD_RECONSTRUCTION_FAMILY",
            "reconstruction",
            True,
            False,
            "HD_HDprime_symbolic_family_missing",
            "reproduce or obtain symbolic expressions for H_D,H_D_prime from BAO families",
            "data/physical_nulls/backreaction_reproduction/source_native_HD_family_samples.csv",
        ),
        task(
            "FAMILY_METADATA_EXPORT",
            "metadata",
            True,
            exports_ready,
            "selection_family_metadata_missing",
            "provide source_native_selection_metadata.csv using the generated template",
            "data/physical_nulls/backreaction_reproduction/source_native_selection_metadata.csv",
        ),
        task(
            "BACKREACTION_VECTOR_EXPORT",
            "formula_application",
            True,
            exports_ready,
            "source_native_omega_vector_missing",
            "provide valid source_native_reconstruction_vector.csv; validator will apply fixed formula",
            "data/physical_nulls/backreaction_reproduction/source_native_backreaction_vector.csv",
        ),
        task(
            "BACKREACTION_COVARIANCE_EXPORT",
            "uncertainty",
            True,
            uncertainty_ready,
            "source_native_covariance_or_bootstrap_missing",
            "export bootstrap samples and/or covariance for Omega_R_plus_3Omega_Q",
            "data/physical_nulls/backreaction_reproduction/source_native_backreaction_covariance.csv",
        ),
        task(
            "K2_BRIDGE_SOURCE_NATIVE_SCORE",
            "bridge_scoring",
            True,
            source_bridge_ready,
            "source_native_vector_and_covariance_missing",
            "score source-native backreaction bridge against locked K2 without changing K2",
            "evidence/source_native_backreaction_bridge_scorecard.csv",
        ),
    ]
    queue = pd.DataFrame(tasks)
    queue.to_csv(OUT_QUEUE, index=False)

    required = queue[queue["Required"].map(bool)]
    blocking = required[required["BlocksSourceNativeScoring"].map(bool)]
    readiness = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_REPRODUCTION_TASK_QUEUE_V1",
                "RequiredTasks": len(required),
                "AvailableRequiredTasks": int(required["CurrentlyAvailable"].map(bool).sum()),
                "BlockingTasks": len(blocking),
                "PantheonInputReady": has_pantheon,
                "BAOInputReady": has_desi and has_upstream_bao,
                "NumericRuntimeReady": minimum_runtime,
                "SymbolicRegressionRuntimeReady": has_pysr,
                "GenericSymbolicToolingFound": has_generic_tooling,
                "TrainingDatasetsReady": training_ready,
                "DerivativePilotReady": pilot_ready,
                "DerivativePilotUncertaintyReady": pilot_uncertainty_ready,
                "ExportTemplatesReady": templates_ready,
                "SourceNativeExportsReady": exports_ready,
                "SourceNativeUncertaintyReady": uncertainty_ready,
                "SourceNativeBridgeScoreReady": source_bridge_ready,
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "SOURCE_NATIVE_REPRODUCTION_BLOCKED_ON_SYMBOLIC_FAMILY_EXPORTS"
                    if has_pantheon and has_desi and has_upstream_bao
                    else "SOURCE_NATIVE_REPRODUCTION_BLOCKED_ON_PUBLIC_INPUTS"
                ),
                "StrongestAllowedClaim": (
                    "public SN and BAO training inputs are locally exported and the source-native reproduction queue is executable in stages, "
                    "but symbolic-regression family exports and covariance are still missing"
                ),
                "PrimaryResidualRisk": "author symbolic-expression selection choices may not be reproduced exactly without source exports",
                "NextAction": "run or obtain symbolic-regression family exports for D,D_prime,D_double_prime,H_D,H_D_prime, then attach bootstrap/covariance",
                "ClaimBoundary": "source_native_reproduction_task_queue_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Reproduction Task Queue",
                "",
                "Status: staged reproduction route declared; source-native scoring remains blocked.",
                "",
                "This queue separates available public inputs from the missing symbolic-regression family exports. It does not alter locked K2, fit K1, or authorize measurement validation.",
                "",
                "## Current bottleneck",
                "",
                "The local repo contains Pantheon+ and DESI inputs, and now exports public SN/BAO training tables for the reproduction route. It still does not contain the source-native symbolic-expression families or bootstrap/covariance exports needed to reproduce the published backreaction families.",
                "",
                "## Outputs",
                "",
                f"- Task queue: `{OUT_QUEUE.relative_to(ROOT)}`",
                f"- Readiness: `{OUT_READINESS.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_QUEUE}")
    print(f"Wrote {OUT_READINESS}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
