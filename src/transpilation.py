
from time import perf_counter

from qiskit import QuantumCircuit, transpile


NUM_QUBITS = 4
BASIS_GATES = ["u", "cx"]
SEED_TRANSPILER = 2026
OPTIMIZATION_LEVELS = [0, 1, 2, 3]


def get_coupling_map(topology: str) -> list[list[int]]:
    """Return the directed coupling map for a supported topology."""

    if topology == "linear":
        return [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2]]

    if topology == "fully_connected":
        return [
            [i, j]
            for i in range(NUM_QUBITS)
            for j in range(NUM_QUBITS)
            if i != j
        ]

    raise ValueError(
        "Unsupported topology. Use 'linear' or 'fully_connected'."
    )


def transpile_circuit(
    circuit: QuantumCircuit,
    optimization_level: int,
    topology: str,
) -> tuple[QuantumCircuit, float]:
    """Transpile a circuit and return it with the elapsed time."""

    if optimization_level not in OPTIMIZATION_LEVELS:
        raise ValueError("optimization_level must be between 0 and 3.")

    coupling_map = get_coupling_map(topology)

    start_time = perf_counter()

    compiled_circuit = transpile(
        circuit.copy(),
        basis_gates=BASIS_GATES,
        coupling_map=coupling_map,
        initial_layout=list(range(NUM_QUBITS)),
        optimization_level=optimization_level,
        seed_transpiler=SEED_TRANSPILER,
    )

    elapsed_time = perf_counter() - start_time

    return compiled_circuit, elapsed_time
