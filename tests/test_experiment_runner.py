import pandas as pd
from qiskit import QuantumCircuit

from src.metrics import collect_metrics
from src.experiment_runner import OUTPUT_PATH, run_experiments
from src.experiment_runner import GRAPH_EDGES, build_qaoa_circuit


def test_graph_has_four_vertices_and_four_edges():
    assert len(set(v for edge in GRAPH_EDGES for v in edge)) == 4
    assert len(GRAPH_EDGES) == 4


def test_qaoa_circuit_has_four_qubits():
    circuit = build_qaoa_circuit()
    assert circuit.num_qubits == 4


def test_qaoa_circuit_has_measurements():
    circuit = build_qaoa_circuit()
    assert circuit.count_ops().get("measure", 0) == 4


def test_qaoa_circuit_contains_cost_and_mixer_gates():
    circuit = build_qaoa_circuit()
    operations = circuit.count_ops()

    assert operations.get("rzz", 0) == 4
    assert operations.get("rx", 0) == 4
    assert operations.get("h", 0) == 4


from src.transpilation import OPTIMIZATION_LEVELS, transpile_circuit


def test_all_transpilation_configurations():
    circuit = build_qaoa_circuit()

    for topology in ("linear", "fully_connected"):
        for level in OPTIMIZATION_LEVELS:
            compiled, elapsed = transpile_circuit(
                circuit,
                optimization_level=level,
                topology=topology,
            )

            assert compiled.num_qubits == 4
            assert elapsed >= 0
            assert compiled.count_ops().get("measure", 0) == 4


def test_invalid_topology_is_rejected():
    from src.transpilation import get_coupling_map
    import pytest

    with pytest.raises(ValueError):
        get_coupling_map("invalid_topology")


def test_invalid_optimization_level_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        transpile_circuit(
            build_qaoa_circuit(),
            optimization_level=4,
            topology="linear",
        )

from src.experiment_runner import GAMMA


def test_qaoa_cost_gates_use_expected_angle():
    circuit = build_qaoa_circuit()

    cost_gates = [
        instruction.operation
        for instruction in circuit.data
        if instruction.operation.name == "rzz"
    ]

    assert len(cost_gates) == len(GRAPH_EDGES)
    assert all(
        abs(gate.params[0] - (-GAMMA)) < 1e-10
        for gate in cost_gates
    )


def test_metrics_exclude_barriers_and_measurements_from_gate_depth():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.barrier()
    circuit.measure_all()

    metrics = collect_metrics(circuit)

    assert metrics["num_qubits"] == 2
    assert metrics["measurement_count"] == 2
    assert metrics["gate_count_1q"] == 1
    assert metrics["gate_count_2q"] == 1
    assert metrics["circuit_depth"] == 2


def test_metrics_count_explicit_swap():
    circuit = QuantumCircuit(2)
    circuit.swap(0, 1)

    metrics = collect_metrics(circuit)

    assert metrics["explicit_swap_count"] == 1
    assert metrics["gate_count_2q"] == 1


def test_experiment_results_have_forty_rows():
    results = run_experiments()

    assert len(results) == 40
    assert len({row["experiment_id"] for row in results}) == 8

    for row in results:
        assert row["trial_id"] in range(1, 6)

    assert {
        (row["topology"], row["optimization_level"])
        for row in results
    } == {
        (topology, level)
        for topology in ("linear", "fully_connected")
        for level in range(4)
    }
