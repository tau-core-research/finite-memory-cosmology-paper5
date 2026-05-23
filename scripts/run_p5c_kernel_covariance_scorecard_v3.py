#!/usr/bin/env python3
"""Run the P5C covariance/operator-kernel scorecard for kernel v3.

This wrapper preserves the v0-v2 covariance scorecard family while switching
the v3 primary artifact to the frozen PSD covariance-deformation projection.
It should be run only after the v3 final scoring authorization validator passes.
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
    "K_RANDOM_SMOOTH_PSD": "K_RANDOM_SMOOTH_PSD_000",
    "K_IDENTITY_DIAGONAL": "K_IDENTITY_DIAGONAL_PSD",
}


def matrix_from_long_v3(path: Path, kernel_id: str, n: int):
    return _BASE_MATRIX_FROM_LONG(path, _NULL_ID_MAP.get(kernel_id, kernel_id), n)


p5c_v0.matrix_from_long = matrix_from_long_v3


if __name__ == "__main__":
    raise SystemExit(p5c_v0.main())
