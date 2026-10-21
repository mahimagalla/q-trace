import csv

import pytest

from src.experiment_schema import CSV_COLUMNS
from src.integrated_analysis import analyze
from src.validate_qaoa import validate_classical_max_cut


def _dataset(path, version):
    rows = []
    baseline = dict.fromkeys(CSV_COLUMNS, "")
    baseline.update({
        "experiment_id": "EXP-BASELINE", "circuit_name": "QAOA_MaxCut_Cycle4_p1",
        "graph_edges": "0-1;1-2;2-3;3-0", "num_qubits": 4, "qaoa_p": 1,
        "parameter_values": "gamma=0.5,beta=0.25", "topology": "baseline",
        "initial_layout": "0-0;1-1;2-2;3-3", "basis_gates": "['u', 'cx']",
        "seed_transpiler": 2026, "qiskit_version": version, "total_ops": 16,
        "measurement_count": 4, "gate_count_1q": 8, "gate_count_2q": 4,
        "circuit_depth": 6, "explicit_swap_count": 0, "input_swap_count": 0,
    })
    rows.append(baseline)
    for topology in ("linear", "fully_connected"):
        for level in range(4):
            twoq = (14 if level < 2 else 12) if topology == "linear" else 8
            depth = 18 if topology == "linear" else 14
            for trial in range(1, 6):
                row = dict.fromkeys(CSV_COLUMNS, "")
                row.update({
                    "experiment_id": f"{topology}-{level}",
                    "circuit_name": "QAOA_MaxCut_Cycle4_p1",
                    "graph_edges": "0-1;1-2;2-3;3-0", "num_qubits": 4,
                    "qaoa_p": 1, "parameter_values": "gamma=0.5,beta=0.25",
                    "optimization_level": level, "topology": topology,
                    "initial_layout": "0-0;1-1;2-2;3-3",
                    "routing_method": "Qiskit preset default",
                    "basis_gates": "['u', 'cx']", "seed_transpiler": 2026,
                    "qiskit_version": version, "total_ops": 30 if topology == "linear" else 24,
                    "measurement_count": 4, "gate_count_1q": 12,
                    "gate_count_2q": twoq, "circuit_depth": depth,
                    "explicit_swap_count": 0, "input_swap_count": 0,
                    "transpile_time_seconds": trial / 1000, "trial_id": trial,
                })
                rows.append(row)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_integrated_analysis_reads_both_datasets_and_computes_frontier(tmp_path):
    connectivity, optimization = tmp_path / "connectivity.csv", tmp_path / "optimization.csv"
    _dataset(connectivity, "2.5.1")
    _dataset(optimization, "2.5.2")
    output = tmp_path / "combined.csv"

    summaries = analyze(connectivity, optimization, output)

    assert len(summaries) == 18
    assert {row["dataset"] for row in summaries} == {"connectivity", "optimization"}
    assert {row["topology"] for row in summaries if row["pareto_structural"]} == {"fully_connected"}
    assert output.exists()
    with output.open(newline="", encoding="utf-8") as stream:
        assert len(list(csv.DictReader(stream))) == 18


def test_integrated_analysis_rejects_bad_schema(tmp_path):
    connectivity, optimization = tmp_path / "connectivity.csv", tmp_path / "optimization.csv"
    _dataset(connectivity, "2.5.1")
    _dataset(optimization, "2.5.2")
    contents = optimization.read_text(encoding="utf-8").replace(
        "experiment_id,circuit_name", "circuit_name,experiment_id", 1
    )
    optimization.write_text(contents, encoding="utf-8")
    with pytest.raises(ValueError, match="exact 22-column schema"):
        analyze(connectivity, optimization, tmp_path / "output.csv")


def test_connectivity_opt0_output_labels_the_median(capsys, tmp_path):
    summaries = analyze(output_path=tmp_path / "summary.csv")
    captured = capsys.readouterr().out
    row = next(
        item for item in summaries
        if item["dataset"] == "connectivity"
        and item["topology"] == "linear"
        and item["optimization_level"] == 0
    )

    assert row["median_transpile_time_seconds"] == pytest.approx(0.0066507000010460615)
    assert "linear           Opt 0" in captured
    assert "median transpile time=6.651 ms" in captured
    assert "mean=an=" not in captured


def test_exhaustive_classical_max_cut_optimum():
    assert validate_classical_max_cut() == (4, {"0101", "1010"})
