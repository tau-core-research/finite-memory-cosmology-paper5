#!/usr/bin/env python3
"""Build calibration requirements for physical-null amplitudes.

This artifact does not calibrate physical nulls. It declares what would be
needed before backreaction-only or Dyer-Roeder/optical templates could become
measurement-grade null comparators.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

OUT = EVIDENCE / "physical_null_calibration_requirements.csv"
OUT_READINESS = EVIDENCE / "physical_null_calibration_readiness.csv"


def main() -> None:
    rows = [
        {
            "CalibrationID": "BACKREACTION_PUBLIC_RECONSTRUCTION_AMPLITUDE",
            "NullID": "BACKREACTION_ONLY",
            "RequiredInput": "public backreaction reconstruction or envelope on the same source-split coordinate vector",
            "AllowedAmplitudeSource": "amplitude derived before K2 score inspection from public backreaction observable or simulation prior",
            "CoordinateNativeRequired": True,
            "CovarianceRequired": True,
            "SameDataFitAllowed": False,
            "PostHocSelectionAllowed": False,
            "CurrentStatus": "missing",
            "BlocksMeasurementValidation": True,
            "NextAction": "identify public backreaction reconstruction product or define an independent simulation-prior amplitude before rerun",
            "ClaimBoundary": "physical_null_calibration_requirements_no_measurement_validation",
        },
        {
            "CalibrationID": "DYER_ROEDER_PUBLIC_OPTICAL_CLUMPINESS_AMPLITUDE",
            "NullID": "DYER_ROEDER_OPTICAL",
            "RequiredInput": "public optical clumpiness or Dyer-Roeder alpha(z) constraint mapped to the same source-split coordinate vector",
            "AllowedAmplitudeSource": "amplitude derived before K2 score inspection from public optical propagation/clumpiness constraint",
            "CoordinateNativeRequired": True,
            "CovarianceRequired": True,
            "SameDataFitAllowed": False,
            "PostHocSelectionAllowed": False,
            "CurrentStatus": "missing",
            "BlocksMeasurementValidation": True,
            "NextAction": "identify public alpha(z)/clumpiness constraint or lensing/opacity proxy with covariance before rerun",
            "ClaimBoundary": "physical_null_calibration_requirements_no_measurement_validation",
        },
        {
            "CalibrationID": "FORBIDDEN_SAME_SCORECARD_AMPLITUDE_FIT",
            "NullID": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "RequiredInput": "same scorecard target residuals",
            "AllowedAmplitudeSource": "forbidden",
            "CoordinateNativeRequired": False,
            "CovarianceRequired": False,
            "SameDataFitAllowed": False,
            "PostHocSelectionAllowed": False,
            "CurrentStatus": "forbidden",
            "BlocksMeasurementValidation": True,
            "NextAction": "do not use least-squares, AIC, BIC, or row-wise residual inspection to choose physical-null amplitude",
            "ClaimBoundary": "physical_null_calibration_requirements_no_measurement_validation",
        },
    ]
    requirements = pd.DataFrame(rows)
    requirements.to_csv(OUT, index=False)

    allowed = requirements[requirements["CurrentStatus"].ne("forbidden")]
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PHYSICAL_NULL_CALIBRATION_READINESS",
                "CalibrationRoutesRegistered": int(len(requirements)),
                "AllowedCalibrationRoutes": int(len(allowed)),
                "AllowedRoutesAvailable": int(allowed["CurrentStatus"].eq("available").sum()),
                "ForbiddenRoutesRegistered": int(requirements["CurrentStatus"].eq("forbidden").sum()),
                "BackreactionCalibrationAvailable": bool(
                    requirements[
                        requirements["CalibrationID"].eq("BACKREACTION_PUBLIC_RECONSTRUCTION_AMPLITUDE")
                    ]["CurrentStatus"].eq("available").any()
                ),
                "DyerRoederCalibrationAvailable": bool(
                    requirements[
                        requirements["CalibrationID"].eq("DYER_ROEDER_PUBLIC_OPTICAL_CLUMPINESS_AMPLITUDE")
                    ]["CurrentStatus"].eq("available").any()
                ),
                "PhysicalNullMeasurementReady": False,
                "PrimaryBlockingIssue": "physical_null_calibration_inputs_missing",
                "NextAction": "obtain independent public backreaction and optical-propagation amplitude sources before measurement-level physical-null comparison",
                "Interpretation": "physical null preflight is runnable, but physical-null measurement comparison is blocked by missing independent amplitude calibration",
                "ClaimBoundary": "physical_null_calibration_requirements_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
