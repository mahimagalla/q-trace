
import csv
import platform
from pathlib import Path

import qiskit
from qiskit import QuantumCircuit

from src.metrics import collect_metrics
from src.transpilation import (
    BASIS_GATES,
    NUM_QUBITS,
    OPTIMIZATION_LEVELS,
    SEED_TRANSPIER,
    transpile_circuit,
)


GRAPH_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]

GAMMA = 0.5
BETA = 0.25

OUTPUT_PATH = Path("results") / "qtrace_results.csv"


def build_qaoa_circuit() -> QuantumCircuit:
    """Build a p=1 QAOA circuit for Max-Cut on a four-vertex cycle."""

    circuit = QuantumCircuit(NUM_QUBITS)

    for qubit in range(NUM_QUBITS):
        circuit.h(qubit)

    for u, v in GRAPH_EDGES:
        circuit.rzz(2 * GAMMA, u, v)

    for qubit in range(NUM_QUBITS):
        circuit.rx(2 * BETA, qubit)

    circuit.measure_all()

    return circuit


def run_experiments() -> list[dict]:
    """Run all eight topology and optimization configurations."""

    results = []
    experiment_number = 0

    for topology in ("linear", "fully_connected"):
        for level in OPTIMIZATION_LEVELS:
            experiment_number += 1

            circuit = build_qaoa_circuit()

            compiled, elapsed = transpile_circuit(
                circuit,
                optimization_level=level,
                topology=topology,
            )

            metrics = collect_metrics(compiled)

            input_swap_count = sum(
                instruction.operation.name == "swap"
                for instruction in circuit.data
            )

            results.append({
                "experiment_id": f"EXP-{experiment_number:02d}",
                "circuit_name": "QAOA_MaxCut_Cycle4_p1",
                "graph_edges": str(GRAPH_EDGES),
                "num_qubits": NUM_QUBITS,
                "qaoa_p": 1,
                "parameter_values": f"gamma={GAMMA},beta={BETA}",
                "optimization_level": level,
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
                "trial_id": 1,
            })

            print(
                f"{experiment_number}/8 | {topology} | "
                f"optimization={level} | "
                f"2q gates={metrics['gate_count_2q']} | "
                f"depth={metrics['circuit_depth']}"
            )

    return results


def save_results(results: list[dict]) -> None:
    """Save experiment metrics to CSV."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not results:
        raise ValueError("No experiment results were produced.")

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved {len(results)} experiments to {OUTPUT_PATH}")


if __name__ == "__main__":
    experiment_results = run_experiments()
    save_results(experiment_results)
