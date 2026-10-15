
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
