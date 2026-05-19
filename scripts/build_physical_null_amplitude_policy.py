#!/usr/bin/env python3
"""Register amplitude policies for physical-null proxy templates.

This is a policy artifact only. It does not score the physical nulls.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE_READINESS = ROOT / "evidence" / "physical_null_proxy_template_readiness.csv"
OUT_POLICY = ROOT / "evidence" / "physical_null_amplitude_policy.csv"
OUT_READINESS = ROOT / "evidence" / "physical_null_amplitude_policy_readiness.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    templates = pd.read_csv(TEMPLATE_READINESS).iloc[0]
    template_available = bool_text(templates["BackreactionTemplateAvailable"]) and bool_text(
        templates["DyerRoederOpticalTemplateAvailable"]
    )

    policy_rows = [
        {
            "PolicyID": "PHYSNULL_AMP_UNIT_ONLY_V1",
            "PolicyRole": "primary_sanity_preflight",
            "AppliesTo": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "AmplitudeRule": "A=1 on unit-norm template",
            "AmplitudeFitToTargetAllowed": False,
            "GridSelectionAllowed": False,
            "CanSupportScoringPreflight": True,
            "CanSupportMeasurementValidation": False,
            "RequiredReporting": "report as unit-shape sanity comparator only",
            "BlockingIssue": "unit amplitude is not a physical calibration",
            "ClaimBoundary": "physical_null_amplitude_policy_no_measurement_validation",
        },
        {
            "PolicyID": "PHYSNULL_AMP_BOUNDED_GRID_V1",
            "PolicyRole": "secondary_sensitivity_preflight",
            "AppliesTo": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "AmplitudeRule": "A in {-1.0,-0.5,0.0,0.5,1.0}; report all grid outcomes",
            "AmplitudeFitToTargetAllowed": False,
            "GridSelectionAllowed": False,
            "CanSupportScoringPreflight": True,
            "CanSupportMeasurementValidation": False,
            "RequiredReporting": "all amplitudes must be reported; no best-amplitude promotion",
            "BlockingIssue": "bounded grid is sensitivity only",
            "ClaimBoundary": "physical_null_amplitude_policy_no_measurement_validation",
        },
        {
            "PolicyID": "PHYSNULL_AMP_FORBIDDEN_FREE_FIT_V1",
            "PolicyRole": "forbidden",
            "AppliesTo": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "AmplitudeRule": "least_squares_or_AIC_selected_amplitude_after_score_inspection",
            "AmplitudeFitToTargetAllowed": False,
            "GridSelectionAllowed": False,
            "CanSupportScoringPreflight": False,
            "CanSupportMeasurementValidation": False,
            "RequiredReporting": "invalid route",
            "BlockingIssue": "post_hoc_physical_null_amplitude_rescue_forbidden",
            "ClaimBoundary": "physical_null_amplitude_policy_no_measurement_validation",
        },
    ]
    policy = pd.DataFrame(policy_rows)
    policy.to_csv(OUT_POLICY, index=False)

    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PHYSICAL_NULL_AMPLITUDE_POLICY_READINESS",
                "TemplatesAvailable": template_available,
                "PoliciesRegistered": len(policy),
                "PrimaryPolicyID": "PHYSNULL_AMP_UNIT_ONLY_V1",
                "SecondaryPolicyID": "PHYSNULL_AMP_BOUNDED_GRID_V1",
                "ForbiddenPolicyID": "PHYSNULL_AMP_FORBIDDEN_FREE_FIT_V1",
                "AmplitudePolicyDeclared": True,
                "ScoringPreflightAllowed": template_available,
                "MeasurementValidationAllowed": False,
                "PrimaryBlockingIssue": "physical_null_amplitudes_not_physically_calibrated",
                "NextAction": "run physical null preflight scorecard only as sanity/sensitivity comparator, not measurement validation",
                "Interpretation": "physical null amplitudes are declared for preflight without allowing free target fits",
                "ClaimBoundary": "physical_null_amplitude_policy_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_POLICY}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
