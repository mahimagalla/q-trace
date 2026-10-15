
from qiskit import QuantumCircuit


def collect_metrics(circuit: QuantumCircuit) -> dict:
    """Collect resource metrics from a quantum circuit."""

    one_qubit_gates = 0
    two_qubit_gates = 0
    measurement_count = 0
    explicit_swap_count = 0

    for instruction in circuit.data:
        operation = instruction.operation
        name = operation.name

        if name == "measure":
            measurement_count += 1
            continue

        if name in {"barrier", "delay"}:
            continue

        if name == "swap":
            explicit_swap_count += 1

        if operation.num_qubits == 1:
            one_qubit_gates += 1
        elif operation.num_qubits == 2:
            two_qubit_gates += 1

    gate_only_circuit = circuit.copy()
    gate_only_circuit.remove_final_measurements(inplace=True)

    for instruction in list(gate_only_circuit.data):
        if instruction.operation.name in {"barrier", "delay"}:
            gate_only_circuit.data.remove(instruction)

    return {
        "num_qubits": circuit.num_qubits,
        "total_ops": circuit.size(),
        "measurement_count": measurement_count,
        "gate_count_1q": one_qubit_gates,
        "gate_count_2q": two_qubit_gates,
        "circuit_depth": gate_only_circuit.depth(),
        "explicit_swap_count": explicit_swap_count,
    }
