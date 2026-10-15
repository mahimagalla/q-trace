
from qiskit import QuantumCircuit


NON_GATE_OPERATIONS = {"measure", "barrier", "delay"}


def collect_metrics(circuit: QuantumCircuit) -> dict:
    """Collect operation counts and gate-only circuit depth."""

    one_qubit_gates = 0
    two_qubit_gates = 0
    measurement_count = 0
    explicit_swap_count = 0

    gate_only_circuit = QuantumCircuit(*circuit.qregs)

    for instruction in circuit.data:
        operation = instruction.operation
        name = operation.name

        if name == "measure":
            measurement_count += 1
            continue

        if name in {"barrier", "delay"}:
            continue

        qubits = [
            gate_only_circuit.qubits[circuit.find_bit(qubit).index]
            for qubit in instruction.qubits
        ]

        if name == "swap":
            explicit_swap_count += 1

        if operation.num_qubits == 1:
            one_qubit_gates += 1
        elif operation.num_qubits == 2:
            two_qubit_gates += 1

        gate_only_circuit.append(operation, qubits)

    return {
        "num_qubits": circuit.num_qubits,
        "total_ops": circuit.size(),
        "measurement_count": measurement_count,
        "gate_count_1q": one_qubit_gates,
        "gate_count_2q": two_qubit_gates,
        "circuit_depth": gate_only_circuit.depth(),
        "explicit_swap_count": explicit_swap_count,
    }
