"""Optimization-Level Experiment Runner for Q-TRACE.

Member 3: K Prerana (2024BCS0048)
Primary Responsibility: Optimization-level experiments (Levels 0, 1, 2, 3).

This module systematically evaluates how Qiskit transpiler optimization levels
(0, 1, 2, 3) affect compiled quantum circuit metrics:
- 1-qubit and 2-qubit gate counts
- Total operations
- Gate-only circuit depth
- Explicit SWAP counts
- Classical transpilation duration across repeated trials
"""

import csv
import platform
import sys
from pathlib import Path
from statistics import mean, median

# Ensure repository root is on sys.path for direct or modular execution
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import qiskit
from qiskit import QuantumCircuit

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
    transpile_circuit,
)

NUM_TRIALS = 5
OPTIMIZATION_RESULTS_PATH = REPO_ROOT / "results" / "optimization_experiments.csv"


def run_optimization_trials(
    topologies: tuple[str, ...] = ("fully_connected", "linear"),
    optimization_levels: tuple[int, ...] = tuple(OPTIMIZATION_LEVELS),
    num_trials: int = NUM_TRIALS,
) -> list[dict]:
    """Execute transpilation across optimization levels and topologies.

    All other parameters (basis gates, seed, layout) are held strictly constant.
    """
    records = []
    exp_idx = 0

    print("=" * 72)
    print("Q-TRACE: Running Optimization-Level Experiments (Levels 0, 1, 2, 3)")
    print(f"Topologies: {topologies} | Trials per configuration: {num_trials}")
    print(f"Basis gates: {BASIS_GATES} | Seed: {SEED_TRANSPIER}")
    print("=" * 72)

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
                    "experiment_id": f"EXP-OPT-{exp_idx:02d}",
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


def save_optimization_results(
    results: list[dict],
    output_path: Path = OPTIMIZATION_RESULTS_PATH,
) -> None:
    """Save optimization experiment records to CSV."""
    if not results:
        raise ValueError("No optimization experiment records to save.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[OK] Saved {len(results)} trial records to: {output_path}")


def compute_optimization_summary(results: list[dict]) -> dict:
    """Compute aggregate metric summaries across optimization levels."""
    import pandas as pd

    df = pd.DataFrame(results)
    summary = (
        df.groupby(["topology", "optimization_level"])
        .agg(
            gate_count_1q=("gate_count_1q", "first"),
            gate_count_2q=("gate_count_2q", "first"),
            circuit_depth=("circuit_depth", "first"),
            explicit_swap_count=("explicit_swap_count", "first"),
            median_time_ms=("transpile_time_seconds", lambda s: median(s) * 1000),
            mean_time_ms=("transpile_time_seconds", lambda s: mean(s) * 1000),
            min_time_ms=("transpile_time_seconds", lambda s: min(s) * 1000),
            max_time_ms=("transpile_time_seconds", lambda s: max(s) * 1000),
        )
        .reset_index()
    )
    return summary


def main():
    results = run_optimization_trials()
    save_optimization_results(results)

    summary = compute_optimization_summary(results)
    print("\nOptimization Summary Table:")
    print("-" * 88)
    print(summary.to_string(index=False))
    print("-" * 88)


if __name__ == "__main__":
    main()
