# Physical Null Proxy Templates

Status: templates available; scoring requires the separate amplitude policy.

The physical null hierarchy requires backreaction-only and Dyer-Roeder/optical
comparators on the same source-split vector. This artifact creates deterministic
unit-norm proxy shapes for those comparators without fitting amplitudes and
without adding them to any scorecard.

Outputs:

- `evidence/physical_null_proxy_templates.csv`;
- `evidence/physical_null_proxy_template_readiness.csv`.

## Templates

Two templates are exported:

```text
BACKREACTION_BROADBAND_UNIT_NORM_V1
ShapeDefinition: unit_norm(centered[x^2*(1-0.5*x)])
```

```text
DYER_ROEDER_OPTICAL_UNIT_NORM_V1
ShapeDefinition: unit_norm(centered[x^2])
```

Both are defined on the same coordinate-native source-split rows.

## Boundary

The template artifact by itself is not a scoring control:

```text
AmplitudePolicyDeclared: false
ScoringAllowed: false
MeasurementValidationAllowed: false
```

The amplitude policy is declared separately in
`docs/physical_null_amplitude_policy.md`. With that policy attached, the
templates may enter a future preflight scorecard only as sanity / sensitivity
controls, not as measurement-calibrated physical explanations. A free
least-squares or AIC-selected amplitude chosen after inspecting the benchmark
remains forbidden.
