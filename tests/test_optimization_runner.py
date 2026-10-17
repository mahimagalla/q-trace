"""Unit tests for Member 3's optimization experiment module."""

import pytest
from experiments.optimization.optimization_runner import (
    NUM_TRIALS,
    compute_optimization_summary,
    run_optimization_trials,
)
from src.transpilation import OPTIMIZATION_LEVELS


def test_optimization_trial_generation():
    """Verify trial execution for all optimization levels with 1 trial per configuration."""
    results = run_optimization_trials(
        topologies=("linear", "fully_connected"),
        optimization_levels=(0, 1, 2, 3),
        num_trials=1,
    )

    # 2 topologies * 4 optimization levels * 1 trial = 8 records
    assert len(results) == 8

    expected_keys = {
        "experiment_id",
        "circuit_name",
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
        "python_version",
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
        assert expected_keys.issubset(row.keys())
        assert row["optimization_level"] in OPTIMIZATION_LEVELS
        assert row["transpile_time_seconds"] > 0
        assert row["circuit_depth"] > 0
        assert row["gate_count_2q"] > 0


def test_linear_topology_gate_reduction():
    """Verify that optimization levels 2 and 3 reduce or match 2Q gates compared to 0 and 1."""
    results = run_optimization_trials(
        topologies=("linear",),
        optimization_levels=(0, 1, 2, 3),
        num_trials=1,
    )

    gates_by_level = {
        row["optimization_level"]: row["gate_count_2q"] for row in results
    }

    # Level 2/3 should optimize 2Q operations compared to Level 0
    assert gates_by_level[2] <= gates_by_level[0]
    assert gates_by_level[3] <= gates_by_level[1]


def test_compute_optimization_summary():
    """Verify calculation of summary metrics."""
    mock_results = [
        {
            "topology": "linear",
            "optimization_level": 0,
            "gate_count_1q": 10,
            "gate_count_2q": 14,
            "circuit_depth": 18,
            "explicit_swap_count": 0,
            "transpile_time_seconds": 0.05,
        },
        {
            "topology": "linear",
            "optimization_level": 0,
            "gate_count_1q": 10,
            "gate_count_2q": 14,
            "circuit_depth": 18,
            "explicit_swap_count": 0,
            "transpile_time_seconds": 0.06,
        },
    ]
    summary = compute_optimization_summary(mock_results)
    assert len(summary) == 1
    assert summary.iloc[0]["median_time_ms"] == pytest.approx(55.0, rel=1e-2)
