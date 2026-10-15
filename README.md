
# Q-TRACE

**Compilation-Aware Resource Estimation for NISQ Quantum Circuits**

Q-TRACE investigates how transpiler optimization levels and hardware connectivity affect the compiled resource requirements of a QAOA circuit for the Max-Cut problem.

## Research Setup

- **Benchmark:** QAOA for Max-Cut
- **Graph:** Four-vertex cycle with edges (0,1), (1,2), (2,3), (3,0)
- **QAOA depth:** p = 1
- **Optimization levels:** 0, 1, 2, 3
- **Connectivity topologies:** Linear and fully connected
- **Basis gates:** `u`, `cx`
- **Transpiler seed:** 2026
- **Initial layout:** Identity layout

The experiment runner evaluates eight combinations of topology and optimization level.

## Metrics

The pipeline records:

- Total operations
- One-qubit gate count
- Two-qubit gate count
- Gate-only circuit depth
- Measurement count
- Explicit SWAP count
- Input-circuit SWAP count
- Transpilation time
- Qiskit and Python versions

Explicit SWAP counts are diagnostic only. SWAP operations may be decomposed into basis gates during transpilation, so two-qubit gate count and circuit depth are also used to examine potential routing overhead.

## Project Structure

```text
q-trace/
├── circuits/
├── experiments/
├── plots/
├── results/
│   └── qtrace_results.csv
├── src/
│   ├── __init__.py
│   ├── experiment_runner.py
│   ├── metrics.py
│   └── transpilation.py
├── tests/
│   └── test_experiment_runner.py
├── requirements.txt
└── README.md
```

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run Experiments

From the repository root:

```bash
python -m src.experiment_runner
```

The results are written to:

```text
results/qtrace_results.csv
```

Running the experiment runner again overwrites the previous CSV.

## Run Tests

Install pytest if it is not already installed:

```bash
python -m pip install pytest
```

Run the test suite:

```bash
python -m pytest -v
```

## Current Preliminary Observation

In the initial run, the linear configuration produced 12–14 two-qubit gates, while the fully connected configuration produced 8. These are preliminary results from one fixed circuit and parameter setting; they do not establish a general result for all QAOA circuits or hardware.

## Reproducibility

The transpiler seed, optimization level, topology, initial layout, basis gates, and software versions are recorded in the experiment output.

Transpilation time may vary across runs and system conditions. For stronger timing comparisons, use repeated trials and report a suitable summary statistic, such as the median.

## References

- Qiskit Transpiler Guide: https://qiskit.qotlabs.org/docs/guides/transpile
- Transpiler Stages: https://qiskit.qotlabs.org/docs/guides/transpiler-stages
- Qiskit Compiler API: https://qiskit.qotlabs.org/docs/api/qiskit/compiler
