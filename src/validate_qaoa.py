
from qiskit.quantum_info import Statevector
from src.experiment_runner import (
    GRAPH_EDGES,
    build_qaoa_circuit,
    NUM_QUBITS,
)
from src.transpilation import OPTIMIZATION_LEVELS, transpile_circuit


def cut_value(bitstring):
    bits = bitstring[::-1]
    return sum(bits[u] != bits[v] for u, v in GRAPH_EDGES)


def get_probabilities(circuit):
    circuit = circuit.copy()
    circuit.remove_final_measurements(inplace=True)
    return Statevector.from_instruction(circuit).probabilities()


def align_compiled_probabilities(original, compiled):
    probabilities = get_probabilities(compiled)
    layout = compiled.layout

    if layout is None:
        return probabilities

    final_layout = layout.final_index_layout(filter_ancillas=True)
    aligned = [0.0] * (2 ** original.num_qubits)

    for logical_index in range(2 ** original.num_qubits):
        physical_index = 0

        for logical_qubit, physical_qubit in enumerate(final_layout):
            bit = (logical_index >> logical_qubit) & 1
            physical_index |= bit << physical_qubit

        aligned[logical_index] = probabilities[physical_index]

    return aligned


def validate_qaoa():
    original = build_qaoa_circuit()
    original_probabilities = get_probabilities(original)

    state = Statevector.from_instruction(
        original.copy().remove_final_measurements(inplace=False)
    )
    probabilities = state.probabilities_dict()

    expected_cut = sum(
        probabilities[bitstring] * cut_value(bitstring)
        for bitstring in probabilities
    )

    optimal_probability = sum(
        probability
        for bitstring, probability in probabilities.items()
        if cut_value(bitstring) == len(GRAPH_EDGES)
    )

    print(f"Qubits: {NUM_QUBITS}")
    print(f"Graph edges: {len(GRAPH_EDGES)}")
    print(
        f"Expected Max-Cut value: "
        f"{expected_cut:.6f} / {len(GRAPH_EDGES)}"
    )
    print(
        f"Probability of an optimal cut: "
        f"{optimal_probability:.6f}"
    )

    assert abs(expected_cut - 2.708073) < 1e-5
    assert abs(optimal_probability - 0.358374) < 1e-5

    print("\nTranspilation equivalence checks:")

    for topology in ("linear", "fully_connected"):
        for level in OPTIMIZATION_LEVELS:
            compiled, _ = transpile_circuit(
                original,
                optimization_level=level,
                topology=topology,
            )

            compiled_probabilities = align_compiled_probabilities(
                original, compiled
            )

            difference = max(
                abs(a - b)
                for a, b in zip(
                    original_probabilities,
                    compiled_probabilities,
                )
            )

            print(
                f"{topology:16} | optimization={level} "
                f"| max probability difference={difference:.3e}"
            )

            assert difference < 1e-8, (
                f"Output probabilities differ for {topology}, "
                f"optimization level {level}"
            )

    print("\nAll QAOA and transpilation validation checks passed.")


if __name__ == "__main__":
    validate_qaoa()
