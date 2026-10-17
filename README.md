
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

To run the dedicated optimization experiments across levels 0, 1, 2, and 3:

```cmd
python -m experiments.optimization.optimization_runner
```

The output is saved to `results/qtrace_results.csv` and `results/optimization_experiments.csv`.

## Generate Plots

```cmd
python -m src.plot_results
python -m experiments.optimization.plot_optimization
```

Plots are written to `plots/` and `plots/optimization/`.

## Run Tests

```cmd
python -m pip install pytest
python -m pytest -v
```

## References

- Qiskit Transpiler Guide: https://qiskit.qotlabs.org/docs/guides/transpile
- Transpiler Stages: https://qiskit.qotlabs.org/docs/guides/transpiler-stages
- Qiskit Compiler API: https://qiskit.qotlabs.org/docs/api/qiskit/compiler


## QAOA Validation and Transpilation Equivalence

### Circuit validation

The Q-TRACE experiment uses a four-qubit QAOA circuit for Max-Cut on a four-vertex cycle with four edges.

The circuit uses:
- QAOA depth: p = 1
- Cost parameter: gamma = 0.5
- Mixer parameter: beta = 0.25
- Cost gates: RZZ(-gamma)
- Mixer gates: RX(2 * beta)

Ideal statevector simulation produced the following baseline results:

| Metric | Result |
|---|---:|
| Number of qubits | 4 |
| Number of graph edges | 4 |
| Expected Max-Cut value | 2.708073 / 4 |
| Probability of an optimal cut | 0.358374 |

These results correspond to the fixed circuit parameters used in this experiment. They do not establish that the parameters are globally optimal.

### Transpilation equivalence

The original circuit was compared with transpiled circuits for both coupling topologies and optimization levels 0–3.

The comparison accounts for the transpiler's final qubit layout before comparing output probability distributions.

| Topology | Optimization level | Maximum probability difference |
|---|---:|---:|
| Linear | 0 | 4.163e-16 |
| Linear | 1 | 4.163e-16 |
| Linear | 2 | 2.776e-16 |
| Linear | 3 | 2.776e-16 |
| Fully connected | 0 | 4.163e-16 |
| Fully connected | 1 | 4.163e-16 |
| Fully connected | 2 | 4.163e-16 |
| Fully connected | 3 | 4.163e-16 |

The differences are at floating-point numerical precision, supporting ideal output-probability equivalence for all eight tested configurations.

### Observed connectivity effects

For the tested circuit, the compiled structural metrics were:

| Topology | Optimization level | Two-qubit operations | Circuit depth |
|---|---:|---:|---:|
| Linear | 0 | 14 | 18 |
| Linear | 1 | 14 | 18 |
| Linear | 2 | 12 | 18 |
| Linear | 3 | 12 | 18 |
| Fully connected | 0 | 8 | 14 |
| Fully connected | 1 | 8 | 14 |
| Fully connected | 2 | 8 | 14 |
| Fully connected | 3 | 8 | 14 |

For this specific circuit, the linear coupling topology produced 50%–75% more two-qubit operations than the fully connected topology, depending on the optimization level. Its circuit depth was approximately 28.6% higher.

These are observations for the selected graph, circuit parameters, basis gates, layout, and Qiskit version. They should not be generalized to all quantum circuits or hardware.

Two-qubit operation counts and circuit depth are used as structural indicators. Explicit SWAP counts alone may not capture all routing overhead because transpilation can decompose or eliminate SWAP operations.

### Automated validation

Run the following commands from the project root:

```bash
python -m src.validate_qaoa
python -m pytest -v
```

The test suite checks circuit construction, gate parameters, metrics, experiment records, and output-probability equivalence across all eight transpilation configurations.
