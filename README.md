
# Q-TRACE

**Compilation-Aware Resource Estimation for NISQ Quantum Circuits**

Q-TRACE studies how transpiler optimization levels and hardware connectivity affect the compiled resource requirements of a QAOA circuit for the Max-Cut problem.

## Experiment Configuration

- **Benchmark:** QAOA for Max-Cut
- **Graph:** Four-vertex cycle
- **Edges:** (0,1), (1,2), (2,3), (3,0)
- **QAOA depth:** p = 1
- **Fixed parameters:** gamma = 0.5, beta = 0.25
- **Optimization levels:** 0, 1, 2, 3
- **Connectivity:** Linear and fully connected
- **Basis gates:** `u`, `cx`
- **Initial layout:** Identity layout
- **Transpiler seed:** 2026
- **Trials per configuration:** 5

The experiment runner evaluates eight topology/optimization configurations and stores five raw timing trials per configuration, producing 40 rows.

## QAOA Circuit

The circuit prepares a uniform superposition using Hadamard gates, applies the cost unitary using `RZZ` gates, applies the mixer using `RX` gates, and measures the qubits.

The Max-Cut cost Hamiltonian convention used is:

\[
H_C = \sum_{(u,v)\in E}\frac{I-Z_uZ_v}{2}
\]

The cost-unitary convention is:

\[
U_C(\gamma)=e^{-i\gamma H_C}
\]

For this convention, the implementation uses `rzz(-GAMMA, u, v)` for each graph edge, up to a global phase.

The parameters are fixed starting values, not claimed to be optimal. The current tests check the circuit structure and expected cost-gate angle; a separate objective-value validation is still required before claiming solution quality.

## Metrics

The CSV records:

- Number of qubits
- Total operations
- Measurement count
- One-qubit operation count
- Two-qubit operation count
- Gate-only circuit depth
- Explicit SWAP count
- Input-circuit SWAP count
- Transpilation time
- Topology and optimization level
- Qiskit and Python versions
- Trial ID and transpiler seed

Measurements, barriers, and delays are excluded from the one-qubit and two-qubit operation counts. Gate-only depth is calculated after excluding those operations.

`explicit_swap_count` counts instructions named `swap` in the compiled circuit. Routing SWAPs may be decomposed into basis gates, so this count alone does not measure total routing overhead.

`input_swap_count` counts explicit SWAP instructions in the original QAOA input circuit.

The two-qubit operation count includes all two-qubit operations, not exclusively entangling gates.

## Preliminary Findings

In the current experiment:

| Optimization level | Linear two-qubit operations | Fully connected two-qubit operations |
|---:|---:|---:|
| 0 | 14 | 8 |
| 1 | 14 | 8 |
| 2 | 12 | 8 |
| 3 | 12 | 8 |

The measured gate-only depth was 18 for linear connectivity and 14 for fully connected connectivity at every optimization level in this run.

These are preliminary results for one four-qubit circuit, one parameter setting, and the selected Qiskit transpiler configuration. They should not be generalized to all quantum circuits or hardware.

## Timing Methodology

Each configuration is transpiled five times using the same transpiler seed and settings. All 40 raw timing observations are retained in the CSV.

Median transpilation time is reported for each configuration. Minimum-to-maximum ranges describe observed variability; they are not confidence intervals.

Repeated timings with a fixed seed measure runtime variability under fixed compilation settings. They do not represent independent random transpiler configurations.

## Project Structure

```text
q-trace/
├── circuits/
├── experiments/
├── plots/
│   ├── two_qubit_gates.png
│   ├── circuit_depth.png
│   └── transpilation_time.png
├── results/
│   └── qtrace_results.csv
├── src/
│   ├── __init__.py
│   ├── experiment_runner.py
│   ├── metrics.py
│   ├── plot_results.py
│   └── transpilation.py
├── tests/
│   └── test_experiment_runner.py
├── requirements.txt
└── README.md
```

## Setup

Create and activate a virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run Experiments

From the repository root:

```cmd
python -m src.experiment_runner
```

The output is saved to `results/qtrace_results.csv`. Running the experiment runner again overwrites the previous CSV.

## Generate Plots

```cmd
python -m src.plot_results
```

Plots are written to the `plots/` directory.

## Run Tests

```cmd
python -m pip install pytest
python -m pytest -v
```

## References

- Qiskit Transpiler Guide: https://qiskit.qotlabs.org/docs/guides/transpile
- Transpiler Stages: https://qiskit.qotlabs.org/docs/guides/transpiler-stages
- Qiskit Compiler API: https://qiskit.qotlabs.org/docs/api/qiskit/compiler
