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
    ]
    missing = [rel for rel in required if not (ROOT / rel).exists()]
    assert not missing


def test_key_preflight_summaries_preserve_claim_boundary():
    required = [
        "evidence/finite_memory_preflight_summary.csv",
        "evidence/author_protocol_guided_dominance_summary.csv",
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
