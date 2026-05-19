"""Shared benchmark helpers for measurement-gate MVP scripts."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fmc.coordinates import x_chi_normalized, x_index_native, x_optical_depth_like, x_z_normalized
from fmc.nulls import coordinate_remap_control, null_no_memory, polynomial_fit, sign_randomized_control
from fmc.operators import k2_from_k1


def bool_series(values: pd.Series) -> np.ndarray:
    """Parse permissive boolean strings from CSV."""
    return values.astype(str).str.lower().isin(["true", "1", "yes", "y"]).to_numpy()


def mapping_set(z: np.ndarray, packet_x: np.ndarray) -> dict[str, np.ndarray]:
    """Return predeclared audit mappings."""
    return {
        "z_normalized_current_packet": packet_x,
        "z_normalized_recomputed": x_z_normalized(z),
        "chi_normalized_flat_lcdm_audit": x_chi_normalized(z),
        "optical_depth_like_uniform": x_optical_depth_like(z),
        "likelihood_native_index": x_index_native(len(z)),
    }


def model_predictions(x_values, k1, y) -> list[dict[str, object]]:
    """Return the standard model set for null comparison scripts."""
    return [
        {
            "Model": "K2_LOCKED_RHO4",
            "Prediction": k2_from_k1(x_values, k1, rho=4.0),
            "ParameterCount": 0,
            "rho": 4.0,
            "Notes": "fixed_rho4_locked_prediction",
        },
        {
            "Model": "K1_NO_MEMORY",
            "Prediction": null_no_memory(k1),
            "ParameterCount": 0,
            "rho": None,
            "Notes": "frozen_k1_no_memory_control",
        },
        {
            "Model": "POLY_DEG2",
            "Prediction": polynomial_fit(x_values, y, degree=2),
            "ParameterCount": 3,
            "rho": None,
            "Notes": "fixed_degree_polynomial_null",
        },
        {
            "Model": "POLY_DEG3",
            "Prediction": polynomial_fit(x_values, y, degree=3),
            "ParameterCount": 4,
            "rho": None,
            "Notes": "fixed_degree_polynomial_null",
        },
        {
            "Model": "SIGN_RANDOMIZED_CONTROL",
            "Prediction": sign_randomized_control(y, seed=0),
            "ParameterCount": 0,
            "rho": None,
            "Notes": "fixed_seed_sign_control",
        },
        {
            "Model": "COORDINATE_REMAP_CONTROL",
            "Prediction": coordinate_remap_control(x_values, k1, rho=4.0, alpha=1.2),
            "ParameterCount": 1,
            "rho": 4.0,
            "Notes": "fixed_alpha_1p2_coordinate_remap_control",
        },
    ]


def depth_masks(x_values) -> dict[str, np.ndarray]:
    """Return all/sign/depth subset masks for a diagnostic grid."""
    x = np.asarray(x_values, dtype=float)
    return {
        "low_depth": x <= (1.0 / 3.0),
        "mid_depth": (x > (1.0 / 3.0)) & (x <= (2.0 / 3.0)),
        "high_depth": x > (2.0 / 3.0),
    }
