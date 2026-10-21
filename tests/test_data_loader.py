from analysis.data_loader import DataLoader, audit_compatibility
from src.experiment_schema import CSV_COLUMNS


def test_compatibility_groups_separate_qiskit_versions():
    primary = DataLoader("results/connectivity_experiments.csv")
    other = DataLoader("results/optimization_experiments.csv")

    report = audit_compatibility({"connectivity": primary, "optimization": other})

    assert len(report["compatible_groups"]) == 2
    assert any("Different Qiskit versions" in note for note in report["notes"])


def test_data_loader_rejects_extra_or_reordered_columns(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text(",".join(CSV_COLUMNS + ["unexpected"]) + "\n", encoding="utf-8")
    try:
        DataLoader(source)
    except ValueError as exc:
        assert "exact order" in str(exc)
    else:
        raise AssertionError("expected strict schema validation to fail")
