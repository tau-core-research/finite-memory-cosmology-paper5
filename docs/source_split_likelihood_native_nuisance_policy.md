# Source-Split Likelihood-Native Nuisance Policy

Status: policy added; baseline vector remains preflight until covariance and
coordinate promotion are complete.

This policy resolves the first promotion-task boundary:

```text
LNPROMO_1_NUISANCE_POLICY
```

## Problem

The current baseline prediction vector contains two source-split responses:

```text
RawSourceSplitResponse
CenteredControlSourceSplitResponse
```

The centered response subtracts a same-sample SN offset. That is useful as a
diagnostic control, but it must not silently become the primary K1 amplitude,
because same-sample centering can absorb part of the signal being tested.

## Policy

Primary K1 promotion must use:

```text
RawSourceSplitResponse
```

unless a public likelihood-native SN nuisance treatment is introduced before
K2/null scoring.

The centered response is allowed only as:

```text
nuisance_control
```

It may appear in sensitivity tables, but it must not set the primary K1
amplitude and must not be used to rescue K2 performance.

## Required Metadata For Promotion

Any promoted K1 export must include:

```text
NuisancePolicyID
PrimaryResponseColumn
ControlResponseColumn
SameSampleCenteringUsedForPrimaryK1
FittedInThisNote
SameDataAmplitudeFit
```

with:

```text
PrimaryResponseColumn = RawSourceSplitResponse
SameSampleCenteringUsedForPrimaryK1 = false
FittedInThisNote = false
SameDataAmplitudeFit = false
```

## Current Decision

The current baseline vector is not promoted yet because covariance and
coordinate promotion are still open. However, this policy resolves the core
nuisance ambiguity: same-sample centering is a control, not the primary K1
baseline.
