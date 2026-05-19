# Source-Native Backreaction Data Request Packet

Purpose: replace the provisional BAO-only backreaction bridge with the source-native reconstruction used for the published `Omega_R + 3 Omega_Q` constraints.

Please provide, for each published backreaction family:

## QR_CRITERIA_1

- Addendum figure: `QR_criteria1.pdf`
- Upstream input route: criteria set 1 H_D,H_D_prime plus reconstructed D,D_prime,D_double_prime

Required machine-readable objects:
- `RECONSTRUCTION_VECTOR_MEDIAN`: z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_BOOTSTRAP_SAMPLES`: sample_id,z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_COVARIANCE`: row-wise covariance for D,D_prime,D_double_prime,H_D,H_D_prime
- `SELECTION_METADATA`: criteria_set,data_combination,algorithm,expression_id,selection_rule
- `GRID_AND_UNITS_METADATA`: redshift_grid,D_definition,H_D_units,normalization

## QR_CRITERIA_2

- Addendum figure: `QR_criteria2.pdf`
- Upstream input route: criteria set 2 H_D,H_D_prime plus reconstructed D,D_prime,D_double_prime

Required machine-readable objects:
- `RECONSTRUCTION_VECTOR_MEDIAN`: z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_BOOTSTRAP_SAMPLES`: sample_id,z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_COVARIANCE`: row-wise covariance for D,D_prime,D_double_prime,H_D,H_D_prime
- `SELECTION_METADATA`: criteria_set,data_combination,algorithm,expression_id,selection_rule
- `GRID_AND_UNITS_METADATA`: redshift_grid,D_definition,H_D_units,normalization

## QR_CRITERIA_3

- Addendum figure: `QR_criteria3.pdf`
- Upstream input route: criteria set 3 H_D,H_D_prime plus reconstructed D,D_prime,D_double_prime

Required machine-readable objects:
- `RECONSTRUCTION_VECTOR_MEDIAN`: z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_BOOTSTRAP_SAMPLES`: sample_id,z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_COVARIANCE`: row-wise covariance for D,D_prime,D_double_prime,H_D,H_D_prime
- `SELECTION_METADATA`: criteria_set,data_combination,algorithm,expression_id,selection_rule
- `GRID_AND_UNITS_METADATA`: redshift_grid,D_definition,H_D_units,normalization

## QR_DESI

- Addendum figure: `QR_DESI.pdf`
- Upstream input route: DESI-dominated symbolic-regression family

Required machine-readable objects:
- `RECONSTRUCTION_VECTOR_MEDIAN`: z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_BOOTSTRAP_SAMPLES`: sample_id,z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_COVARIANCE`: row-wise covariance for D,D_prime,D_double_prime,H_D,H_D_prime
- `SELECTION_METADATA`: criteria_set,data_combination,algorithm,expression_id,selection_rule
- `GRID_AND_UNITS_METADATA`: redshift_grid,D_definition,H_D_units,normalization

## QR_EBOSS

- Addendum figure: `QR_eBOSS.pdf`
- Upstream input route: eBOSS/BOSS-dominated symbolic-regression family

Required machine-readable objects:
- `RECONSTRUCTION_VECTOR_MEDIAN`: z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_BOOTSTRAP_SAMPLES`: sample_id,z,D,D_prime,D_double_prime,H_D,H_D_prime
- `RECONSTRUCTION_COVARIANCE`: row-wise covariance for D,D_prime,D_double_prime,H_D,H_D_prime
- `SELECTION_METADATA`: criteria_set,data_combination,algorithm,expression_id,selection_rule
- `GRID_AND_UNITS_METADATA`: redshift_grid,D_definition,H_D_units,normalization

Claim boundary: these files would be used for a source-native benchmark only. They would not by themselves imply measurement validation or discovery.
