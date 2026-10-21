"""Unit tests for Member 4's connectivity experiment module."""

import pytest
from experiments.connectivity.connectivity_runner import (
    EXPECTED_FC_MAP,
    EXPECTED_LINEAR_MAP,
    compute_connectivity_overhead_summary,
    run_connectivity_trials,
    validate_topology_definitions,
)
from src.experiment_schema import CSV_COLUMNS, GRAPH_EDGES_SERIALIZED, INITIAL_LAYOUT_SERIALIZED
from src.transpilation import OPTIMIZATION_LEVELS, get_coupling_map


def test_topology_coupling_maps():
    """Verify directed coupling map definitions for Linear and Fully Connected."""
    validate_topology_definitions()

    linear_map = get_coupling_map("linear")
    assert len(linear_map) == 6
    assert sorted(linear_map) == sorted(EXPECTED_LINEAR_MAP)

    fc_map = get_coupling_map("fully_connected")
    assert len(fc_map) == 12
    assert sorted(fc_map) == sorted(EXPECTED_FC_MAP)


def test_connectivity_trial_generation():
    """Verify trial execution for all topologies and optimization levels (1 trial each)."""
    results = run_connectivity_trials(
        topologies=("linear", "fully_connected"),
        optimization_levels=(0, 1, 2, 3),
        num_trials=1,
    )

    # 2 topologies * 4 optimization levels * 1 trial = 8 records
    assert len(results) == 8

    expected_keys = {
        "experiment_id",
        "circuit_name",
        "graph_edges",
        "num_qubits",
        "qaoa_p",
        "parameter_values",
        "optimization_level",
        "topology",
        "initial_layout",
        "routing_method",
        "basis_gates",
        "seed_transpiler",
        "qiskit_version",
        "total_ops",
        "measurement_count",
        "gate_count_1q",
        "gate_count_2q",
        "circuit_depth",
        "explicit_swap_count",
        "input_swap_count",
        "transpile_time_seconds",
        "trial_id",
    }

    for row in results:
        assert list(row) == CSV_COLUMNS
        assert set(row) == expected_keys
        assert row["graph_edges"] == GRAPH_EDGES_SERIALIZED
        assert row["initial_layout"] == INITIAL_LAYOUT_SERIALIZED
        assert row["optimization_level"] in OPTIMIZATION_LEVELS
        assert row["topology"] in ("linear", "fully_connected")
        assert row["transpile_time_seconds"] > 0
        assert row["circuit_depth"] > 0
        assert row["gate_count_2q"] > 0


def test_connectivity_routing_overhead():
    """Verify that Linear topology incurs 2Q gate and depth overhead compared to Fully Connected."""
    results = run_connectivity_trials(
        topologies=("linear", "fully_connected"),
        optimization_levels=(0, 1, 2, 3),
        num_trials=1,
    )

    data = {(r["topology"], r["optimization_level"]): r for r in results}

    for opt in OPTIMIZATION_LEVELS:
        linear_row = data[("linear", opt)]
        fc_row = data[("fully_connected", opt)]

        # Linear must have more 2Q gates due to missing (3, 0) physical interaction
        assert linear_row["gate_count_2q"] > fc_row["gate_count_2q"]

        # Linear must have higher depth
        assert linear_row["circuit_depth"] > fc_row["circuit_depth"]


def test_compute_connectivity_overhead_summary():
    """Verify calculation of summary routing overhead table."""
    mock_results = [
        {
            "topology": "linear",
            "optimization_level": 0,
            "gate_count_1q": 12,
            "gate_count_2q": 14,
            "circuit_depth": 18,
            "transpile_time_seconds": 0.010,
        },
        {
            "topology": "fully_connected",
            "optimization_level": 0,
            "gate_count_1q": 12,
            "gate_count_2q": 8,
            "circuit_depth": 14,
            "transpile_time_seconds": 0.005,
        },
        {
            "topology": "linear",
            "optimization_level": 1,
            "gate_count_1q": 12,
            "gate_count_2q": 14,
            "circuit_depth": 18,
            "transpile_time_seconds": 0.012,
        },
        {
            "topology": "fully_connected",
            "optimization_level": 1,
            "gate_count_1q": 12,
            "gate_count_2q": 8,
            "circuit_depth": 14,
            "transpile_time_seconds": 0.006,
        },
        {
            "topology": "linear",
            "optimization_level": 2,
            "gate_count_1q": 17,
            "gate_count_2q": 12,
            "circuit_depth": 18,
            "transpile_time_seconds": 0.015,
        },
        {
            "topology": "fully_connected",
            "optimization_level": 2,
            "gate_count_1q": 12,
            "gate_count_2q": 8,
            "circuit_depth": 14,
            "transpile_time_seconds": 0.010,
        },
        {
            "topology": "linear",
            "optimization_level": 3,
            "gate_count_1q": 17,
            "gate_count_2q": 12,
            "circuit_depth": 18,
            "transpile_time_seconds": 0.014,
        },
        {
            "topology": "fully_connected",
            "optimization_level": 3,
            "gate_count_1q": 12,
            "gate_count_2q": 8,
            "circuit_depth": 14,
            "transpile_time_seconds": 0.010,
        },
    ]

    summary_df = compute_connectivity_overhead_summary(mock_results)
    assert len(summary_df) == 4

    row_opt0 = summary_df[summary_df["Opt Level"] == 0].iloc[0]
    assert row_opt0["Linear 2Q"] == 14
    assert row_opt0["FC 2Q"] == 8
    assert row_opt0["2Q Overhead (%)"] == "+75.0%"
    assert row_opt0["Depth Overhead (%)"] == "+28.6%"

def test_validate_sample_csv_row_and_routing_constraints():
    """Validate a sample CSV row against a live compiled circuit and check topology routing."""
    import pandas as pd
    from src.experiment_runner import build_qaoa_circuit
    from src.metrics import collect_metrics
    from src.transpilation import get_coupling_map, transpile_circuit
    from experiments.connectivity.connectivity_runner import CONNECTIVITY_RESULTS_PATH

    assert CONNECTIVITY_RESULTS_PATH.exists(), "results/connectivity_experiments.csv does not exist"

    df = pd.read_csv(CONNECTIVITY_RESULTS_PATH)
    assert list(df.columns) == CSV_COLUMNS

    # 1. Validate baseline row
    baseline_rows = df[df["experiment_id"] == "EXP-BASELINE"]
    assert len(baseline_rows) == 1
    baseline = baseline_rows.iloc[0]
    assert baseline["topology"] == "baseline"
    assert baseline["num_qubits"] == 4
    assert baseline["gate_count_2q"] == 4  # 4 RZZ gates
    assert baseline["gate_count_1q"] == 8  # 4 H + 4 RX gates
    assert baseline["circuit_depth"] == 6
    assert baseline["input_swap_count"] == 0

    # 2. Validate sample compiled row (EXP-CONN-01, Trial 1)
    sample_rows = df[(df["experiment_id"] == "EXP-CONN-01") & (df["trial_id"] == 1)]
    assert len(sample_rows) == 1
    sample = sample_rows.iloc[0]

    circuit = build_qaoa_circuit()
    compiled, _ = transpile_circuit(circuit, optimization_level=0, topology="linear")
    metrics = collect_metrics(compiled)

    # Verify metric consistency between CSV and compiled circuit
    assert int(sample["gate_count_2q"]) == metrics["gate_count_2q"] == 14
    assert int(sample["gate_count_1q"]) == metrics["gate_count_1q"] == 12
    assert int(sample["circuit_depth"]) == metrics["circuit_depth"] == 18
    assert int(sample["total_ops"]) == metrics["total_ops"] == 30
    assert int(sample["explicit_swap_count"]) == metrics["explicit_swap_count"] == 0
    assert int(sample["measurement_count"]) == metrics["measurement_count"] == 4

    # 3. Verify that topology routing constraints are strictly enforced
    # Every 2-qubit gate in the compiled circuit must be on an allowed edge of the linear topology
    linear_allowed = set(map(tuple, get_coupling_map("linear")))
    for instruction in compiled.data:
        if instruction.operation.num_qubits == 2:
            q0 = compiled.find_bit(instruction.qubits[0]).index
            q1 = compiled.find_bit(instruction.qubits[1]).index
            assert (q0, q1) in linear_allowed, (
                f"Routing constraint violated: gate placed on unauthorized edge ({q0}, {q1})"
            )
