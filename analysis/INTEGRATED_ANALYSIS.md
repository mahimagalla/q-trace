# Integrated Resource Trade-off and Pareto Analysis

**Project:** Q-TRACE (Compilation-Aware Resource Estimation for NISQ Quantum Circuits)  
**Team:** EIGEN5 (IEG 313: Quantum Computing for Engineers)  
**Author:** Shaik Shaheeq (Member 5 — Integrated Analysis, Visualization, and Trade-offs)  
**Date:** October 2026  
**Status:** Validated Research Findings Report

---

## Executive Summary

This report presents the integrated findings of the Q-TRACE research study, combining empirical measurements across transpiler optimization levels 0–3 and two qubit coupling topologies: Linear and idealized Fully Connected. The analysis evaluates compilation-aware resource requirements for a fixed four-qubit Quantum Approximate Optimization Algorithm (QAOA) Max-Cut benchmark at depth \(p=1\).

The study examines trade-offs among two-qubit gate count, gate-only circuit depth, one-qubit gate count, and classical transpilation time. It uses repeated compilation trials, cross-dataset auditing, and multi-objective Pareto analysis.

### Key measured insights

1. **Connectivity-associated gate overhead:** Linear connectivity produces a 75.0% increase in two-qubit gate count at optimization levels 0–1 (14 CX vs. 8 CX) and a 50.0% increase at levels 2–3 (12 CX vs. 8 CX). Gate-only depth increases by 28.6% (18 vs. 14).

2. **Basis decomposition versus routing:** The logical baseline contains four two-qubit \(R_{ZZ}\) gates and eight single-qubit gates. Translating the circuit to `['u', 'cx']` decomposes each \(R_{ZZ}\) interaction into two CX gates and local rotations. This results in eight CX gates even with Fully Connected connectivity.

3. **Two-qubit versus one-qubit gate trade-off:** On Linear connectivity, optimization levels 2 and 3 reduce the CX count from 14 to 12, a 14.3% reduction. The one-qubit gate count increases from 12 to 17, while gate-only depth remains 18.

4. **Pareto analysis:** In the primary dataset, Fully Connected Opt 0 dominates the other configurations across two-qubit gate count, gate-only depth, and median transpilation time. When analysis is restricted to Linear connectivity, Opt 0 and Opt 2 are Pareto-optimal because they offer different trade-offs between compilation time and CX count.

These findings apply to the evaluated benchmark and experimental environment; they are not universal claims about all quantum circuits or physical processors.

---

## 1. Experimental Methodology and Benchmark Setup

The experiment evaluates how Qiskit transpilation settings change circuit resource profiles under controlled conditions.

### 1.1 Benchmark specification

- **Problem:** Max-Cut on an unweighted four-vertex cycle graph \(C_4\).
- **Graph edges:**

  \[
  E=\{(0,1),(1,2),(2,3),(3,0)\}
  \]

- **QAOA depth:** \(p=1\).
- **Cost parameter:** \(\gamma=0.5\).
- **Mixer parameter:** \(\beta=0.25\).
- **Purpose:** Isolate compilation behavior by keeping the benchmark and variational parameters fixed.

The cost Hamiltonian is:

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

The edge \((3,0)\) is non-local on a linear chain \(0-1-2-3\), making the benchmark useful for examining connectivity-associated compilation costs.

### 1.2 Transpilation matrix and controlled factors

| Experimental factor | Value / protocol | Methodological rationale |
|---|---|---|
| Optimization levels | `0, 1, 2, 3` | Compares Qiskit's preset transpilation optimization levels. |
| Linear topology | `[(0,1), (1,2), (2,3)]`, bidirectional | Represents nearest-neighbor coupling. |
| Fully Connected topology | Complete graph \(K_4\), bidirectional | Provides an idealized reference without connectivity restrictions. |
| Target basis | `['u', 'cx']` | Maintains a consistent gate representation across topologies. |
| Initial layout | Identity | Keeps the initial qubit mapping fixed. |
| Transpiler seed | `2026` | Controls the configured transpiler seed across repetitions. |
| Repeated trials | Five per configuration | Samples observed classical compilation-time variability. |
| Scheduling | Off / not requested | Pulse scheduling and idle-time analysis are excluded. |

The primary experiment matrix contains:

\[
2\times4\times5=40\text{ compiled trials}
\]

### 1.3 Metric counting conventions

The analysis follows these conventions:

- **One-qubit and two-qubit gate counts:** Measurement operations, barriers, delays, and compiler directives are excluded.
- **Gate-only circuit depth:** Measurements, barriers, delays, and compiler directives are excluded from the depth calculation.
- **Measurements:** Recorded separately in `measurement_count`.
- **Total operations:** `total_ops` includes the recorded circuit operations, including measurements. It is distinct from the sum of the one-qubit and two-qubit gate counts.
- **Gate arity:** Two-qubit gates are counted by operator arity rather than gate name alone. With basis `['u', 'cx']`, the two-qubit operations are CX gates.
- **Transpilation time:** Measured as wall-clock time around the Qiskit `transpile()` invocation, excluding circuit creation, metric extraction, and disk I/O.

---

## 2. Cross-Dataset Audit and Environmental Compatibility

Three experimental CSV outputs were audited using [`analysis/data_loader.py`](data_loader.py).

| Dataset path | Rows | Qiskit version | Python version | Primary purpose |
|---|---:|---|---|---|
| `results/qtrace_results.csv` | 40 | `2.5.2` | `3.14.4` | Primary dataset: 8 configurations × 5 trials |
| `results/optimization_experiments.csv` | 40 | `2.5.2` | `3.14.4` | Dedicated optimization-level experiments |
| `results/connectivity_experiments.csv` | 41 | `2.5.1` | `3.14.2` | Connectivity experiments plus one untranspiled baseline record |

### Methodological rule on cross-environment data

The audit found consistent structural metrics for corresponding configurations across the datasets. However, classical compilation runtimes can be sensitive to software versions and execution environments.

The primary experiments use Qiskit `2.5.2` and Python `3.14.4`. The connectivity dataset uses Qiskit `2.5.1` and Python `3.14.2`.

**Transpilation timings from different environments should not be pooled into a single timing distribution.** Structural comparisons can be made when configurations and counting conventions match, but timing comparisons must retain their environment context.

The main quantitative results and Pareto frontiers in this report therefore use `results/qtrace_results.csv`. Supporting datasets provide additional evidence but are treated separately where environmental differences affect interpretation.

---

## 3. Quantitative Results and Structural Invariants

The table below summarizes the structural metrics and classical transpilation times from the primary dataset, alongside the logical baseline recorded in the connectivity dataset.

| Configuration | Topology | Opt. level | 1Q gates (`u`) | 2Q gates (`cx`) | Gate-only depth | Total ops | Explicit SWAPs | Median time (ms) | Observed min–max (ms) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Baseline (Logical)** | `baseline` | N/A | 8 | 4 | 6 | **16** | 0 | N/A | N/A |
| **FC-Opt0** | `fully_connected` | 0 | 12 | 8 | 14 | 24 | 0 | **8.74** | 6.67–13.26 |
| **FC-Opt1** | `fully_connected` | 1 | 12 | 8 | 14 | 24 | 0 | 13.37 | 11.80–15.65 |
| **FC-Opt2** | `fully_connected` | 2 | 12 | 8 | 14 | 24 | 0 | 14.17 | 13.53–20.37 |
| **FC-Opt3** | `fully_connected` | 3 | 12 | 8 | 14 | 24 | 0 | 18.24 | 14.44–21.48 |
| **LI-Opt0** | `linear` | 0 | 12 | 14 | 18 | 30 | 0 | **13.24** | 8.94–49.88 |
| **LI-Opt1** | `linear` | 1 | 12 | 14 | 18 | 30 | 0 | 14.22 | 12.46–16.77 |
| **LI-Opt2** | `linear` | 2 | 17 | 12 | 18 | 33 | 0 | **20.28** | 17.55–22.94 |
| **LI-Opt3** | `linear` | 3 | 17 | 12 | 18 | 33 | 0 | 20.50 | 18.18–21.72 |

*Note: `total_ops` includes measurement operations. The baseline has 16 total operations, including 4 measurements. One-qubit and two-qubit gate counts and gate-only circuit depth exclude measurements, barriers, and directives.*

---

## 4. In-Depth Analysis of Research Questions

### 4.1 Decomposition versus routing overhead

A key distinction in NISQ compilation analysis is the difference between basis-decomposition overhead and connectivity-routing overhead.

#### 1. Logical baseline

The untranspiled QAOA circuit contains four single-qubit Hadamard gates, four two-qubit \(R_{ZZ}(-\gamma)\) gates, and four single-qubit \(R_X(2\beta)\) mixer gates.

Its logical resource counts are:

\[
\text{1Q gates}=8,\qquad
\text{2Q gates}=4,\qquad
\text{gate-only depth}=6
\]

The circuit also contains four measurement operations, giving 16 total operations under the counting convention used in this report.

#### 2. Basis-translation expansion

In the target basis `['u', 'cx']`, \(R_{ZZ}(\theta)\) is not a basis instruction. A standard decomposition is:

\[
R_{ZZ}(\theta)
=
CX(q_1,q_2)
(I\otimes R_Z(\theta))
CX(q_1,q_2)
\]

Each logical edge therefore requires two CX gates and local rotation operations. Across four graph edges:

\[
4\times2=8\text{ CX gates}
\]

This expansion occurs even with Fully Connected connectivity. The increase from four logical \(R_{ZZ}\) gates to eight CX gates is a basis-translation effect, not routing overhead by itself.

#### 3. SWAP decomposition and routing

On Linear connectivity, the logical edge \((3,0)\) is non-local. Compilation must account for this connectivity restriction.

In `results/qtrace_results.csv`, `explicit_swap_count` is zero across the compiled configurations. This does not establish that routing overhead is absent. Under the target basis `['u', 'cx']`, routing SWAPs can be decomposed into CX gates:

\[
SWAP(a,b)=CX(a,b)\,CX(b,a)\,CX(a,b)
\]

Routing-related overhead can therefore appear as additional CX gates and greater circuit depth rather than as explicit SWAP instructions.

### 4.2 Observed connectivity-associated overhead

The following table compares Linear and Fully Connected connectivity at the same optimization level.

| Optimization level | Metric | Fully Connected | Linear | Linear increase |
|---:|---|---:|---:|---:|
| **Level 0** | Two-qubit gates | 8 | 14 | **+75.0%** |
| | Gate-only depth | 14 | 18 | **+28.6%** |
| | Median transpilation time | 8.74 ms | 13.24 ms | +51.6% |
| **Level 1** | Two-qubit gates | 8 | 14 | **+75.0%** |
| | Gate-only depth | 14 | 18 | **+28.6%** |
| | Median transpilation time | 13.37 ms | 14.22 ms | +6.4% |
| **Level 2** | Two-qubit gates | 8 | 12 | **+50.0%** |
| | Gate-only depth | 14 | 18 | **+28.6%** |
| | Median transpilation time | 14.17 ms | 20.28 ms | +43.1% |
| **Level 3** | Two-qubit gates | 8 | 12 | **+50.0%** |
| | Gate-only depth | 14 | 18 | **+28.6%** |
| | Median transpilation time | 18.24 ms | 20.50 ms | +12.4% |

#### Key empirical observations

- **Entangling-gate inflation:** At levels 0 and 1, Linear connectivity uses six additional CX gates compared with Fully Connected connectivity, a 75.0% increase.
- **Depth expansion:** Gate-only depth increases from 14 to 18 at every optimization level, a 28.6% increase.
- **Transpilation-time differences:** Linear compilation has higher median transpilation time than Fully Connected compilation in these measurements. The observed increase ranges from 6.4% to 51.6%.

These are measured differences for the benchmark and environment; they are not universal runtime guarantees.

### 4.3 Optimization trade-off: two-qubit reduction versus one-qubit increase

#### Fully Connected topology

All four optimization levels produce identical structural metrics in the primary dataset:

\[
\text{1Q}=12,\quad
\text{2Q}=8,\quad
\text{depth}=14,\quad
\text{total operations}=24
\]

Median transpilation time increases from 8.74 ms at Opt 0 to 18.24 ms at Opt 3, an increase of approximately 108.7%, without reducing the measured gate counts or depth.

For this benchmark under idealized Fully Connected connectivity, Opt 0 is the fastest tested configuration while retaining the same structural metrics.

#### Linear topology

Opt 2 and Opt 3 reduce the CX count from 14 to 12, a 14.3% reduction relative to Opt 0 and Opt 1. The change comes with the following trade-offs:

- **Single-qubit gates:** Increase from 12 to 17, a 41.7% increase.
- **Total operations:** Increase from 30 to 33, a 10.0% increase.
- **Gate-only depth:** Remains 18.
- **Median transpilation time:** Increases from 13.24 ms at Opt 0 to 20.28 ms at Opt 2, approximately 53.2%.

#### Physical interpretation

Two-qubit gates can be important contributors to errors on NISQ hardware, but the magnitude of any reliability improvement depends on the target device, calibrated gate error rates, gate durations, and the compiled circuit.

This study measures structural resource counts and classical compilation time. It does not measure hardware execution fidelity or simulate a hardware noise model. Therefore, **a reduction of two CX gates is an observed structural improvement, but a corresponding reduction in physical error cannot be established from these measurements alone**.

---

## 5. Pareto-Frontier Analysis

Pareto optimality identifies configurations that cannot be improved in one objective without worsening at least one other objective, within the evaluated set.

### 5.1 Mathematical dominance definition

Let each compilation configuration \(C\) have an objective vector:

\[
M(C)=[m_1(C),m_2(C),\ldots,m_k(C)]
\]

All objectives in this report are minimized.

A configuration \(A\) Pareto-dominates configuration \(B\), written \(A\prec B\), if:

\[
\forall i,\quad m_i(A)\leq m_i(B)
\]

and:

\[
\exists j,\quad m_j(A)<m_j(B)
\]

A configuration is Pareto-optimal if no other configuration in the evaluated set dominates it.

### 5.2 Evaluated objective spaces

#### 1. Primary multi-objective space

**Objectives:** Two-qubit gates, gate-only depth, and median transpilation time.

- **Evaluated set:** All eight compiled configurations in `results/qtrace_results.csv`.
- **Global non-dominated frontier:**

  \[
  \{\text{FC-Opt0}\}
  \]

FC-Opt0 has eight two-qubit gates, depth 14, and median transpilation time 8.74 ms. It dominates the other configurations under these three objectives in the primary dataset.

This result includes idealized Fully Connected connectivity and does not imply that this topology is available on all physical processors.

#### 2. Structural objective space

**Objectives:** Two-qubit gate count and gate-only depth.

The non-dominated frontier is:

\[
\{\text{FC-Opt0},\text{FC-Opt1},\text{FC-Opt2},\text{FC-Opt3}\}
\]

All four Fully Connected configurations have the same objective vector, \((8,14)\). Identical vectors do not strictly dominate each other, so all four remain on the structural frontier.

The Linear configurations, with vectors \((14,18)\) and \((12,18)\), are dominated by \((8,14)\) when both topologies are included.

#### 3. Compilation trade-off space

**Objectives:** Two-qubit gate count and median transpilation time.

The non-dominated frontier is:

\[
\{\text{FC-Opt0}\}
\]

FC-Opt0 has the lowest two-qubit gate count and lowest median transpilation time in this primary dataset.

### 5.3 Within-topology Pareto frontier: Linear connectivity

When targeting a physical processor, its coupling topology is fixed. A circuit targeting a linear qubit chain cannot simply choose an idealized Fully Connected topology.

Restricting the Pareto analysis to the four Linear configurations reveals a trade-off between classical compilation time and two-qubit gate count.

| Linear configuration | 2Q gates | Gate-only depth | Median time | Pareto status | Engineering profile |
|---|---:|---:|---:|---|---|
| **Linear Opt 0** | 14 | 18 | **13.24 ms** | **Pareto-optimal** | **Fastest compilation:** Lowest median classical preprocessing time among the Linear configurations. |
| **Linear Opt 1** | 14 | 18 | 14.22 ms | Dominated | Dominated by Opt 0: equal gate count and depth, but slower compilation. |
| **Linear Opt 2** | **12** | 18 | 20.28 ms | **Pareto-optimal** | **Lowest 2Q gate count:** Reduces the CX count by two gates (−14.3%) compared with Opt 0, at the cost of a +53.2% median transpilation-time increase. |
| **Linear Opt 3** | 12 | 18 | 20.50 ms | Dominated | Dominated by Opt 2: equal gate count and depth, but slower compilation. |

The within-Linear Pareto frontier consists of **Opt 0 and Opt 2**. The preferred choice depends on whether minimizing compilation time or minimizing the two-qubit gate count is more important.

---

## 6. Generated Visualizations

The four figures are generated by [`analysis/plot_integrated.py`](plot_integrated.py) and saved in [`plots/analysis/`](../plots/analysis/).

### Figure 1: Two-qubit gates versus transpilation time

**File:** [`plots/analysis/2q_gates_vs_transpilation_time.png`](../plots/analysis/2q_gates_vs_transpilation_time.png)

- **Visual representation:** Scatter plot with asymmetric horizontal error bars showing the observed minimum and maximum transpilation times relative to the median across five trials.
- **Research takeaway:** Fully Connected configurations use eight CX gates, with median runtimes ranging from 8.74 ms at Opt 0 to 18.24 ms at Opt 3. Linear configurations transition from 14 CX gates at Opt 0–1 to 12 CX gates at Opt 2–3. Linear Opt 0 has an observed maximum runtime of 49.88 ms, demonstrating timing variability.

### Figure 2: Structural comparison — depth versus two-qubit gates

**File:** [`plots/analysis/depth_vs_2q_gates.png`](../plots/analysis/depth_vs_2q_gates.png)

- **Visual representation:** Gate-only depth plotted against two-qubit gate count, with identical coordinate pairs consolidated into cluster labels.
- **Research takeaway:** The results form three structural groups:
  1. Fully Connected compilation at \((8,14)\).
  2. Linear Opt 0 and Opt 1 at \((14,18)\).
  3. Linear Opt 2 and Opt 3 at \((12,18)\).

The plot illustrates that higher optimization reduces the CX count on Linear connectivity but does not reduce gate-only depth below 18 in this experiment.

### Figure 3: Multi-objective Pareto frontier

**File:** [`plots/analysis/pareto_frontier.png`](../plots/analysis/pareto_frontier.png)

- **Visual representation:** Displays dominated and non-dominated configurations and highlights `fully_connected / Opt 0`.
- **Research takeaway:** Idealized Fully Connected connectivity performs favorably across the measured resource objectives in this benchmark. Pareto classification depends on the selected objectives; a two-dimensional projection may not communicate dominance in the full three-objective space. The classification should be interpreted using the objective definitions in Section 5.

### Figure 4: Observed connectivity-associated overhead

**File:** [`plots/analysis/routing_overhead_integrated.png`](../plots/analysis/routing_overhead_integrated.png)

- **Visual representation:** Grouped bar chart showing percentage increases for Linear connectivity relative to Fully Connected connectivity at each optimization level.
- **Research takeaway:** Two-qubit gate overhead is +75.0% at levels 0–1 and +50.0% at levels 2–3. Gate-only depth overhead remains +28.6% across all four levels.

---

## 7. Scope, Methodological Precautions, and Limitations

### 7.1 Specific benchmark instance

The findings are derived from a single four-qubit QAOA Max-Cut benchmark on \(C_4\) at depth \(p=1\). They should not be generalized automatically to arbitrary quantum algorithms, larger graphs, higher QAOA depths, or unstructured circuits.

### 7.2 Idealized versus physical coupling

Fully Connected coupling is an idealized reference for comparing compilation without connectivity restrictions. **It is not a universal theoretical lower bound for all circuits or compilation strategies.** Commercial quantum processors have topology-specific coupling constraints, so these results are not measurements of physical hardware performance.

### 7.3 Timing sample size

Classical compilation runtimes were measured over five trials per configuration with a fixed transpiler seed (`2026`). Five trials provide exploratory evidence but do not establish definitive runtime distributions.

One trial in the connectivity dataset recorded a runtime of approximately 4.58 seconds. Its cause has not been established. It is reported as an observed outlier and should not be silently discarded or treated as a confirmed measurement error.

### 7.4 Classical compilation versus quantum execution

Transpilation time measures classical CPU wall-clock time during compilation. It does not measure quantum execution duration, pulse duration, coherence decay, or physical hardware error rates.

### 7.5 Software-version sensitivity

The datasets include Qiskit versions `2.5.1` and `2.5.2`, and Python versions `3.14.2` and `3.14.4`. Structural results may agree while timing results remain environment-dependent. Software versions and host environments should be recorded when comparing runtimes.

### 7.6 Gate counts are not a complete hardware cost model

Gate counts and gate-only depth do not capture all hardware costs. Actual execution can depend on native gate implementations, calibrated error rates, gate durations, scheduling, crosstalk, and device-specific properties.

This study does not establish that reducing the CX count improves hardware fidelity. Such a conclusion requires hardware execution or a suitable noise-model evaluation.

---

## 8. Reproducibility Instructions

Run the following commands from the repository root.

### Step 1: Environment setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows CMD:

```cmd
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the project requirements and analysis dependencies:

```bash
pip install -r requirements.txt
pip install pytest matplotlib numpy
```

### Step 2: Run unit tests

Run the Pareto analysis tests:

```bash
python -m pytest tests/test_pareto_analysis.py -v
```

The expected result for the corresponding test version is eight passing tests.

To run the full repository test suite:

```bash
python -m pytest -v
```

### Step 3: Generate the trade-off report

```bash
python -m analysis.tradeoff_analysis --csv results/qtrace_results.csv --name "Q-TRACE Primary Experiments" --output results/tradeoff_analysis.md
```

### Step 4: Generate integrated figures

```bash
python -m analysis.plot_integrated
```

Expected figure paths:

- `plots/analysis/2q_gates_vs_transpilation_time.png`
- `plots/analysis/depth_vs_2q_gates.png`
- `plots/analysis/pareto_frontier.png`
- `plots/analysis/routing_overhead_integrated.png`

**Reproducibility note:** These commands regenerate analysis outputs. Review generated changes before committing them, especially if the CSVs, reports, or figures are tracked in Git.

---

## 9. Conclusion

The Q-TRACE integrated resource trade-off analysis demonstrates that transpiler optimization and qubit connectivity interact in non-trivial ways during NISQ circuit compilation.

- Linear connectivity increases the two-qubit gate count by **50% to 75%** and gate-only depth by **28.6%** relative to the idealized Fully Connected reference for this benchmark.
- Higher optimization levels leave the measured structural metrics unchanged under Fully Connected connectivity, but reduce the CX count by two gates under Linear connectivity.
- The Linear CX reduction comes with additional single-qubit gates and increased median classical compilation time.
- Within Linear connectivity, **Opt 0** minimizes median compilation time, while **Opt 2** minimizes the measured two-qubit gate count.
- The results support evaluating compilation settings against explicit resource objectives and the target coupling topology rather than assuming that higher optimization always produces a better circuit.

These conclusions describe the measured benchmark and environment. A physical reliability improvement cannot be assumed from gate counts alone and would require additional hardware or noise-model validation.
