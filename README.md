# Q-TRACE: Compilation-Aware Resource Estimation for NISQ Quantum Circuits

**Team:** EIGEN5  
**Course:** IEG 313 — Quantum Computing for Engineers  
**Institution:** IIIT Kottayam

Q-TRACE (**Quantum Transpilation and Resource Analysis under Connectivity Effects**) investigates how quantum circuit transpilation choices affect gate resources, circuit depth, and classical compilation time in Noisy Intermediate-Scale Quantum (NISQ) computing.

The project uses a four-qubit Quantum Approximate Optimization Algorithm (QAOA) Max-Cut benchmark implemented with Qiskit. It compares transpiler optimization levels and qubit coupling topologies to understand how compilation settings influence circuit structure.

## Research Objectives

- Measure structural changes introduced by quantum circuit transpilation.
- Compare Linear and idealized Fully Connected coupling topologies.
- Evaluate the effects of Qiskit optimization levels 0–3.
- Distinguish basis-gate decomposition from connectivity-associated routing overhead.
- Analyze trade-offs between two-qubit gate count, circuit depth, and classical compilation time.
- Identify Pareto-optimal compilation configurations.
- Maintain a reproducible workflow for compilation-aware resource estimation.

## Research Questions

1. How does qubit connectivity affect compiled circuit resources?
2. How do optimization levels change gate counts and circuit depth?
3. Does higher optimization always produce a better circuit?
4. What compilation-time costs are associated with different optimization levels?
5. Which configurations are Pareto-optimal under different resource objectives?

## Benchmark and Experimental Setup

### QAOA Max-Cut benchmark

The benchmark is Max-Cut on an unweighted four-vertex cycle graph \(C_4\).

\[
V=\{0,1,2,3\}
\]

\[
E=\{(0,1),(1,2),(2,3),(3,0)\}
\]

The circuit uses QAOA depth \(p=1\), with fixed parameters \(\gamma=0.5\) and \(\beta=0.25\). These parameters remain constant so that the experiments focus on compilation behavior rather than variational parameter optimization.

The cost Hamiltonian is:

\[
H_C=\sum_{(u,v)\in E}\frac{I-Z_uZ_v}{2}
\]

The mixer unitary is:

\[
U_M(\beta)=\prod_{v\in V}R_X(2\beta,v)
\]

### Experimental configuration

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
| Optimization levels | 0, 1, 2, 3 |
| Timing trials per configuration | 5 |

### Coupling topologies

**Linear:** A nearest-neighbor chain, \(0-1-2-3\). Non-local interactions may require additional routing operations.

**Fully Connected:** A complete graph \(K_4\), used as an idealized reference without connectivity restrictions. It is not a claim about the topology of any particular physical processor.

The experiment matrix contains:

\[
2\text{ topologies}\times4\text{ optimization levels}\times5\text{ trials}=40
\]

The primary dataset is `results/qtrace_results.csv`.

## Metrics

Q-TRACE records the following metrics:

| Metric | Meaning |
|---|---|
| `gate_count_1q` | Number of one-qubit gates |
| `gate_count_2q` | Number of two-qubit gates |
| `circuit_depth` | Gate-only circuit depth |
| `total_ops` | Total recorded circuit operations, including measurements |
| `explicit_swap_count` | Number of explicit SWAP instructions |
| `measurement_count` | Number of measurement operations |
| Transpilation time | Classical wall-clock time for Qiskit's `transpile()` invocation |

Measurements, barriers, delays, and compiler directives are excluded from the one-qubit and two-qubit gate counts and gate-only depth. Measurements are recorded separately.

The target basis `['u', 'cx']` represents two-qubit interactions using CX gates. Routing SWAPs may be decomposed into CX gates, so a zero explicit SWAP count does not establish that no routing overhead occurred.

## Key Results

### Primary dataset results

| Configuration | Topology | Opt. level | 1Q gates | 2Q gates | Depth | Total ops | Median time |
|---|---|---:|---:|---:|---:|---:|---:|
| FC-Opt0 | Fully Connected | 0 | 12 | 8 | 14 | 24 | 8.74 ms |
| FC-Opt1 | Fully Connected | 1 | 12 | 8 | 14 | 24 | 13.37 ms |
| FC-Opt2 | Fully Connected | 2 | 12 | 8 | 14 | 24 | 14.17 ms |
| FC-Opt3 | Fully Connected | 3 | 12 | 8 | 14 | 24 | 18.24 ms |
| LI-Opt0 | Linear | 0 | 12 | 14 | 18 | 30 | 13.24 ms |
| LI-Opt1 | Linear | 1 | 12 | 14 | 18 | 30 | 14.22 ms |
| LI-Opt2 | Linear | 2 | 17 | 12 | 18 | 33 | 20.28 ms |
| LI-Opt3 | Linear | 3 | 17 | 12 | 18 | 33 | 20.50 ms |

The logical baseline has 8 one-qubit gates, 4 two-qubit \(R_{ZZ}\) gates, gate-only depth 6, and 4 measurement operations, giving 16 total operations under the project's counting convention.

### Finding 1: Connectivity affects resource requirements

At optimization levels 0 and 1, Linear connectivity uses 14 CX gates compared with 8 on Fully Connected connectivity, a 75% increase.

At levels 2 and 3, Linear connectivity uses 12 CX gates compared with 8, a 50% increase.

Gate-only depth increases from 14 to 18 for Linear connectivity at all four optimization levels, a 28.6% increase.

### Finding 2: Higher optimization does not always reduce every metric

On Fully Connected connectivity, all four optimization levels produce identical structural metrics in the primary dataset. However, median transpilation time increases from 8.74 ms at level 0 to 18.24 ms at level 3.

On Linear connectivity, levels 2 and 3 reduce the CX count from 14 to 12, a 14.3% reduction. This comes with five additional one-qubit gates, an increase in total operations from 30 to 33, and no reduction in gate-only depth.

### Finding 3: Basis decomposition differs from routing

The logical circuit contains four \(R_{ZZ}\) interactions. In the target basis `['u', 'cx']`, each interaction is decomposed into two CX gates and local rotations. Thus, eight CX gates are required after basis translation even on the idealized Fully Connected topology.

Additional CX gates on Linear connectivity are associated with compiling under a restricted coupling map. Explicit SWAP counts alone do not capture the entire routing cost.

### Finding 4: Compilation time is configuration-dependent

The measured median compilation times range from 8.74 ms for Fully Connected Opt 0 to 20.50 ms for Linear Opt 3. These are results for the tested benchmark and environment, not universal runtime guarantees.

## Pareto Analysis

Pareto analysis identifies configurations that are not dominated by another configuration across the selected objectives.

### Global comparison

The primary analysis considers two-qubit gate count, gate-only depth, and median transpilation time. In the primary dataset, `fully_connected / Opt 0` dominates the other configurations under these three objectives.

Its measured profile is:

- 8 two-qubit gates.
- Gate-only depth 14.
- Median transpilation time 8.74 ms.

This result includes the idealized Fully Connected topology and does not imply that such connectivity is available on every physical processor.

### Within-Linear comparison

| Configuration | CX gates | Depth | Median time | Pareto status |
|---|---:|---:|---:|---|
| Linear Opt 0 | 14 | 18 | 13.24 ms | Pareto-optimal |
| Linear Opt 1 | 14 | 18 | 14.22 ms | Dominated |
| Linear Opt 2 | 12 | 18 | 20.28 ms | Pareto-optimal |
| Linear Opt 3 | 12 | 18 | 20.50 ms | Dominated |

Within Linear connectivity, Opt 0 is preferred for lower median compilation time, while Opt 2 is preferred for lower CX count. The best choice depends on which resource objective matters most.

## Repository Structure

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

This is a high-level view of the main project components, not an exhaustive listing of every file.

## Technology Stack

- **Python** — experiment implementation and analysis.
- **Qiskit** — quantum circuit construction and transpilation.
- **pandas and NumPy** — data handling and numerical operations.
- **Matplotlib** — visualization.
- **pytest** — automated testing.
- **Git and GitHub** — version control and collaboration.

## Installation and Setup

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

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest matplotlib numpy
```

### 5. Verify the environment

```bash
python --version
python -m pip show qiskit
python -m pytest -v
```

The primary dataset was produced using Qiskit 2.5.2 and Python 3.14.4. Compilation timings can differ across environments.

## Running the Analysis

### Validate the QAOA benchmark

```bash
python -m src.validate_qaoa
```

### Generate the trade-off report

```bash
python -m analysis.tradeoff_analysis --csv results/qtrace_results.csv --name "Q-TRACE Primary Experiments" --output results/tradeoff_analysis.md
```

### Generate integrated plots

```bash
python -m analysis.plot_integrated
```

The integrated plots are saved in `plots/analysis/`:

1. `2q_gates_vs_transpilation_time.png`
2. `depth_vs_2q_gates.png`
3. `pareto_frontier.png`
4. `routing_overhead_integrated.png`

Experiment and plotting scripts may regenerate tracked files. Avoid rerunning them if you only intend to edit documentation.

## Validation and Tests

Run the complete test suite:

```bash
python -m pytest -v
```

The latest recorded validation after the integrated analysis merge reported **28 passed tests**. This is a previously observed result, not a guarantee for every future revision or environment.

To run the Pareto-analysis tests specifically:

```bash
python -m pytest tests/test_pareto_analysis.py -v
```

## Limitations

- The study uses a single four-qubit QAOA Max-Cut benchmark at \(p=1\); findings should not be generalized automatically to larger circuits or other algorithms.
- Fully Connected connectivity is an idealized reference, not a universal theoretical lower bound or a representation of all physical processors.
- Five timing trials per configuration provide exploratory evidence, not definitive runtime distributions.
- Gate counts and depth do not fully model hardware fidelity, pulse duration, scheduling, crosstalk, or calibrated error rates.
- This study does not establish a physical error-rate or fidelity improvement from reducing the CX count.
- Cross-dataset timing comparisons must account for software-version and execution-environment differences.

## Team Contributions

**Team EIGEN5 — IEG 313: Quantum Computing for Engineers**

| Team member | Student identifier | Main responsibility |
|---|---|---|
| Galla Mahima Suharshitha | `2024BCS0051` | Q-TRACE experiment and analysis contributions |
| Chandrana Hanisha | `2024BCD0004` | Project experimentation and research contributions |
| K. Prerana | `2024BCS0048` | Project experimentation and research contributions |
| Mounika Kolluru | `2024BCS0259` | Integrated analysis and related contributions |
| Shaik Shaheeq | `2024BCS0109` | Integrated analysis, visualization, and trade-off analysis |

This table summarizes broad project involvement. The repository's commits and pull requests provide the detailed implementation history.

## Reproducibility

To reproduce the integrated analysis:

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install the project dependencies.
4. Use `results/qtrace_results.csv` as the primary dataset.
5. Run the test suite.
6. Run the trade-off analysis and integrated plotting commands.
7. Record any changes to generated outputs before committing them.

For comparable experiments, record the Python and Qiskit versions, target basis, coupling map, initial layout, transpiler seed, optimization level, and timing protocol.

## License

This repository does not include a `LICENSE` file, so no project license is declared here. Do not assume open-source reuse permission solely because the repository is hosted on GitHub.
