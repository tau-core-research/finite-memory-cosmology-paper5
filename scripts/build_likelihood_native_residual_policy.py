#!/usr/bin/env python3
"""Freeze candidate residual policies for the full likelihood-native route.

The policies remove the residual-definition ambiguity that blocked FLN_1/FLN_2.
They do not authorize measurement validation; they only define the next locked
rerun candidate.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PARAMS = DATA / "k1" / "source_split_likelihood_native_parameters.yaml"
SN_TABLE = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
SN_COV = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_MEAN = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
BAO_COV = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
L_SN = DATA / "transforms" / "k2_a2_l_sn_transform_v1.csv"
L_BAO = DATA / "transforms" / "k2_a2_l_bao_transform_v1.csv"

OUT_POLICY = EVIDENCE / "likelihood_native_residual_policy.csv"
OUT_READINESS = EVIDENCE / "likelihood_native_residual_policy_readiness.csv"
OUT_SN = DATA / "residuals" / "sn_cmb_only_raw_residual_v1.csv"
OUT_BAO = DATA / "residuals" / "bao_cmb_only_log_residual_v1.csv"
OUT_CANDIDATE = EVIDENCE / "likelihood_native_residual_candidate_summary.csv"
OUT_DOC = DOCS / "likelihood_native_residual_policy.md"


def parse_scalar(value: str) -> object:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return float(value)
    except ValueError:
        return value


def read_simple_yaml(path: Path) -> dict[str, object]:
    result: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1]
            result[current_key] = {}
            continue
        if not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key] = parse_scalar(value)
            current_key = None
            continue
        if current_key and ":" in line:
            key, value = line.strip().split(":", 1)
            assert isinstance(result[current_key], dict)
            result[current_key][key] = parse_scalar(value)
    return result


def load_flat_covariance(path: Path) -> np.ndarray:
    values = np.loadtxt(path)
    declared = int(values[0])
    flat = values[1:]
    if len(flat) != declared * declared:
        raise ValueError("SN covariance length mismatch")
    return flat.reshape((declared, declared))


def main() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from fmc.bao_transform import bao_log_residual_transform
    from fmc.public_data import load_bao_mean, load_pantheon_table, load_square_covariance
    from fmc.sn_transform import sn_residual_transform

    params_doc = read_simple_yaml(PARAMS)
    params = params_doc["parameters"]
    assert isinstance(params, dict)
    baseline = {
        "baseline_id": str(params_doc["baseline_id"]),
        "H0": float(params["H0"]),
        "omega_m": float(params["OmegaM"]),
        "rd_mpc": float(params["rd_mpc"]),
    }

    sn_table = load_pantheon_table(SN_TABLE)
    sn_cov = load_flat_covariance(SN_COV)
    sn_rows = sn_residual_transform(sn_table, sn_cov, "PANTHEON_PLUS_SH0ES_SN", baseline=baseline)
    sn_candidate = sn_rows[
        [
            "RowID",
            "z",
            "ObservedMu",
            "AuditPredictionMu",
            "RawResidualMu",
            "SigmaDiag",
            "CovarianceIndex",
            "BaselineID",
        ]
    ].copy()
    sn_candidate = sn_candidate.rename(columns={"AuditPredictionMu": "CMBOnlyPredictionMu"})
    sn_candidate["ResidualPolicyID"] = "SN_RAW_CMB_ONLY_NO_SAME_SAMPLE_OFFSET_V1"
    sn_candidate["SameSampleOffsetUsed"] = False
    sn_candidate["AllowedForRerunCandidate"] = True
    sn_candidate["MeasurementValidationAllowed"] = False

    bao_mean = load_bao_mean(BAO_MEAN)
    bao_cov = load_square_covariance(BAO_COV)
    bao_rows, bao_residual_cov = bao_log_residual_transform(bao_mean, bao_cov, "DESI_DR2_BAO_ALL_GAUSSIAN", baseline=baseline)
    bao_candidate = bao_rows[
        [
            "RowID",
            "Quantity",
            "z",
            "ObservedValue",
            "AuditPrediction",
            "LogResidual",
            "SigmaDiag",
            "CovarianceIndex",
            "BaselineID",
        ]
    ].copy()
    bao_candidate = bao_candidate.rename(columns={"AuditPrediction": "CMBOnlyPrediction"})
    bao_candidate["ResidualPolicyID"] = "BAO_LOG_CMB_ONLY_RD_FIXED_V1"
    bao_candidate["rd_mpc"] = baseline["rd_mpc"]
    bao_candidate["AllowedForRerunCandidate"] = True
    bao_candidate["MeasurementValidationAllowed"] = False

    OUT_SN.parent.mkdir(parents=True, exist_ok=True)
    sn_candidate.to_csv(OUT_SN, index=False)
    bao_candidate.to_csv(OUT_BAO, index=False)

    policy_rows = [
        {
            "PolicyID": "SN_RAW_CMB_ONLY_NO_SAME_SAMPLE_OFFSET_V1",
            "ResolvesContract": "RDEF_SN_1_OBSERVABLE;RDEF_SN_2_OFFSET_POLICY",
            "PolicyClass": "sn_residual_policy",
            "Definition": "r_SN = MU_SH0ES - mu_CMB_only_LCDM(z)",
            "BaselineSource": str(PARAMS.relative_to(ROOT)),
            "UsesSameSampleOffset": False,
            "UsesExternalFrozenBaseline": True,
            "AllowedForRerunCandidate": True,
            "MeasurementValidationAllowed": False,
            "ResidualRisk": "SN absolute-magnitude/nuisance treatment is fixed by using the public distance-modulus table and external baseline; no same-sample centering is used",
            "NextAction": "propagate through declared L_SN and joint covariance; keep nuisance caveat in report",
        },
        {
            "PolicyID": "BAO_LOG_CMB_ONLY_RD_FIXED_V1",
            "ResolvesContract": "RDEF_BAO_1_OBSERVABLE;RDEF_BAO_2_RS_POLICY",
            "PolicyClass": "bao_residual_policy",
            "Definition": "r_BAO = log(observed / prediction_CMB_only_LCDM) for DH/DM/DV over rs",
            "BaselineSource": str(PARAMS.relative_to(ROOT)),
            "UsesSameSampleOffset": False,
            "UsesExternalFrozenBaseline": True,
            "AllowedForRerunCandidate": True,
            "MeasurementValidationAllowed": False,
            "ResidualRisk": "BAO residual amplitude depends on externally frozen CMB-only rd policy",
            "NextAction": "propagate through declared L_BAO and joint covariance; do not refit rd",
        },
        {
            "PolicyID": "LSN_DECLARED_LINEAR_PROJECTION_V1",
            "ResolvesContract": "RDEF_SN_3_GRID_TRANSFORM",
            "PolicyClass": "sn_transform_policy",
            "Definition": "use predeclared L_SN linear projection matrix on raw SN residual vector",
            "BaselineSource": str(L_SN.relative_to(ROOT)),
            "UsesSameSampleOffset": False,
            "UsesExternalFrozenBaseline": True,
            "AllowedForRerunCandidate": L_SN.exists(),
            "MeasurementValidationAllowed": False,
            "ResidualRisk": "projection matrix is declared for candidate rerun but still requires final covariance adjudication",
            "NextAction": "rerun source-split vector with this L_SN and report route as candidate only",
        },
        {
            "PolicyID": "LBAO_DECLARED_LINEAR_PROJECTION_V1",
            "ResolvesContract": "RDEF_BAO_3_GRID_TRANSFORM",
            "PolicyClass": "bao_transform_policy",
            "Definition": "use predeclared L_BAO linear projection matrix on BAO log residual vector",
            "BaselineSource": str(L_BAO.relative_to(ROOT)),
            "UsesSameSampleOffset": False,
            "UsesExternalFrozenBaseline": True,
            "AllowedForRerunCandidate": L_BAO.exists(),
            "MeasurementValidationAllowed": False,
            "ResidualRisk": "projection matrix is declared for candidate rerun but still requires final covariance adjudication",
            "NextAction": "rerun source-split vector with this L_BAO and report route as candidate only",
        },
    ]
    policy = pd.DataFrame(policy_rows)
    policy["ClaimBoundary"] = "residual_policy_candidate_no_measurement_validation"
    policy.to_csv(OUT_POLICY, index=False)

    resolved_contracts = sorted(
        {
            item
            for values in policy.loc[policy["AllowedForRerunCandidate"].astype(bool), "ResolvesContract"]
            for item in str(values).split(";")
            if item
        }
    )
    summary = pd.DataFrame(
        [
            {
                "PolicySetID": "LIKELIHOOD_NATIVE_RESIDUAL_POLICY_CANDIDATE_V1",
                "Policies": len(policy),
                "PoliciesAllowedForRerunCandidate": int(policy["AllowedForRerunCandidate"].astype(bool).sum()),
                "ResolvedResidualContracts": len(resolved_contracts),
                "ResolvedResidualContractIDs": ";".join(resolved_contracts),
                "SNRows": len(sn_candidate),
                "BAORows": len(bao_candidate),
                "BaselineID": baseline["baseline_id"],
                "H0": baseline["H0"],
                "OmegaM": baseline["omega_m"],
                "rd_mpc": baseline["rd_mpc"],
                "SameSampleOffsetUsed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "RESIDUAL_BLOCKERS_RESOLVED_FOR_LOCKED_RERUN_CANDIDATE",
                "StrongestAllowedClaim": "SN and BAO residual-definition blockers are resolved for an unchanged locked-A2 rerun candidate",
                "PrimaryResidualRisk": "candidate route still requires joint covariance adjudication and cannot be read as measurement validation",
                "NextAction": "build candidate y_split and C_split using frozen residual policies, then rerun K1/null/A2 scorecard unchanged",
                "ClaimBoundary": "residual_policy_candidate_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_READINESS, index=False)

    candidate = pd.DataFrame(
        [
            {
                "CandidateID": "SN_RAW_CMB_ONLY_NO_SAME_SAMPLE_OFFSET_V1",
                "Rows": len(sn_candidate),
                "MeanResidual": float(sn_candidate["RawResidualMu"].mean()),
                "MedianResidual": float(sn_candidate["RawResidualMu"].median()),
                "MedianSigma": float(sn_candidate["SigmaDiag"].median()),
                "AllowedForRerunCandidate": True,
                "MeasurementValidationAllowed": False,
            },
            {
                "CandidateID": "BAO_LOG_CMB_ONLY_RD_FIXED_V1",
                "Rows": len(bao_candidate),
                "MeanResidual": float(bao_candidate["LogResidual"].mean()),
                "MedianResidual": float(bao_candidate["LogResidual"].median()),
                "MedianSigma": float(bao_candidate["SigmaDiag"].median()),
                "AllowedForRerunCandidate": True,
                "MeasurementValidationAllowed": False,
            },
        ]
    )
    candidate["ClaimBoundary"] = "residual_candidate_no_measurement_validation"
    candidate.to_csv(OUT_CANDIDATE, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Likelihood-Native Residual Policy",
        "",
        "Status: residual blockers are resolved for a locked rerun candidate. Measurement validation remains closed.",
        "",
        "## Policy Summary",
        "",
        f"- Baseline: {baseline['baseline_id']}",
        f"- H0: {baseline['H0']}",
        f"- OmegaM: {baseline['omega_m']}",
        f"- rd_mpc: {baseline['rd_mpc']}",
        f"- Resolved residual contracts: {len(resolved_contracts)}/6",
        "- Same-sample offset used: False",
        "- Measurement validation allowed: False",
        "",
        "## Policies",
        "",
    ]
    for _, row in policy.iterrows():
        lines.extend(
            [
                f"### {row['PolicyID']}",
                "",
                f"- Class: {row['PolicyClass']}",
                f"- Resolves: {row['ResolvesContract']}",
                f"- Definition: {row['Definition']}",
                f"- Rerun candidate: {row['AllowedForRerunCandidate']}",
                f"- Residual risk: {row['ResidualRisk']}",
                f"- Next action: {row['NextAction']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "The locked A2 prediction is unchanged. These policies only define the residual route for the next candidate rerun.",
            "",
        ]
    )
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_POLICY}")
    print(f"Wrote {OUT_READINESS}")
    print(f"Wrote {OUT_SN}")
    print(f"Wrote {OUT_BAO}")
    print(f"Wrote {OUT_CANDIDATE}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
