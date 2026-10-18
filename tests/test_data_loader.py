from dataclasses import replace

from analysis.data_loader import DataLoader, audit_compatibility


def test_compatibility_groups_separate_python_versions():
    primary = DataLoader("results/qtrace_results.csv")
    other_python = DataLoader("results/qtrace_results.csv")
    other_python.records = [
        replace(record, python_version="3.13.0")
        for record in other_python.records
    ]

    report = audit_compatibility({"primary": primary, "other-python": other_python})

    assert len(report["compatible_groups"]) == 2
    assert any("Different Python versions" in note for note in report["notes"])


def test_compatibility_handles_missing_python_metadata():
    loader = DataLoader("results/qtrace_results.csv")
    loader.records = [replace(record, python_version=None) for record in loader.records]

    report = audit_compatibility({"missing-python": loader})

    assert len(report["compatible_groups"]) == 1
    assert report["datasets"]["missing-python"]["python_versions"] == ["unknown"]
