# Q-TRACE: Compilation-Aware Resource Estimation for NISQ Quantum Circuits

**Team:** EIGEN5  
**Course:** IEG 313 — Quantum Computing for Engineers  
**Institution:** IIIT Kottayam

Q-TRACE (**Quantum Transpilation and Resource Analysis under Connectivity Effects**) is a research project that investigates how quantum circuit transpilation choices affect circuit structure, gate resources, and classical compilation time in Noisy Intermediate-Scale Quantum (NISQ) computing.

The project studies the interaction between transpiler optimization levels and qubit connectivity constraints using a reproducible Quantum Approximate Optimization Algorithm (QAOA) Max-Cut benchmark implemented with Qiskit.

Rather than assuming that higher optimization levels always produce better circuits, Q-TRACE compares measured resource metrics and identifies trade-offs using multi-objective Pareto analysis.

---

## Table of Contents

- [Overview](#overview)
- [Research Objectives](#research-objectives)
- [Research Questions](#research-questions)
- [Benchmark and Experimental Setup](#benchmark-and-experimental-setup)
- [Experimental Variables](#experimental-variables)
- [Metrics](#metrics)
- [Key Results](#key-results)
- [Pareto Analysis](#pareto-analysis)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [Installation and Setup](#installation-and-setup)
- [Running the Experiments](#running-the-experiments)
- [Integrated Analysis](#integrated-analysis)
- [Validation and Tests](#validation-and-tests)
- [Interpretation and Limitations](#interpretation-and-limitations)
- [Team Contributions](#team-contributions)
- [Reproducibility](#reproducibility)
- [License](#license)

---

## Overview

Quantum circuits designed at a logical level must be translated into instructions supported by a target quantum processor. This process, known as **transpilation**, can change the number and arrangement of gates, circuit depth, and compilation runtime.

Physical quantum processors also impose connectivity constraints: not every pair of physical qubits can necessarily interact directly. These restrictions can introduce additional gates and dependencies when a circuit is compiled for a particular device topology.

Q-TRACE examines these effects through controlled experiments involving:

- Four transpiler optimization levels: 0, 1, 2, and 3.
- Two coupling topologies: Linear and Fully Connected.
- A fixed four-qubit QAOA Max-Cut circuit.
- A fixed target basis of `['u', 'cx']`.
- Repeated compilation trials to measure runtime variability.
- Structural resource analysis and Pareto-frontier evaluation.

The aim is to understand how compilation settings affect the measured circuit resource profile and how the preferred setting depends on the resource objective.

## Research Objectives

1. Measure the structural changes introduced by quantum circuit transpilation.
2. Compare constrained Linear connectivity with an idealized Fully Connected topology.
3. Evaluate the effects of Qiskit optimization levels on gate count, circuit depth, and compilation time.
4. Distinguish basis-gate decomposition from connectivity-associated routing overhead.
5. Analyze trade-offs between two-qubit gates, circuit depth, and classical compilation runtime.
6. Identify Pareto-optimal configurations for different resource objectives.
7. Establish a reproducible experimental workflow for compilation-aware quantum resource estimation.

## Research Questions

This project investigates the following questions:

1. How does physical qubit connectivity affect the compiled resource requirements of a fixed quantum circuit?
2. How do Qiskit optimization levels change one-qubit gate count, two-qubit gate count, and circuit depth?
3. Does a higher optimization level necessarily reduce the resources required by a compiled circuit?
4. How much classical compilation time is associated with different optimization settings?
5. Which configurations are Pareto-optimal when multiple resource objectives are considered?
6. How should compilation choices be evaluated when the target connectivity is fixed?

---

## Benchmark and Experimental Setup

### QAOA Max-Cut benchmark

The experiments use a Quantum Approximate Optimization Algorithm (QAOA) circuit for the unweighted four-vertex cycle graph \(C_4\).

The graph is defined by:

\[
V=\{0,1,2,3\}
\]

\[
E=\{(0,1),(1,2),(2,3),(3,0)\}
\]

The graph contains four vertices and four edges. Under Linear connectivity, the interaction between qubits 3 and 0 is non-local, making this benchmark useful for examining the effects of connectivity constraints.

### QAOA parameters

| Parameter | Value |
|---|---|
| Number of qubits | 4 |
| Graph | Four-vertex cycle, \(C_4\) |
| QAOA depth | \(p=1\) |
| Cost parameter | \(\gamma=0.5\) |
| Mixer parameter | \(\beta=0.25\) |
| Target basis | `['u', 'cx']` |
| Initial layout | Identity |
| Transpiler seed | `2026` |

The variational parameters are held fixed so that the experiments focus on compilation behavior rather than parameter optimization.

### Cost Hamiltonian

For the Max-Cut problem, the cost Hamiltonian is represented as:

\[
H_C=\sum_{(u,v)\in E}\frac{I-Z_uZ_v}{2}
\]

The corresponding cost unitary is:

\[
U_C(\gamma)=e^{-i\gamma H_C}
\]

The mixer unitary is:

\[
U_M(\beta)=\prod_{v\in V}R_X(2\beta,v)
\]

These operators form the QAOA circuit used in the experiments.

### Coupling topologies

**Linear topology**

The physical coupling map is:

\[
0-1-2-3
\]

Only neighboring qubits are directly connected. Non-local interactions may require routing and additional circuit operations.

**Fully Connected topology**

Every pair of physical qubits is connected, corresponding to the complete graph \(K_4\).

This is an **idealized reference topology** used to study compilation without connectivity restrictions. It is not a claim that a particular physical quantum processor provides fully connected hardware.

---

## Experimental Variables

The experiments vary two principal factors.

### 1. Transpiler optimization level

| Level | Purpose |
|---:|---|
| 0 | Baseline compilation with minimal optimization |
| 1 | Light optimization |
| 2 | More aggressive optimization |
| 3 | Highest preset optimization level tested |

The exact transformations depend on the Qiskit version and the selected target configuration.

### 2. Coupling topology

| Topology | Description |
|---|---|
| Linear | Restricted nearest-neighbor connectivity |
| Fully Connected | Idealized connectivity without routing restrictions |

### Controlled factors

The target basis, initial layout, QAOA parameters, and transpiler seed are held fixed across the primary experiments.

Each combination of topology and optimization level is measured over five timing trials.

The primary experiment matrix contains:

\[
2\text{ topologies}\times4\text{ levels}\times5\text{ trials}=40\text{ rows}
\]

The primary dataset is stored in `results/qtrace_results.csv`.

---

## Metrics

Q-TRACE records structural metrics and classical compilation runtime.

| Metric | Description |
|---|---|
| `gate_count_1q` | Number of one-qubit gates |
| `gate_count_2q` | Number of two-qubit gates |
| `circuit_depth` | Gate-only circuit depth |
| `total_ops` | Total operations recorded in the compiled circuit, including measurements |
| `explicit_swap_count` | Number of explicit SWAP instructions |
| `measurement_count` | Number of measurement operations |
| Transpilation time | Wall-clock time spent in the Qiskit `transpile()` invocation |

### Metric conventions

- Measurements, barriers, delays, and compiler directives are excluded from the one-qubit and two-qubit gate counts and gate-only depth.
- Measurement operations are recorded separately.
- `total_ops` includes measurement operations, so it is not necessarily equal to the sum of the one-qubit and two-qubit gate counts.
- The target basis `['u', 'cx']` represents two-qubit interactions using CX gates.
- Routing SWAP operations may be decomposed into CX gates. Consequently, a zero explicit SWAP count does not establish that no routing overhead occurred.
- Transpilation time represents classical compilation latency, not quantum execution time.

---

## Key Results

The following measurements come from the primary experiment dataset.

### Structural comparison

| Configuration | Topology | Optimization level | 1Q gates | 2Q gates | Gate-only depth | Total operations | Median time |
|---|---|---:|---:|---:|---:|---:|---:|
| FC-Opt0 | Fully Connected | 0 | 12 | 8 | 14 | 24 | 8.74 ms |
| FC-Opt1 | Fully Connected | 1 | 12 | 8 | 14 | 24 | 13.37 ms |
| FC-Opt2 | Fully Connected | 2 | 12 | 8 | 14 | 24 | 14.17 ms |
| FC-Opt3 | Fully Connected | 3 | 12 | 8 | 14 | 24 | 18.24 ms |
| LI-Opt0 | Linear | 0 | 12 | 14 | 18 | 30 | 13.24 ms |
| LI-Opt1 | Linear | 1 | 12 | 14 | 18 | 30 | 14.22 ms |
| LI-Opt2 | Linear | 2 | 17 | 12 | 18 | 33 | 20.28 ms |
| LI-Opt3 | Linear | 3 | 17 | 12 | 18 | 33 | 20.50 ms |

*The logical baseline contains 8 one-qubit gates, 4 two-qubit \(R_{ZZ}\) gates, gate-only depth 6, and 4 measurement operations, giving 16 total operations under the project's counting convention.*

### Finding 1: Connectivity affects gate count and depth

At Optimization Levels 0 and 1:

- Fully Connected topology uses 8 CX gates.
- Linear topology uses 14 CX gates.
- The Linear topology therefore has a **75% higher two-qubit gate count**.

At Optimization Levels 2 and 3:

- Fully Connected topology uses 8 CX gates.
- Linear topology uses 12 CX gates.
- The Linear topology therefore has a **50% higher two-qubit gate count**.

Gate-only depth increases from 14 to 18 across all four optimization levels when comparing Linear with Fully Connected connectivity, a **28.6% increase**.

### Finding 2: Higher optimization does not always reduce all resources

On Fully Connected connectivity, all four optimization levels produce identical structural metrics in the primary dataset.

The median compilation time nevertheless increases from 8.74 ms at Level 0 to 18.24 ms at Level 3.

On Linear connectivity, Levels 2 and 3 reduce the CX count from 14 to 12, a 14.3% reduction. However, the one-qubit gate count increases from 12 to 17, total operations increase from 30 to 33, and gate-only depth remains 18.

### Finding 3: Basis decomposition and routing are different

The logical baseline contains four \(R_{ZZ}\) interactions. In the target basis `['u', 'cx']`, each \(R_{ZZ}\) interaction is decomposed into two CX gates and local rotations.

Therefore, eight CX gates are required after this basis translation even under Fully Connected connectivity.

The additional CX gates observed under Linear connectivity are associated with compiling under the restricted coupling map. Because routing SWAP operations can be decomposed into CX instructions, explicit SWAP counts alone do not capture the entire routing cost.

### Finding 4: Compilation time depends on optimization level

In the primary dataset, the median compilation times range from:

- **8.74 ms** for Fully Connected Opt 0.
- **20.50 ms** for Linear Opt 3.

These results are specific to the tested benchmark, software versions, and execution environment.

---

## Pareto Analysis

Pareto analysis identifies configurations that cannot be improved in one objective without worsening at least one other objective, within the evaluated set.

Q-TRACE evaluates multiple objective spaces rather than assuming one configuration is universally best.

### Global multi-objective comparison

The primary analysis considers:

1. Two-qubit gate count.
2. Gate-only circuit depth.
3. Median transpilation time.

Within the primary dataset, `fully_connected / Opt 0` dominates the other configurations under these three objectives.

Its measured resource profile is:

- 8 two-qubit gates.
- Gate-only depth 14.
- Median transpilation time 8.74 ms.

This conclusion includes the idealized Fully Connected topology and should not be interpreted as a claim that this topology is available on every physical processor.

### Within-Linear comparison

When the topology is restricted to Linear, the results reveal a trade-off.

| Configuration | CX gates | Depth | Median compilation time | Pareto status |
|---|---:|---:|---:|---|
| Linear Opt 0 | 14 | 18 | 13.24 ms | Pareto-optimal |
| Linear Opt 1 | 14 | 18 | 14.22 ms | Dominated |
| Linear Opt 2 | 12 | 18 | 20.28 ms | Pareto-optimal |
| Linear Opt 3 | 12 | 18 | 20.50 ms | Dominated |

**Interpretation:**

- Linear Opt 0 is preferred when minimizing median classical compilation time.
- Linear Opt 2 is preferred when minimizing the two-qubit gate count.
- Linear Opt 1 is dominated by Linear Opt 0.
- Linear Opt 3 is dominated by Linear Opt 2.

The preferred configuration therefore depends on the objective being prioritized.

---

## Repository Structure

The repository is organized into experiment, analysis, test, and result directories.

```text
q-trace/
├── analysis/
│   ├── data_loader.py
│   ├── pareto.py
│   ├── tradeoff_analysis.py
│   ├── plot_integrated.py
│   └── INTEGRATED_ANALYSIS.md
├── experiments/
│   └── optimization/
│       ├── plot_optimization.py
│       └── OPTIMIZATION_FINDINGS.md
├── plots/
│   └── analysis/
├── results/
│   ├── qtrace_results.csv
│   ├── optimization_experiments.csv
│   ├── connectivity_experiments.csv
│   └── tradeoff_analysis.md
├── tests/
│   └── test_pareto_analysis.py
├── src/
├── requirements.txt
└── README.md
```

This is a high-level representation of the project structure. Additional files, experiment scripts, tests, and generated artifacts may exist in the repository.

### Main components

- **`src/`** — Core experiment and validation code.
- **`experiments/optimization/`** — Optimization-level experiments, plots, and findings.
- **`results/`** — Recorded experiment data and generated analysis reports.
- **`analysis/data_loader.py`** — Loads and audits experimental datasets.
- **`analysis/pareto.py`** — Implements Pareto analysis.
- **`analysis/tradeoff_analysis.py`** — Performs integrated trade-off analysis and generates a report.
- **`analysis/plot_integrated.py`** — Generates integrated visualization outputs.
- **`analysis/INTEGRATED_ANALYSIS.md`** — Integrated resource trade-off and Pareto analysis report.
- **`tests/`** — Automated tests for the analysis code.

---

## Technology Stack

| Technology | Role |
|---|---|
| Python | Experiment implementation and analysis |
| Qiskit | Quantum circuit construction and transpilation |
| NumPy | Numerical operations |
| pandas | Experimental data processing |
| Matplotlib | Visualization |
| pytest | Automated testing |
| Git and GitHub | Version control and collaborative development |

---

## Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Git.
- Access to the Q-TRACE repository.
- Dependencies specified in `requirements.txt`.

### 1. Clone the repository

```bash
git clone https://github.com/mahimagalla/q-trace.git
cd q-trace
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows CMD:**

```cmd
.venv\Scripts\activate
```

**macOS or Linux:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest matplotlib numpy
```

If the repository already includes a dependency in `requirements.txt`, installing it again is unnecessary. The commands above ensure the analysis and test dependencies are available.

### 5. Verify the environment

```bash
python --version
python -m pip show qiskit
python -m pytest -v
```

The experiment results discussed in this README were obtained using Qiskit 2.5.2 and Python 3.14.4 for the primary dataset. Different environments may produce different compilation timings.

---

## Running the Experiments

The exact experiment commands depend on the scripts present in the repository. The following commands describe the established analysis and validation entry points.

### Validate the QAOA benchmark

```bash
python -m src.validate_qaoa
```

This command was used to validate the QAOA benchmark and its measured output.

### Generate the trade-off report

From the repository root:

```bash
python -m analysis.tradeoff_analysis --csv results/qtrace_results.csv --name "Q-TRACE Primary Experiments" --output results/tradeoff_analysis.md
```

This analyzes the primary dataset and generates the trade-off report.

### Generate integrated plots

```bash
python -m analysis.plot_integrated
```

The integrated plots are written to `plots/analysis/`.

**Important:** Experiment and plotting scripts may regenerate tracked CSVs, Markdown reports, or images. Review the resulting changes before committing them.

---

## Integrated Analysis

The integrated analysis combines structural measurements, timing data, and Pareto comparisons to evaluate the compilation trade-offs.

### Main outputs

**Report:** `analysis/INTEGRATED_ANALYSIS.md`

This report covers:

- Benchmark and transpilation methodology.
- Cross-dataset compatibility considerations.
- Structural resource metrics.
- Basis decomposition and connectivity-associated overhead.
- Optimization-level comparisons.
- Pareto-frontier analysis.
- Visualizations and research limitations.

**Plots:** `plots/analysis/`

The analysis generates the following figures:

1. `2q_gates_vs_transpilation_time.png`
2. `depth_vs_2q_gates.png`
3. `pareto_frontier.png`
4. `routing_overhead_integrated.png`

**Trade-off report:** `results/tradeoff_analysis.md`

This file contains the generated trade-off analysis for the selected primary dataset.

---

## Validation and Tests

Run the full test suite from the repository root:

```bash
python -m pytest -v
```

The latest recorded validation of the repository after the integrated analysis merge reported:

```text
28 passed
```

This is a previously observed result, not a guarantee for every environment or future revision.

To run the Pareto-analysis tests specifically:

```bash
python -m pytest tests/test_pareto_analysis.py -v
```

The integrated analysis should be validated after code changes, particularly changes to metric extraction, dataset compatibility checks, Pareto classification, or report generation.

---

## Interpretation and Limitations

The results should be interpreted within the scope of the experiment.

### Benchmark scope

The experiments use a single four-qubit QAOA Max-Cut benchmark on \(C_4\) with \(p=1\) and fixed parameters. The findings should not be generalized automatically to larger circuits, different algorithms, or higher QAOA depths.

### Idealized connectivity

Fully Connected connectivity is a comparison reference. Actual processors may impose sparse coupling constraints and additional hardware-specific costs.

### Timing variability

Each configuration was measured over five trials. This sample size is useful for exploratory comparison but does not establish definitive runtime distributions.

One connectivity-dataset trial recorded a runtime of approximately 4.58 seconds. Its cause was not established, so it should not be silently treated as a confirmed measurement error.

### Structural metrics vs. physical performance

Gate count and circuit depth are structural resource indicators. They do not fully characterize physical execution cost, which can depend on:

- Native gate implementations.
- Calibrated error rates.
- Gate durations and scheduling.
- Decoherence and crosstalk.
- Device-specific connectivity and control constraints.

This project does not establish a measured improvement in hardware fidelity from reducing the CX count. Such a conclusion would require hardware execution or an appropriate noise-model evaluation.

### Cross-environment comparisons

The primary and supporting datasets include different Qiskit and Python versions. Structural results may agree while timing measurements remain environment-dependent. Timing comparisons should retain their software and execution context.

---

## Team Contributions

The project is developed by **EIGEN5** as part of IEG 313: Quantum Computing for Engineers.

| Team member | Student identifier | Main responsibility |
|---|---|---|
| Galla Mahima Suharshitha | `2024BCS0051` | Q-TRACE experiment and analysis contributions |
| Chandrana Hanisha | `2024BCD0004` | Project experimentation and research contributions |
| K. Prerana | `2024BCS0048` | Project experimentation and research contributions |
| Mounika Kolluru | `2024BCS0259` | Integrated analysis and related contributions |
| Shaik Shaheeq | `2024BCS0109` | Integrated analysis, visualization, and trade-off analysis |

The table summarizes broad areas of involvement. Refer to the repository's commit history and pull requests for the exact implementation history of individual contributions.

---

## Reproducibility

To reproduce the integrated analysis:

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install the project dependencies.
4. Confirm the availability of the recorded experiment CSV files.
5. Run the automated tests.
6. Run the integrated trade-off analysis.
7. Generate the integrated plots.
8. Compare generated artifacts with the committed versions.

Use the primary dataset, `results/qtrace_results.csv`, for the main resource and Pareto comparisons. Treat supporting datasets as separate experimental contexts when software versions or environments differ.

For reproducible comparisons, record the Python version, Qiskit version, target basis, coupling map, initial layout, transpiler seed, optimization level, and timing protocol.

---

## License

The repository license governs the use, modification, and redistribution of this project.

Check the repository's `LICENSE` file for the applicable terms. If no license file exists, the project should not be assumed to be open source solely because it is hosted on GitHub.
