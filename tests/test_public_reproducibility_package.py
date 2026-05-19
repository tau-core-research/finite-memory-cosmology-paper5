from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]


def test_submission_packet_exists():
    required = [
        "README.md",
        "DATA_NOTICE.md",
        "CITATION.cff",
        "LICENSE",
        "paper5_submission_source/main.tex",
        "paper5_submission_source/main.pdf",
        "draft.md",
        "make_pdf.py",
        "src/fmc/likelihood.py",
        "scripts/run_gate_current_packet.py",
        "scripts/build_finite_memory_preflight_packet.py",
        "wolfram/README.md",
        "wolfram/FiniteMemory_Diagnostic_Check.wl",
        "studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.csv",
        "studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.log",
    ]
    missing = [rel for rel in required if not (ROOT / rel).exists()]
    assert not missing


def test_key_preflight_summaries_preserve_claim_boundary():
    required = [
        "evidence/finite_memory_preflight_summary.csv",
        "evidence/registered_protocol_guided_dominance_summary.csv",
        "evidence/source_native_reproduction_family_dominance_summary.csv",
    ]
    for rel in required:
        path = ROOT / rel
        assert path.exists(), rel
        rows = list(csv.DictReader(path.open()))
        assert rows, rel
        assert rows[0].get("MeasurementValidationAllowed") == "False"


def test_readme_avoids_forbidden_claims():
    forbidden = [
        "Tau Core" + " proven",
        "detected" + " finite memory",
    ]
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in forbidden:
        assert phrase not in text


def test_wolfram_audit_is_second_implementation_pass():
    path = ROOT / "studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.csv"
    rows = list(csv.DictReader(path.open()))
    assert rows
    assert all(row["Status"] == "REPRODUCIBILITY_OK" for row in rows)
    check_ids = {row["CheckID"] for row in rows}
    required = {
        "symbolic_operator",
        "symbolic_tail_integral",
        "symbolic_passive_bound",
        "symbolic_power_bound",
        "shape_selection_baseline_kernel",
        "threshold_sensitivity_row_count",
        "snbao_point_gate_row_count",
        "snbao_locked_k2_status",
    }
    assert required <= check_ids


def test_submission_zip_contains_wolfram_audit():
    import zipfile

    zip_path = ROOT / "arxiv_submission_source.zip"
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    required = {
        "wolfram/README.md",
        "wolfram/FiniteMemory_Diagnostic_Check.wl",
        "studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.csv",
        "studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.log",
    }
    assert required <= names
