#!/usr/bin/env python3
"""Build frozen parameter source for the likelihood-native source-split K1 route."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CMB_BESTFIT = ROOT / "data" / "public_ingest" / "desi_dr2_bestfit" / "base_cmb_only" / "bestfit.minimum.txt"
DESI_BESTFIT = ROOT / "data" / "public_ingest" / "desi_dr2_bestfit" / "base_desi_bao_all" / "bestfit.minimum.txt"
OUT = ROOT / "data" / "k1" / "source_split_likelihood_native_parameters.yaml"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_parameters_summary.csv"
BASELINE_PREDICTION = ROOT / "data" / "k1" / "source_split_likelihood_native_baseline_prediction.csv"
COORDINATE_MAP = ROOT / "data" / "k1" / "source_split_likelihood_native_coordinate_map.csv"


def load_bestfit(path: Path) -> dict[str, float]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    header = lines[0].lstrip("#").split()
    values = lines[1].split()
    return dict(zip(header, map(float, values)))


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return f'"{value}"'


def main() -> None:
    cmb = load_bestfit(CMB_BESTFIT)
    desi = load_bestfit(DESI_BESTFIT)
    h0 = float(cmb["H0"])
    omega_m = float(cmb["omegam"])
    rd = float(cmb["rdrag"])

    baseline_issue = (
        "baseline_prediction_preflight_not_primary"
        if BASELINE_PREDICTION.exists()
        else "baseline_prediction_vector_missing"
    )
    coordinate_issue = (
        "coordinate_map_preflight_not_promoted"
        if COORDINATE_MAP.exists()
        else "likelihood_native_coordinate_map_missing"
    )

    data = {
        "baseline_id": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_CMB_ONLY_BASELINE_V1",
        "source_product_ids": [
            "PANTHEON_PLUS_SH0ES_SN",
            "DESI_DR2_BAO_ALL_GAUSSIAN",
        ],
        "parameter_source": "public_cmb_only_bestfit_preflight",
        "parameter_source_file": str(CMB_BESTFIT.relative_to(ROOT)),
        "comparison_control_source_file": str(DESI_BESTFIT.relative_to(ROOT)),
        "frozen_before_k2_scoring": True,
        "fitted_in_this_note": False,
        "same_data_amplitude_fit": False,
        "likelihood_native": False,
        "coordinate_native": False,
        "allowed_for_k1_export_now": False,
        "required_next_step": "promote baseline prediction vector, coordinate map, and covariance policy before K1 export",
        "parameters": {
            "H0": h0,
            "OmegaM": omega_m,
            "rd_mpc": rd,
            "omega_m_h2": float(cmb["omegamh2"]),
            "OmegaLambda": float(cmb["omegal"]),
            "sigma8": float(cmb["sigma8"]),
        },
        "diagnostic_controls": {
            "cmb_reported_chi2": float(cmb["chi2__CMB"]),
            "desi_same_data_reported_chi2_bao": float(desi["chi2__BAO"]),
            "desi_same_data_H0": float(desi["H0rdrag"]) / float(desi["rdrag"]),
            "desi_same_data_OmegaM": float(desi["omegam"]),
            "desi_same_data_rd_mpc": float(desi["rdrag"]),
        },
        "claim_boundary": "frozen_parameter_source_only_no_measurement_validation",
    }

    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {yaml_scalar(item)}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for subkey, subvalue in value.items():
                lines.append(f"  {subkey}: {yaml_scalar(subvalue)}")
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    pd.DataFrame(
        [
            {
                "ParameterSourceID": data["baseline_id"],
                "OutputPath": str(OUT.relative_to(ROOT)),
                "ParameterSource": data["parameter_source"],
                "H0": h0,
                "OmegaM": omega_m,
                "RdMpc": rd,
                "FrozenBeforeK2Scoring": True,
                "FittedInThisNote": False,
                "SameDataAmplitudeFit": False,
                "AllowedForK1ExportNow": False,
                "BlockingIssue": f"{baseline_issue};{coordinate_issue}",
                "NextAction": data["required_next_step"],
                "ClaimBoundary": data["claim_boundary"],
            }
        ]
    ).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
