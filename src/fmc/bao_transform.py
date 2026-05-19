"""BAO residual transform helpers for public benchmark preflight."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fmc.coordinates import x_chi_normalized, x_index_native, x_z_normalized

C_KM_S = 299792.458

FIDUCIAL_AUDIT_BASELINE = {
    "baseline_id": "AUDIT_FLAT_LCDM_BAO_V0",
    "H0": 70.0,
    "omega_m": 0.3,
    "rd_mpc": 147.0,
}


def e_z(z, omega_m: float = 0.3) -> np.ndarray:
    """Dimensionless expansion rate for a flat audit LCDM baseline."""
    values = np.asarray(z, dtype=float)
    return np.sqrt(float(omega_m) * (1.0 + values) ** 3 + (1.0 - float(omega_m)))


def comoving_distance_mpc(z, h0: float = 70.0, omega_m: float = 0.3, samples: int = 1024) -> np.ndarray:
    """Numerical line-of-sight comoving distance in Mpc for the audit baseline."""
    values = np.asarray(z, dtype=float)
    distances = []
    for item in values:
        if item == 0.0:
            distances.append(0.0)
            continue
        grid = np.linspace(0.0, float(item), int(samples))
        integral = np.trapezoid(1.0 / e_z(grid, omega_m=omega_m), grid)
        distances.append((C_KM_S / float(h0)) * integral)
    return np.asarray(distances, dtype=float)


def bao_prediction(row: pd.Series, baseline: dict | None = None) -> float:
    """Predict one Cobaya-style BAO observable under the audit baseline."""
    params = baseline or FIDUCIAL_AUDIT_BASELINE
    z = float(row["z"])
    quantity = str(row["quantity"])
    h0 = float(params["H0"])
    omega_m = float(params["omega_m"])
    rd = float(params["rd_mpc"])

    dm = float(comoving_distance_mpc([z], h0=h0, omega_m=omega_m)[0])
    dh = C_KM_S / (h0 * float(e_z([z], omega_m=omega_m)[0]))
    dv = (z * dm * dm * dh) ** (1.0 / 3.0)

    if quantity == "DM_over_rs":
        return dm / rd
    if quantity == "DH_over_rs":
        return dh / rd
    if quantity == "DV_over_rs":
        return dv / rd
    raise ValueError(f"unsupported BAO quantity: {quantity}")


def bao_log_residual_transform(
    mean: pd.DataFrame,
    covariance: np.ndarray,
    product_id: str,
    baseline: dict | None = None,
) -> tuple[pd.DataFrame, np.ndarray]:
    """Return log(observed / audit_prediction) rows and propagated covariance."""
    if len(mean) != covariance.shape[0] or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("BAO mean/covariance dimensions do not match")

    params = baseline or FIDUCIAL_AUDIT_BASELINE
    df = mean.reset_index(drop=True).copy()
    predicted = np.array([bao_prediction(row, params) for _, row in df.iterrows()], dtype=float)
    observed = df["value"].to_numpy(float)
    residual = np.log(observed / predicted)

    jac = np.diag(1.0 / observed)
    residual_cov = jac @ np.asarray(covariance, dtype=float) @ jac
    sigma = np.sqrt(np.diag(residual_cov))
    coords = {
        "x_z_normalized": x_z_normalized(df["z"].to_numpy(float)),
        "x_chi_normalized": x_chi_normalized(df["z"].to_numpy(float)),
        "x_likelihood_native_index": x_index_native(len(df)),
    }

    rows = pd.DataFrame(
        {
            "TransformID": "T1_BAO_DISTANCE_RATIO_RESIDUAL",
            "ProductID": product_id,
            "RowID": np.arange(len(df), dtype=int),
            "Quantity": df["quantity"].astype(str),
            "z": df["z"].to_numpy(float),
            "ObservedValue": observed,
            "AuditPrediction": predicted,
            "LogResidual": residual,
            "SigmaDiag": sigma,
            "CovarianceIndex": np.arange(len(df), dtype=int),
            "x_z_normalized": coords["x_z_normalized"],
            "x_chi_normalized": coords["x_chi_normalized"],
            "x_likelihood_native_index": coords["x_likelihood_native_index"],
            "BaselineID": params["baseline_id"],
            "TransformStatus": "BAO_RESIDUAL_PREFLIGHT_NOT_MEASUREMENT_GATE",
            "ClaimBoundary": "preflight_only_no_measurement_validation",
        }
    )
    return rows, residual_cov
