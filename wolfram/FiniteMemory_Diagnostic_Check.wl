(* Independent Wolfram Language check for Paper 5.
   This is a second implementation audit of the finite-memory diagnostic
   identities and compact CSV gates. It is not a measurement-validation run. *)

ClearAll["Global`*"];

scriptDir = DirectoryName[$InputFileName];
root = ParentDirectory[scriptDir];
outDir = FileNameJoin[{root, "studies", "finite_memory_cosmology_paper5_v01", "wolfram_audit_logs"}];
If[! DirectoryQ[outDir], CreateDirectory[outDir, CreateIntermediateDirectories -> True]];

toString[x_] := ToString[x, InputForm];

readCsvAssociations[rel_] := Module[{path, raw, header},
  path = FileNameJoin[{root, rel}];
  If[! FileExistsQ[path], Print["Missing required CSV: ", rel]; Exit[2]];
  raw = Import[path, "CSV"];
  If[Length[raw] < 2, Print["Empty required CSV: ", rel]; Exit[2]];
  header = ToString /@ First[raw];
  AssociationThread[header, ToString /@ #] & /@ Rest[raw]
];

numericValue[s_] := Quiet@Check[ToExpression[s], Missing["NotNumeric"]];

auditRows = {};
appendAudit[id_, status_, value_, expected_] := (
  auditRows = Append[auditRows, {id, status, toString[value], toString[expected]}];
);
ok = "REPRODUCIBILITY_OK";
bad = "CHECK_FAILED";

(* Symbolic finite-memory identities. *)
W[x_, rho_] := 1 + rho*x^3;
tail = FullSimplify[Integrate[W[x, rho] - 1, {x, 0, 1}], Assumptions -> rho >= 0];
bound = FullSimplify[tail <= 1, Assumptions -> rho >= 0];

Wp[x_, rho_, p_] := 1 + rho*x^p;
tailP = FullSimplify[
  Integrate[Wp[x, rho, p] - 1, {x, 0, 1}],
  Assumptions -> {rho >= 0, p > -1}
];
boundP = FullSimplify[tailP <= 1, Assumptions -> {rho >= 0, p > -1}];

appendAudit["symbolic_operator", If[W[x, rho] === 1 + rho*x^3, ok, bad], W[x, rho], 1 + rho*x^3];
appendAudit["symbolic_tail_integral", If[tail === rho/4, ok, bad], tail, rho/4];
appendAudit["symbolic_passive_bound", If[bound === rho <= 4, ok, bad], bound, rho <= 4];
appendAudit["symbolic_power_tail", If[tailP === rho/(1 + p), ok, bad], tailP, rho/(1 + p)];
appendAudit["symbolic_power_bound", If[boundP === rho <= 1 + p, ok, bad], boundP, rho <= 1 + p];

(* Shape-selection and threshold-sensitivity CSV checks. *)
thresholdOutcomes = readCsvAssociations["evidence/threshold_kernel_outcomes.csv"];
baselineOutcome = SelectFirst[thresholdOutcomes, #["ThresholdSet"] == "baseline" &];
strictEndpointOutcome = SelectFirst[thresholdOutcomes, #["ThresholdSet"] == "strict_endpoint" &];
relaxedLowDepthOutcome = SelectFirst[thresholdOutcomes, #["ThresholdSet"] == "relaxed_low_depth" &];

appendAudit[
  "shape_selection_baseline_kernel",
  If[AssociationQ[baselineOutcome] && baselineOutcome["AdmissiblePowerKernels"] == "p=3", ok, bad],
  If[AssociationQ[baselineOutcome], baselineOutcome["AdmissiblePowerKernels"], Missing["Absent"]],
  "p=3"
];
appendAudit[
  "shape_selection_strict_endpoint_warning",
  If[AssociationQ[strictEndpointOutcome] && strictEndpointOutcome["AdmissiblePowerKernels"] == "none", ok, bad],
  If[AssociationQ[strictEndpointOutcome], strictEndpointOutcome["AdmissiblePowerKernels"], Missing["Absent"]],
  "none"
];
appendAudit[
  "threshold_sensitivity_relaxed_low_depth_broadens",
  If[AssociationQ[relaxedLowDepthOutcome] && StringContainsQ[relaxedLowDepthOutcome["AdmissiblePowerKernels"], "p=2"], ok, bad],
  If[AssociationQ[relaxedLowDepthOutcome], relaxedLowDepthOutcome["AdmissiblePowerKernels"], Missing["Absent"]],
  "contains p=2"
];

thresholdRows = readCsvAssociations["evidence/threshold_sensitivity.csv"];
appendAudit[
  "threshold_sensitivity_row_count",
  If[Length[thresholdRows] >= 5, ok, bad],
  Length[thresholdRows],
  ">=5"
];

(* SN+BAO point-level gate checks. *)
pointRows = readCsvAssociations["evidence/diagnostic_point_audit.csv"];
signStableRows = Select[pointRows, #["sign_stable"] == "True" &];
signUnstableRows = Select[pointRows, #["sign_stable"] == "False" &];
allowedDecisions = {"NONVIOLATING_SIGN_STABLE", "COMPATIBLE_SIGN_UNSTABLE"};
allDecisionsAllowed = AllTrue[pointRows, MemberQ[allowedDecisions, #["decision"]] &];

appendAudit["snbao_point_gate_row_count", If[Length[pointRows] == 9, ok, bad], Length[pointRows], 9];
appendAudit["snbao_sign_stable_count", If[Length[signStableRows] == 5, ok, bad], Length[signStableRows], 5];
appendAudit["snbao_sign_unstable_count", If[Length[signUnstableRows] == 4, ok, bad], Length[signUnstableRows], 4];
appendAudit["snbao_decision_set", If[allDecisionsAllowed, ok, bad], DeleteDuplicates[Lookup[pointRows, "decision"]], allowedDecisions];

gateRows = readCsvAssociations["evidence/gate_results_current.csv"];
k2Row = SelectFirst[gateRows, #["Model"] == "K2_LOCKED_CURRENT" &];
appendAudit[
  "snbao_locked_k2_rho",
  If[AssociationQ[k2Row] && numericValue[k2Row["Rho"]] == 4., ok, bad],
  If[AssociationQ[k2Row], k2Row["Rho"], Missing["Absent"]],
  4
];
appendAudit[
  "snbao_locked_k2_status",
  If[AssociationQ[k2Row] && k2Row["Status"] == "NON_VIOLATING_DIAGNOSTIC", ok, bad],
  If[AssociationQ[k2Row], k2Row["Status"], Missing["Absent"]],
  "NON_VIOLATING_DIAGNOSTIC"
];

resultRows = readCsvAssociations["evidence/result_summary.csv"];
r3 = SelectFirst[resultRows, #["ResultID"] == "R3_SN_SIGN_STABLE" &];
r4 = SelectFirst[resultRows, #["ResultID"] == "R4_SN_UNSTABLE" &];
appendAudit[
  "result_summary_sign_stable_fraction",
  If[AssociationQ[r3] && numericValue[r3["Value"]] == 1., ok, bad],
  If[AssociationQ[r3], r3["Value"], Missing["Absent"]],
  1
];
appendAudit[
  "result_summary_sign_unstable_fraction",
  If[AssociationQ[r4] && numericValue[r4["Value"]] == 1., ok, bad],
  If[AssociationQ[r4], r4["Value"], Missing["Absent"]],
  1
];

overall = If[AllTrue[auditRows[[All, 2]], # == ok &], "REPRODUCIBILITY_OK", "CHECK_FAILED"];
auditTable = Prepend[auditRows, {"CheckID", "Status", "Value", "Expected"}];
Export[FileNameJoin[{outDir, "finite_memory_diagnostic_check_wolfram.csv"}], auditTable, "CSV"];

summary = {
  "FiniteMemory_Diagnostic_Check.wl",
  "ReproducibilityStatus=" <> overall,
  "SymbolicTail=" <> toString[tail],
  "PassiveBound=" <> toString[bound],
  "PowerTail=" <> toString[tailP],
  "PowerBound=" <> toString[boundP],
  "ShapeBaseline=" <> If[AssociationQ[baselineOutcome], baselineOutcome["AdmissiblePowerKernels"], "missing"],
  "SNBAOPointRows=" <> ToString[Length[pointRows]],
  "SNBAOSignStableRows=" <> ToString[Length[signStableRows]],
  "SNBAOSignUnstableRows=" <> ToString[Length[signUnstableRows]],
  "OutputCSV=studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.csv"
};
Export[FileNameJoin[{outDir, "finite_memory_diagnostic_check_wolfram.log"}], StringRiffle[summary, "\n"], "Text"];

Print /@ summary;
If[overall =!= "REPRODUCIBILITY_OK", Exit[1]];
