# Sign-Family Export Plan

Status: public branch sign-family preflight exported; no full public
reconstruction-family export is authorized for K2 scoring.

The current method note already uses sign-stability logic, but the available
sign families come from the distilled diagnostic packet. A measurement gate
requires the same idea to be exported from public source-split reconstruction
families.

## Registry

The registry is:

```text
evidence/sign_family_export_registry.csv
```

The readiness output is:

```text
evidence/sign_family_export_readiness.csv
```

Run:

```text
python3 scripts/check_sign_family_export.py
```

## Current Candidates

- `SF_CURRENT_DISTILLED_PACKET`: available as method-note template only.
- `SF_STANDARDIZED_SOURCE_SPLIT_PREFLIGHT`: available as branch-sign warning
  audit only.
- `SF_PUBLIC_SN_RECONSTRUCTION_FAMILIES`: planned.
- `SF_PUBLIC_BAO_RECONSTRUCTION_FAMILIES`: planned.
- `SF_PUBLIC_SOURCE_SPLIT_FAMILIES`: available as coordinate-native public
  branch-sign preflight.
- `SF_LIKELIHOOD_NATIVE_FAMILIES`: future likelihood-native target.

## Decision

No sign-family export is currently allowed for K2 scoring.

The exported preflight is:

```text
SF_PUBLIC_SOURCE_SPLIT_FAMILIES
```

It defines public SN and BAO standardized branch signs on the coordinate-native
source-split target rows. This is not yet a full public reconstruction-family
export.

The scoring-grade upgrade must define:

- which public reconstruction families are compared;
- how signs are computed in the source-split target space;
- what counts as sign-stable;
- how sign-unstable rows are retained as warnings rather than hidden support
  or hidden rejection.

The upgrade contract is:

```text
evidence/source_split_reconstruction_family_upgrade_contract.csv
evidence/source_split_reconstruction_family_upgrade_summary.csv
```

It records that row alignment and warning policy are already available, while
public reconstruction-family responses and the family-level sign-stability rule
remain blocking requirements.

## Family Sign-Rule Preview

The non-scoring preview is:

```text
python3 scripts/build_source_split_family_sign_rule_preview.py
```

It writes:

```text
evidence/source_split_family_sign_rule_preview.csv
evidence/source_split_family_sign_rule_preview_summary.csv
```

Preview rule:

```text
stable if all nonzero public reconstruction-family signs agree
```

The current preview has three stable rows and five warning rows. It is not a
scoring rule because the real reconstruction-family candidate export is still
missing.

## Promotion Readiness

The promotion-readiness check is:

```text
python3 scripts/check_source_split_sign_rule_promotion.py
```

It writes:

```text
evidence/source_split_sign_rule_promotion_readiness.csv
```

The current result blocks promotion because the real candidate export is still
missing. The preview rule is retained as warning-policy documentation only.
