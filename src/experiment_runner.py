
from pathlib import Path
from statistics import median

import qiskit
from qiskit import QuantumCircuit

from src.metrics import collect_metrics
from src.transpilation import (
    BASIS_GATES,
    NUM_QUBITS,
    OPTIMIZATION_LEVELS,
    SEED_TRANSPILER,
    transpile_circuit,
)
from src.experiment_schema import (
    CSV_COLUMNS,
    GRAPH_EDGES_SERIALIZED,
    INITIAL_LAYOUT_SERIALIZED,
    baseline_record,
    write_csv_atomic,
)


GRAPH_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]

GAMMA = 0.5
BETA = 0.25
NUM_TRIALS = 5

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "results" / "qtrace_results.csv"


def build_qaoa_circuit() -> QuantumCircuit:
    """Build a p=1 QAOA circuit for Max-Cut on a four-vertex cycle."""

    circuit = QuantumCircuit(NUM_QUBITS)

    for qubit in range(NUM_QUBITS):
        circuit.h(qubit)

    for u, v in GRAPH_EDGES:
        circuit.rzz(-GAMMA, u, v)

    for qubit in range(NUM_QUBITS):
        circuit.rx(2 * BETA, qubit)

    circuit.measure_all()
    return circuit

def collect_baseline() -> dict:
    """Collect metrics for the original, untranspiled QAOA circuit."""

    circuit = build_qaoa_circuit()
    return baseline_record(circuit)



def run_experiments() -> list[dict]:
    """Run five trials for each topology and optimization configuration."""

    results = []
    experiment_number = 0

    for topology in ("linear", "fully_connected"):
        for level in OPTIMIZATION_LEVELS:
            experiment_number += 1
            configuration_times = []

            for trial_id in range(1, NUM_TRIALS + 1):
                circuit = build_qaoa_circuit()

                compiled, elapsed = transpile_circuit(
                    circuit,
                    optimization_level=level,
                    topology=topology,
                )

                metrics = collect_metrics(compiled)
                configuration_times.append(elapsed)

                input_swap_count = sum(
                    instruction.operation.name == "swap"
                    for instruction in circuit.data
                )

                results.append({
                    "experiment_id": f"EXP-{experiment_number:02d}",
                    "circuit_name": "QAOA_MaxCut_Cycle4_p1",
                    "graph_edges": GRAPH_EDGES_SERIALIZED,
                    "num_qubits": NUM_QUBITS,
                    "qaoa_p": 1,
                    "parameter_values": f"gamma={GAMMA},beta={BETA}",
                    "optimization_level": level,
                    "topology": topology,
                    "initial_layout": INITIAL_LAYOUT_SERIALIZED,
                    "routing_method": "Qiskit preset default",
                    "basis_gates": str(BASIS_GATES),
                    "seed_transpiler": SEED_TRANSPILER,
                    "qiskit_version": qiskit.__version__,
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

            print(
                f"{experiment_number}/8 | {topology} | "
                f"optimization={level} | "
                f"2q gates={metrics['gate_count_2q']} | "
                f"depth={metrics['circuit_depth']} | "
                f"median time={median(configuration_times):.6f}s"
            )

    return results


def save_results(results: list[dict]) -> None:
    """Save baseline metrics and all compiled experiment trials to CSV."""

    if not results:
        raise ValueError("No experiment results were produced.")

    baseline = collect_baseline()
    all_results = [baseline] + results
    if any(set(row) != set(CSV_COLUMNS) for row in all_results):
        raise ValueError("Experiment records do not match the shared CSV schema.")

    write_csv_atomic(OUTPUT_PATH, all_results)

    print(
        f"\nSaved {len(all_results)} records "
        f"({len(all_results) - 1} compiled trials + 1 baseline) "
        f"to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    experiment_results = run_experiments()
    save_results(experiment_results)
