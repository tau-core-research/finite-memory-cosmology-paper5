#!/usr/bin/env python3
"""Define a target-blind domain-metric update rule after Q-clean embedding failure."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
RULE_ID = "P_TAUCOV_DOMAIN_METRIC_UPDATE_RULE_v1"
STATUS = "P_TAUCOV_DOMAIN_METRIC_UPDATE_RULE_DEFINED_NO_METRIC_NO_SCORING"
CLAIM = "domain_metric_update_rule_no_metric_no_scoring"

OUT_RULES = EVIDENCE / "p_taucov_domain_metric_update_rule.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_domain_metric_update_rule_summary.csv"
OUT_DOC = DOCS / "p_taucov_domain_metric_update_rule.md"


RULES = [
    (
        "DMR-R1_PARENT_METRIC_ORIGIN",
        "Any metric update must be derived from declared parent-domain structure: coordinate provenance, source covariance declared before target residuals, self-adjoint-domain pairing, or symmetry/constraint algebra.",
        "required",
    ),
    (
        "DMR-R2_NO_TARGET_OUTCOME_INPUT",
        "The metric may not use held-out residuals, OOS DeltaNLL, fitted alpha behavior, winning nulls, or post-score family/context localization.",
        "forbidden",
    ),
    (
        "DMR-R3_BRANCH_SUPPORT_GATE",
        "Before scoring, active branch coordinates must have non-negligible support in the common clean subspace under the updated metric/embedding.",
        ">=0.20",
    ),
    (
        "DMR-R4_METRIC_POSITIVE_AND_BOUNDED",
        "The domain metric must be symmetric positive semidefinite or explicitly indefinite with a declared Krein/signature convention; condition number policy must be frozen.",
        "required",
    ),
    (
        "DMR-R5_NO_QCLEAN_AS_SOURCE",
        "Q_clean may audit the metric-induced embedding but must not be used as the definition of the metric source.",
        "forbidden_shortcut",
    ),
    (
        "DMR-R6_NULL_GAUGE_COMPATIBILITY",
        "The updated metric must preserve the frozen null/gauge/forbidden exclusions or explicitly declare a new target-blind reference-domain packet.",
        "required",
    ),
    (
        "DMR-R7_COMPARATOR_FREEZE_REQUIRED",
        "Any metric-induced candidate must face morphology-null, projection-null, shuffled-support, generic smooth, and diagonal comparators frozen before scoring.",
        "required",
    ),
]


def main() -> int:
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "RuleID": RULE_ID,
                "RequirementID": req_id,
                "Definition": definition,
                "Policy": policy,
                "ConcreteMetricDefined": False,
                "MetricEvaluationAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for req_id, definition, policy in RULES
        ]
    ).to_csv(OUT_RULES, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "RuleID": RULE_ID,
                "Status": STATUS,
                "Requirements": len(RULES),
                "ConcreteMetricDefined": False,
                "MetricEvaluationAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "NextGate": "derive_or_freeze_target_blind_domain_metric_then_rerun_embedding_qclean_support_audit",
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Domain-Metric Update Rule",
                "",
                f"Rule ID: `{RULE_ID}`",
                "",
                f"Status: `{STATUS}`",
                "",
                "## Motivation",
                "",
                "The embedding/Q-clean audit showed that the current parent-to-score",
                "embedding places the active branch coordinates almost entirely outside",
                "the frozen common clean subspace. This blocks parent-domain curvature",
                "source construction before any empirical score is inspected.",
                "",
                "The remedy cannot be an arbitrary metric chosen to make the support",
                "large. The metric update must be a declared parent-domain object with",
                "target-blind provenance.",
                "",
                "## Rule Table",
                "",
                "| Requirement | Policy | Definition |",
                "|---|---:|---|",
                *[
                    f"| `{req_id}` | `{policy}` | {definition} |"
                    for req_id, definition, policy in RULES
                ],
                "",
                "## Forbidden Shortcut",
                "",
                "The following move is not allowed:",
                "",
                "```text",
                "choose G_domain so that Q_clean E(G_domain) branch is large",
                "```",
                "",
                "unless `G_domain` has an independent parent-domain derivation or a",
                "target-blind provenance source that was declared before scoring.",
                "",
                "## Next Gate",
                "",
                "A future artifact may define a concrete `G_domain` or revised embedding",
                "only if it also declares:",
                "",
                "- parent-domain source of the metric;",
                "- null/gauge compatibility;",
                "- positivity or signature convention;",
                "- condition-number policy;",
                "- target-blind support audit command;",
                "- forbidden inputs certificate.",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> A target-blind rule now constrains how a parent-domain metric or embedding may be revised after the Q-clean support failure.",
                "",
                "Forbidden statement:",
                "",
                "> This rule defines a metric, constructs a Tau signal, or authorizes empirical scoring.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
