"""Connectivity and Routing Experiment Runner for Q-TRACE.

Member 4: Mounika Kolluru
Primary Responsibility: Connectivity and routing experiments (Linear vs. Fully Connected).

This module systematically evaluates the routing and structural overhead of
qubit connectivity constraints on a 4-vertex cycle QAOA Max-Cut benchmark:
- Linear topology (nearest-neighbor line: 0-1-2-3)
- Fully connected topology (all-to-all connectivity)
Across optimization levels 0, 1, 2, and 3 with 5 trials per configuration.
"""

import csv
import platform
import sys
from pathlib import Path
from statistics import median

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import qiskit
import pandas as pd

from src.experiment_runner import (
    BETA,
    GAMMA,
    GRAPH_EDGES,
    NUM_QUBITS,
    build_qaoa_circuit,
)
from src.metrics import collect_metrics
from src.transpilation import (
    BASIS_GATES,
    OPTIMIZATION_LEVELS,
    SEED_TRANSPIER,
    get_coupling_map,
    transpile_circuit,
)

NUM_TRIALS = 5
CONNECTIVITY_RESULTS_PATH = REPO_ROOT / "results" / "connectivity_experiments.csv"

# Expected coupling maps for 4 qubits
EXPECTED_LINEAR_MAP = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2]]
EXPECTED_FC_MAP = [
    [i, j] for i in range(NUM_QUBITS) for j in range(NUM_QUBITS) if i != j
]


def validate_topology_definitions() -> None:
    """Verify that the shared coupling maps match the research protocol."""
    linear_map = get_coupling_map("linear")
    fc_map = get_coupling_map("fully_connected")

    assert sorted(linear_map) == sorted(EXPECTED_LINEAR_MAP), (
        f"Linear coupling map mismatch: expected {EXPECTED_LINEAR_MAP}, got {linear_map}"
    )
    assert len(linear_map) == 6, f"Linear map must have 6 directed edges, got {len(linear_map)}"

    assert sorted(fc_map) == sorted(EXPECTED_FC_MAP), (
        f"Fully connected coupling map mismatch: expected {EXPECTED_FC_MAP}, got {fc_map}"
    )
    assert len(fc_map) == 12, f"Fully connected map must have 12 directed edges, got {len(fc_map)}"


def collect_baseline_record() -> dict:
    """Collect baseline metrics for the untranspiled QAOA input circuit."""
    circuit = build_qaoa_circuit()
    metrics = collect_metrics(circuit)

    return {
        "experiment_id": "EXP-BASELINE",
        "circuit_name": "QAOA_MaxCut_Cycle4_p1",
        "graph_edges": str(GRAPH_EDGES),
        "num_qubits": NUM_QUBITS,
        "qaoa_p": 1,
        "parameter_values": f"gamma={GAMMA},beta={BETA}",
        "optimization_level": "",
        "topology": "baseline",
        "initial_layout": str(list(range(NUM_QUBITS))),
        "routing_method": "",
        "basis_gates": str(BASIS_GATES),
        "seed_transpiler": SEED_TRANSPIER,
        "qiskit_version": qiskit.__version__,
        "python_version": platform.python_version(),
        "total_ops": metrics["total_ops"],
        "measurement_count": metrics["measurement_count"],
        "gate_count_1q": metrics["gate_count_1q"],
        "gate_count_2q": metrics["gate_count_2q"],
        "circuit_depth": metrics["circuit_depth"],
        "explicit_swap_count": metrics["explicit_swap_count"],
        "input_swap_count": 0,
        "transpile_time_seconds": "",
        "trial_id": "",
    }


def run_connectivity_trials(
    topologies: tuple[str, ...] = ("linear", "fully_connected"),
    optimization_levels: tuple[int, ...] = tuple(OPTIMIZATION_LEVELS),
    num_trials: int = NUM_TRIALS,
) -> list[dict]:
    """Execute transpilation across connectivity topologies and optimization levels."""
    validate_topology_definitions()

    records = []
    exp_idx = 0

    print("=" * 76)
    print("Q-TRACE: Running Connectivity & Routing Experiments")
    print(f"Topologies: {topologies} | Optimization levels: {optimization_levels}")
    print(f"Trials per configuration: {num_trials} | Seed: {SEED_TRANSPIER}")
    print("=" * 76)

    for topology in topologies:
        for opt_level in optimization_levels:
            exp_idx += 1
            trial_times = []

            for trial_id in range(1, num_trials + 1):
                circuit = build_qaoa_circuit()

                compiled, elapsed = transpile_circuit(
                    circuit,
                    optimization_level=opt_level,
                    topology=topology,
                )

                metrics = collect_metrics(compiled)
                trial_times.append(elapsed)

                input_swap_count = sum(
                    inst.operation.name == "swap" for inst in circuit.data
                )

                records.append({
                    "experiment_id": f"EXP-CONN-{exp_idx:02d}",
                    "circuit_name": "QAOA_MaxCut_Cycle4_p1",
                    "graph_edges": str(GRAPH_EDGES),
                    "num_qubits": NUM_QUBITS,
                    "qaoa_p": 1,
                    "parameter_values": f"gamma={GAMMA},beta={BETA}",
                    "optimization_level": opt_level,
                    "topology": topology,
                    "initial_layout": str(list(range(NUM_QUBITS))),
                    "routing_method": "Qiskit preset default",
                    "basis_gates": str(BASIS_GATES),
                    "seed_transpiler": SEED_TRANSPIER,
                    "qiskit_version": qiskit.__version__,
                    "python_version": platform.python_version(),
                    "total_ops": metrics["total_ops"],
                    "measurement_count": metrics["measurement_count"],
                    "gate_count_1q": metrics["gate_count_1q"],
                    "gate_count_2q": metrics["gate_count_2q"],
                    "circuit_depth": metrics["circuit_depth"],
                    "explicit_swap_count": metrics["explicit_swap_count"],
                    "input_swap_count": input_swap_count,
                    "transpile_time_seconds": elapsed,
                    "trial_id": trial_id,
                })

            med_time_ms = median(trial_times) * 1000
            print(
                f"[{exp_idx:02d}/8] Topology={topology:<16} | "
                f"Opt={opt_level} | "
                f"1Q={metrics['gate_count_1q']:2d} | "
                f"2Q={metrics['gate_count_2q']:2d} | "
                f"Depth={metrics['circuit_depth']:2d} | "
                f"Time={med_time_ms:7.3f} ms"
            )

    return records


def save_connectivity_results(
    results: list[dict],
    output_path: Path = CONNECTIVITY_RESULTS_PATH,
    include_baseline: bool = True,
) -> None:
    """Save connectivity experiment records and baseline to CSV."""
    if not results:
        raise ValueError("No connectivity experiment records to save.")

    all_rows = [collect_baseline_record()] + results if include_baseline else results

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n[OK] Saved {len(all_rows)} records to: {output_path}")


def compute_connectivity_overhead_summary(results: list[dict]) -> pd.DataFrame:
    """Compute routing overhead by comparing Linear to Fully Connected."""
    df = pd.DataFrame(results)
    grouped = (
        df.groupby(["optimization_level", "topology"])
        .agg(
            gate_count_1q=("gate_count_1q", "first"),
            gate_count_2q=("gate_count_2q", "first"),
            circuit_depth=("circuit_depth", "first"),
            median_time_ms=("transpile_time_seconds", lambda s: median(s) * 1000),
        )
        .reset_index()
    )

    rows = []
    for opt in OPTIMIZATION_LEVELS:
        lin = grouped[(grouped["optimization_level"] == opt) & (grouped["topology"] == "linear")].iloc[0]
        fc = grouped[(grouped["optimization_level"] == opt) & (grouped["topology"] == "fully_connected")].iloc[0]

        q2_overhead_pct = ((lin["gate_count_2q"] - fc["gate_count_2q"]) / fc["gate_count_2q"]) * 100
        depth_overhead_pct = ((lin["circuit_depth"] - fc["circuit_depth"]) / fc["circuit_depth"]) * 100

        rows.append({
            "Opt Level": opt,
            "Linear 2Q": lin["gate_count_2q"],
            "FC 2Q": fc["gate_count_2q"],
            "2Q Overhead (%)": f"+{q2_overhead_pct:.1f}%",
            "Linear Depth": lin["circuit_depth"],
            "FC Depth": fc["circuit_depth"],
            "Depth Overhead (%)": f"+{depth_overhead_pct:.1f}%",
            "Linear Med Time (ms)": f"{lin['median_time_ms']:.2f}",
            "FC Med Time (ms)": f"{fc['median_time_ms']:.2f}",
        })

    return pd.DataFrame(rows)


def main():
    results = run_connectivity_trials()
    save_connectivity_results(results)

    print("\nConnectivity Routing Overhead Analysis (Linear vs. Fully Connected):")
    print("=" * 88)
    summary_df = compute_connectivity_overhead_summary(results)
    print(summary_df.to_string(index=False))
    print("=" * 88)


if __name__ == "__main__":
    main()
