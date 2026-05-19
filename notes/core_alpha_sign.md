# Core Alpha Sign Note

Status: tau-core sign orientation note, not a measurement result.

The source-split response is oriented as:

```text
SNStandardizedResidual = SNCenteredResidualMu / SNSigmaDiagProxy
SourceSplitResponse = SNStandardizedResidual - BAOStandardizedResidual
```

The SN residual is built from:

```text
RawResidualMu = ObservedMu - AuditPredictionMu
CenteredResidualMu = RawResidualMu - SameSampleOffsetMu
```

Therefore a positive SN residual means that the observed SN distance modulus is
larger than the audit baseline after the same-sample offset. In ordinary
distance-modulus language, this means the source appears optically farther or
dimmer relative to the baseline.

Tau-core reading:

```text
alpha < 1
-> weaker optical focusing along the light path
-> larger effective SN distance modulus
-> positive SN-side residual
-> positive contribution to SN - BAO when the optical branch dominates
```

Thus the tau-core sign convention for the optical Dyer-Roeder alpha control is:

```text
AS_DECLARED
response_i = (1 - alpha) * optical_shape_i
```

The inverted sign is not selected by tau-core reasoning. It may be kept only as
a diagnostic contrast, not as the physical optical-null orientation.
