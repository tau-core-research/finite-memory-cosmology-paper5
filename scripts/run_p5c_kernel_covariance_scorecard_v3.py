#!/usr/bin/env python3
"""Run the P5C covariance/operator-kernel scorecard for kernel v3.

This wrapper preserves the v0-v2 covariance scorecard family while switching
the v3 primary artifact to the frozen PSD covariance-deformation projection.
It should be run only after the v3 final scoring authorization validator passes.
For the random-smooth PSD null family, v3 evaluates all frozen random PSD
members and uses the strongest aggregate null for the survival gate.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
spec = importlib.util.spec_from_file_location("p5c_v0", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load v0 scorecard module.")
p5c_v0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p5c_v0)

p5c_v0.KERNEL = ROOT / "evidence/p5c_bstar_kernel_v3_psd_projection.csv"
p5c_v0.NULLS = ROOT / "evidence/p5c_bstar_kernel_v3_null_kernels.csv"
p5c_v0.MANIFEST = ROOT / "evidence/p5c_bstar_kernel_v3_manifest.yaml"
p5c_v0.OUT_IN_SAMPLE = ROOT / "evidence/p5c_kernel_covariance_scorecard_v3.csv"
p5c_v0.OUT_OOS = ROOT / "evidence/p5c_kernel_covariance_oos_scorecard_v3.csv"
p5c_v0.OUT_NULLS = ROOT / "evidence/p5c_kernel_covariance_null_scorecard_v3.csv"
p5c_v0.OUT_GATES = ROOT / "evidence/p5c_kernel_covariance_survival_gates_v3.csv"
p5c_v0.OUT_SUMMARY = ROOT / "evidence/p5c_kernel_covariance_summary_v3.csv"
p5c_v0.OUT_DOC = ROOT / "docs/p5c_kernel_covariance_scorecard_v3.md"
p5c_v0.AUDIT_ID = "P5C_KERNEL_COVARIANCE_SCORECARD_V3"
p5c_v0.KERNEL_ID = "K_BSTAR_P5C_v3_RESIDUAL_COMPLEX_ORIENTATION_PSD_PROJECTION"
p5c_v0.KERNEL_STATUS_TAG = "V3"
p5c_v0.CLAIM_BOUNDARY = "p5c_kernel_covariance_scorecard_v3_no_measurement_validation"

_BASE_MATRIX_FROM_LONG = p5c_v0.matrix_from_long
_NULL_ID_MAP = {
    "K_WRONG_CLOCK": "K_WRONG_CLOCK_PSD",
    "K_PHASE_SHIFTED": "K_PHASE_SHIFTED_PSD",
    "K_FAMILY_PERMUTED": "K_FAMILY_PERMUTED_PSD",
    "K_IDENTITY_DIAGONAL": "K_IDENTITY_DIAGONAL_PSD",
}


def matrix_from_long_v3(path: Path, kernel_id: str, n: int):
    return _BASE_MATRIX_FROM_LONG(path, _NULL_ID_MAP.get(kernel_id, kernel_id), n)


p5c_v0.matrix_from_long = matrix_from_long_v3


def main() -> int:
    import numpy as np
    import pandas as pd
    import yaml

    manifest = yaml.safe_load(p5c_v0.MANIFEST.read_text(encoding="utf-8"))
    if manifest["pre_score_status"] != "FREEZE_READY":
        raise RuntimeError("P5C kernel is not freeze ready.")

    rows = p5c_v0.load_rows()
    kernel = p5c_v0.matrix_from_long(p5c_v0.KERNEL, p5c_v0.KERNEL_ID, len(rows))
    real_ins, real_oos = p5c_v0.score_all(rows, kernel, p5c_v0.KERNEL_ID)

    null_specs = [
        ("K_WRONG_CLOCK", "K_WRONG_CLOCK_PSD"),
        ("K_PHASE_SHIFTED", "K_PHASE_SHIFTED_PSD"),
        ("K_FAMILY_PERMUTED", "K_FAMILY_PERMUTED_PSD"),
        ("K_IDENTITY_DIAGONAL", "K_IDENTITY_DIAGONAL_PSD"),
    ]
    null_df = pd.read_csv(p5c_v0.NULLS)
    random_ids = sorted(
        kernel_id
        for kernel_id in null_df["KernelID"].unique()
        if str(kernel_id).startswith("K_RANDOM_SMOOTH_PSD_")
    )

    null_rows = []
    for display_id, source_id in null_specs:
        mat = _BASE_MATRIX_FROM_LONG(p5c_v0.NULLS, source_id, len(rows))
        _, oos = p5c_v0.score_all(rows, mat, display_id)
        null_rows.append(
            {
                "AuditID": p5c_v0.AUDIT_ID,
                "ProtocolID": p5c_v0.PROTOCOL_ID,
                "KernelID": display_id,
                "SourceKernelID": source_id,
                "PrimaryOOSDeltaNLL_BaselineMinusKernel": float(
                    oos[oos["PrimaryOOS"]]["DeltaNLL_BaselineMinusKernel"].sum()
                ),
                "MedianAlpha": float(oos[oos["PrimaryOOS"]]["Alpha"].median()),
                "NullAggregation": "single_frozen_null",
                "ClaimBoundary": p5c_v0.CLAIM_BOUNDARY,
            }
        )

    random_scores = []
    for source_id in random_ids:
        mat = _BASE_MATRIX_FROM_LONG(p5c_v0.NULLS, source_id, len(rows))
        _, oos = p5c_v0.score_all(rows, mat, source_id)
        random_scores.append(
            {
                "SourceKernelID": source_id,
                "PrimaryOOSDeltaNLL_BaselineMinusKernel": float(
                    oos[oos["PrimaryOOS"]]["DeltaNLL_BaselineMinusKernel"].sum()
                ),
                "MedianAlpha": float(oos[oos["PrimaryOOS"]]["Alpha"].median()),
            }
        )
    if not random_scores:
        raise RuntimeError("No frozen random-smooth PSD null kernels found.")
    random_df = pd.DataFrame(random_scores)
    strongest = random_df.sort_values(
        ["PrimaryOOSDeltaNLL_BaselineMinusKernel", "SourceKernelID"],
        ascending=[False, True],
    ).iloc[0]
    null_rows.append(
        {
            "AuditID": p5c_v0.AUDIT_ID,
            "ProtocolID": p5c_v0.PROTOCOL_ID,
            "KernelID": "K_RANDOM_SMOOTH_PSD",
            "SourceKernelID": strongest["SourceKernelID"],
            "PrimaryOOSDeltaNLL_BaselineMinusKernel": float(
                strongest["PrimaryOOSDeltaNLL_BaselineMinusKernel"]
            ),
            "MedianAlpha": float(strongest["MedianAlpha"]),
            "NullAggregation": "max_over_64_frozen_random_smooth_psd",
            "ClaimBoundary": p5c_v0.CLAIM_BOUNDARY,
        }
    )

    null_summary = pd.DataFrame(null_rows)
    gates, status = p5c_v0.gate_results(real_oos, null_summary)

    real_ins.to_csv(p5c_v0.OUT_IN_SAMPLE, index=False)
    real_oos.to_csv(p5c_v0.OUT_OOS, index=False)
    null_summary.to_csv(p5c_v0.OUT_NULLS, index=False)
    gates.to_csv(p5c_v0.OUT_GATES, index=False)

    primary = real_oos[real_oos["PrimaryOOS"]]
    summary = pd.DataFrame(
        [
            {
                "AuditID": p5c_v0.AUDIT_ID,
                "ProtocolID": p5c_v0.PROTOCOL_ID,
                "KernelID": p5c_v0.KERNEL_ID,
                "Rows": len(rows),
                "Families": int(rows["FamilyID"].nunique()),
                "ClockPositions": int(rows["ClockIndex"].nunique()),
                "InSampleDeltaNLL_BaselineMinusKernel": float(
                    real_ins["DeltaNLL_BaselineMinusKernel"].iloc[0]
                ),
                "PrimaryOOSDeltaNLL_BaselineMinusKernel": float(
                    primary["DeltaNLL_BaselineMinusKernel"].sum()
                ),
                "GatesPassed": int(gates["Passed"].sum()),
                "GatesTotal": int(len(gates)),
                "CurrentStatus": status,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": p5c_v0.CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(p5c_v0.OUT_SUMMARY, index=False)

    p5c_v0.OUT_DOC.write_text(
        "\n".join(
            [
                "# P5C Kernel Covariance Scorecard v3",
                "",
                f"Status: `{status}`",
                "",
                "This is the v3 PSD covariance-deformation scorecard. It is not a",
                "measurement validation claim.",
                "",
                "## Key Numbers",
                "",
                f"- rows: {len(rows)}",
                f"- families: {rows['FamilyID'].nunique()}",
                f"- clock positions: {rows['ClockIndex'].nunique()}",
                f"- in-sample Delta NLL baseline-kernel: {summary['InSampleDeltaNLL_BaselineMinusKernel'].iloc[0]}",
                f"- primary OOS Delta NLL baseline-kernel: {summary['PrimaryOOSDeltaNLL_BaselineMinusKernel'].iloc[0]}",
                f"- gates passed: {summary['GatesPassed'].iloc[0]}/{summary['GatesTotal'].iloc[0]}",
                "",
                "Positive Delta NLL means the kernel covariance model beat the diagonal",
                "baseline on the declared score.",
                "",
                "## Random-Smooth Null Policy",
                "",
                "The random-smooth PSD comparator is the strongest member of the 64 frozen",
                "random-smooth PSD null kernels.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    for path in [
        p5c_v0.OUT_IN_SAMPLE,
        p5c_v0.OUT_OOS,
        p5c_v0.OUT_NULLS,
        p5c_v0.OUT_GATES,
        p5c_v0.OUT_SUMMARY,
        p5c_v0.OUT_DOC,
    ]:
        print(f"wrote {path.relative_to(p5c_v0.ROOT)}")
    print(status)
    print(
        "random_smooth_psd_source="
        f"{strongest['SourceKernelID']} "
        f"delta={float(strongest['PrimaryOOSDeltaNLL_BaselineMinusKernel'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
