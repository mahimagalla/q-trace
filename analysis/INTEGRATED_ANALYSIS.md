# Integrated Resource Trade-off and Pareto Analysis

**Project:** Q-TRACE (Compilation-Aware Resource Estimation for NISQ Quantum Circuits)  
**Team:** EIGEN5 (IEG 313: Quantum Computing for Engineers)  
**Author:** Shaik Shaheeq (Member 5 — Integrated Analysis, Visualization, and Trade-offs)  
**Date:** October 2026  
**Status:** Validated Research Findings Report  

---

## Executive Summary

This report delivers the integrated findings for the **Q-TRACE** research study, synthesizing empirical measurements across transpiler optimization levels (Levels 0, 1, 2, and 3) and physical qubit coupling topologies (Linear vs. idealized Fully Connected). The analysis evaluates compilation-aware resource requirements for a fixed 4-qubit Quantum Approximate Optimization Algorithm (QAOA) Max-Cut benchmark ($p=1$).

Using reproducible data loading, strict mathematical Pareto dominance modeling, and systematic cross-dataset auditing, we examine the trade-offs between two-qubit gate count ($2Q$), gate-only circuit depth, single-qubit rotation overhead, and classical transpilation time.

### Key Measured Insights:
1. **Connectivity Routing Penalty:** For this 4-vertex cycle instance, constrained Linear connectivity imposes an observed **$+75.0\%$ two-qubit gate overhead** (14 CX vs. 8 CX) at Optimization Levels 0–1 and a **$+50.0\%$ overhead** (12 CX vs. 8 CX) at Optimization Levels 2–3, alongside an invariant **$+28.6\%$ gate-only depth penalty** (depth 18 vs. 14).
2. **Decomposition vs. Routing Overhead:** The untranspiled baseline contains 4 two-qubit $R_{ZZ}$ gates and 8 single-qubit gates. Compiling to the basis set `['u', 'cx']` decomposes each $R_{ZZ}$ interaction into 2 CX gates and local rotations, producing 8 CX gates even under unconstrained connectivity. Zero explicit SWAP instructions (`explicit_swap_count = 0`) are observed across all 40 compiled trials because routing SWAPs are fully decomposed into basis CX gates.
3. **The 2Q vs. 1Q Gate Optimization Trade-off:** On the Linear topology, higher optimization levels (Levels 2 and 3) successfully eliminate 2 CX gates (reducing $2Q$ count from 14 to 12, a $14.3\%$ reduction), but this reduction requires **5 additional single-qubit rotations** (increasing $1Q$ gate count from 12 to 17) while leaving circuit depth unchanged at 18.
4. **Pareto Frontier & "Universal Winner" Evaluation:**
   * **Global Multi-Objective Frontier:** When idealized Fully Connected connectivity is compared alongside Linear connectivity, `fully_connected / Opt 0` strictly dominates all other configurations on the primary dataset ($2Q=8$, $\text{depth}=14$, $\text{median time}=8.74\text{ ms}$).
   * **Within-Topology Realism:** On physical Linear hardware where connectivity is fixed by device physics, **no single universal winner exists**. **Linear Opt 0** is Pareto-optimal for compilation latency ($13.24\text{ ms}$ median), whereas **Linear Opt 2** is Pareto-optimal for minimizing entangling gate count ($12\text{ CX}$ gates), requiring a $+53.2\%$ classical transpilation time investment.

---

## 1. Experimental Methodology & Benchmark Setup

The experimental framework evaluates how compilation pass managers alter circuit resource profiles under controlled constraints.

### 1.1 Benchmark Specification
* **Problem:** Max-Cut on an unweighted 4-vertex cycle graph $C_4$.
* **Graph Edges:** $E = \{(0, 1), (1, 2), (2, 3), (3, 0)\}$. The non-adjacent edge $(3, 0)$ forces routing mediation on 1D linear physical lattices.
* **QAOA Instance:** Depth $p = 1$, using fixed variational parameters $\gamma = 0.5$ (cost parameter) and $\beta = 0.25$ (mixer parameter). Parameters are held strictly constant to isolate compilation mechanics; variational parameter optimization is deliberately decoupled from this study.
* **Cost Hamiltonian Formulation:**
  $$H_C = \sum_{(u,v) \in E} \frac{I - Z_u Z_v}{2}, \quad U_C(\gamma) = e^{-i \gamma H_C} \equiv \prod_{(u,v) \in E} R_{ZZ}(-\gamma, u, v)$$
* **Mixer Unitary:**
  $$U_M(\beta) = \prod_{v \in V} R_X(2\beta, v)$$

### 1.2 Transpilation Matrix & Controlled Factors
To ensure fair empirical comparisons, all compilation factors were held constant with the exception of the two independent experimental variables:

| Experimental Factor | Value / Protocol Specification | Methodological Rationale |
| :--- | :--- | :--- |
| **Optimization Levels** | `0, 1, 2, 3` | Explores preset Qiskit pass manager configurations from basic translation to aggressive synthesis. |
| **Coupling Topologies** | **Linear:** `[0-1, 1-2, 2-3]` (bidirectional, 6 links)<br>**Fully Connected:** Complete graph $K_4$ (bidirectional, 12 links) | Contrasts hardware-constrained 1D routing against an unconstrained idealized baseline. |
| **Target Basis Gates** | `['u', 'cx']` | Fixed standard universal basis. Mandates uniform gate representation across topologies. |
| **Initial Layout** | Identity: $q_0 \to Q_0, q_1 \to Q_1, q_2 \to Q_2, q_3 \to Q_3$ | Eliminates layout search heuristics as an uncontrolled confounder. |
| **Transpiler Seed** | `2026` | Ensures deterministic routing seed behavior across repetitions. |
| **Repeated Trials** | $N = 5$ independent timing trials per cell | Measures classical transpilation runtime variability. |
| **Scheduling** | Off / Not requested | Duration and idle-time pulse schedules are excluded from this phase. |

### 1.3 Metric Counting Conventions
In strict adherence to the Q-TRACE protocol:
* **Exclusion Rule:** Measurement operations, barriers, delays, and compiler directives are strictly excluded from `gate_count_1q`, `gate_count_2q`, and `circuit_depth`. Measurement operations are recorded in an independent `measurement_count` field.
* **Gate Arity:** Two-qubit gates are counted by operator arity rather than gate name alone. In basis `['u', 'cx']`, two-qubit operations correspond strictly to CX gates.
* **Transpilation Time:** Measured purely as wall-clock time around the isolated Qiskit `transpile()` function invocation, excluding circuit creation, metric extraction, and disk I/O.

---

## 2. Cross-Dataset Audit & Environmental Compatibility

Three distinct experimental CSV outputs were audited using [`analysis/data_loader.py`](file:///Users/shaheeq.s/q-trace/analysis/data_loader.py):

| Dataset Path | Rows | Qiskit Version | Python Version | Primary Purpose |
| :--- | :---: | :---: | :---: | :--- |
| **`results/qtrace_results.csv`** | 40 | `2.5.2` | `3.14.4` | **Primary Integrated Dataset:** 8 configurations $\times$ 5 trials. Clean baseline environment. |
| **`results/optimization_experiments.csv`** | 40 | `2.5.2` | `3.14.4` | **Member 3 Study:** Dedicated optimization sweeps. |
| **`results/connectivity_experiments.csv`** | 41 | `2.5.1` | `3.14.2` | **Member 4 Study:** Dedicated connectivity sweeps + 1 untranspiled baseline record. |

### Methodological Rule on Cross-Environment Data:
The audit confirmed that **structural metrics (1Q gates, 2Q gates, and depth) are 100% invariant across all three datasets**. However, because classical compilation runtimes are sensitive to software versioning and system environments (Qiskit `2.5.2` vs. `2.5.1`, Python `3.14.4` vs. `3.14.2`), **transpilation timing observations from different environments must not be merged into a single pooled distribution**. 

Consequently, the primary quantitative findings and Pareto frontiers in this report are anchored on the internally consistent `results/qtrace_results.csv` dataset, with cross-dataset differences explicitly annotated.

---

## 3. Quantitative Results & Structural Invariants

The table below summarizes the measured structural metrics and classical transpilation times from the primary dataset (`results/qtrace_results.csv`), alongside the untranspiled baseline from `results/connectivity_experiments.csv`.

| Configuration | Topology | Opt Level | 1Q Gates (`u`) | 2Q Gates (`cx`) | Gate-Only Depth | Total Ops | Explicit SWAPs | Median Time (ms) | Observed Min–Max Range (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Logical)** | `baseline` | *NA* | 8 | 4 | 6 | 12 | 0 | *NA* | *NA* |
| **FC-Opt0** | `fully_connected` | 0 | 12 | 8 | 14 | 24 | 0 | **8.74** | 6.67 – 13.26 |
| **FC-Opt1** | `fully_connected` | 1 | 12 | 8 | 14 | 24 | 0 | 13.37 | 11.80 – 15.65 |
| **FC-Opt2** | `fully_connected` | 2 | 12 | 8 | 14 | 24 | 0 | 14.17 | 13.53 – 20.37 |
| **FC-Opt3** | `fully_connected` | 3 | 12 | 8 | 14 | 24 | 0 | 18.24 | 14.44 – 21.48 |
| **LI-Opt0** | `linear` | 0 | 12 | 14 | 18 | 30 | 0 | **13.24** | 8.94 – 49.88 |
| **LI-Opt1** | `linear` | 1 | 12 | 14 | 18 | 30 | 0 | 14.22 | 12.46 – 16.77 |
| **LI-Opt2** | `linear` | 2 | 17 | 12 | 18 | 33 | 0 | **20.28** | 17.55 – 22.94 |
| **LI-Opt3** | `linear` | 3 | 17 | 12 | 18 | 33 | 0 | 20.50 | 18.18 – 21.72 |

*(Note: Total operations and gate counts exclude 4 measurement operations).*

---

## 4. In-Depth Analysis of Research Questions

### 4.1 Decomposition vs. Routing Overhead
A central point of confusion in NISQ compilation analysis is distinguishing between **basis decomposition overhead** and **connectivity routing overhead**.

1. **Logical Baseline:** The untranspiled QAOA circuit contains 4 single-qubit Hadamard gates ($H$), 4 two-qubit $R_{ZZ}(-\gamma)$ problem-Hamiltonian gates, and 4 single-qubit $R_X(2\beta)$ mixer gates, yielding:
   $$\text{1Q gates} = 8, \quad \text{2Q gates} = 4, \quad \text{Depth} = 6$$
2. **Basis Translation Expansion:** In target basis `['u', 'cx']`, $R_{ZZ}(\theta)$ is not a native physical instruction. The canonical unitary equivalence is:
   $$R_{ZZ}(\theta) \equiv \text{CX}(q_1, q_2) \cdot (I \otimes R_Z(\theta)) \cdot \text{CX}(q_1, q_2)$$
   Each logical edge therefore requires **2 CX gates** and local rotation adjustments. Across 4 graph edges, basis translation expands the two-qubit requirement to:
   $$4 \times 2 = 8 \text{ CX gates}$$
   This expansion occurs even on the unconstrained Fully Connected topology. Thus, the jump from 4 to 8 CX gates is **purely a basis translation artifact**, not routing overhead.
3. **The SWAP Decomposition Reality:** On Linear connectivity, the logical edge $(3, 0)$ is non-local. Compiling on a linear chain $0-1-2-3$ requires routing. However, in `results/qtrace_results.csv`, `explicit_swap_count` is **0 across all compiled configurations**. This does **not** indicate that routing occurred without SWAPs; rather, under target basis `['u', 'cx']`, Qiskit decomposes every routing SWAP into 3 CX gates:
   $$\text{SWAP}(a, b) \equiv \text{CX}(a, b) \cdot \text{CX}(b, a) \cdot \text{CX}(a, b)$$
   Consequently, routing overhead surfaces directly as an increase in two-qubit CX gates and critical-path depth, rather than named SWAP operations.

### 4.2 Observed Connectivity-Associated Overhead
Comparing Linear topology against Fully Connected topology under identical optimization levels isolates the physical connectivity penalty:

| Optimization Level | Metric | Fully Connected | Linear Topology | Programmatic Overhead (% Increase) |
| :---: | :--- | :---: | :---: | :---: |
| **Level 0** | Two-qubit gates (CX)<br>Gate-only depth<br>Median transpilation time | 8<br>14<br>8.74 ms | 14<br>18<br>13.24 ms | **+75.0%**<br>**+28.6%**<br>+51.6% |
| **Level 1** | Two-qubit gates (CX)<br>Gate-only depth<br>Median transpilation time | 8<br>14<br>13.37 ms | 14<br>18<br>14.22 ms | **+75.0%**<br>**+28.6%**<br>+6.4% |
| **Level 2** | Two-qubit gates (CX)<br>Gate-only depth<br>Median transpilation time | 8<br>14<br>14.17 ms | 12<br>18<br>20.28 ms | **+50.0%**<br>**+28.6%**<br>+43.1% |
| **Level 3** | Two-qubit gates (CX)<br>Gate-only depth<br>Median transpilation time | 8<br>14<br>18.24 ms | 12<br>18<br>20.50 ms | **+50.0%**<br>**+28.6%**<br>+12.4% |

#### Key Empirical Observations:
* **Entangling Gate Inflation:** At Optimization Levels 0 and 1, the lack of a direct link between qubits 3 and 0 introduces 6 additional CX gates (14 vs. 8, a **$+75.0\%$ penalty**).
* **Depth Expansion:** In all four optimization levels, critical path depth increases from 14 to 18 (a **$+28.6\%$ penalty**). This expansion is constrained by the dependency chain along the 1D physical lattice, serializing operations that would otherwise execute concurrently.
* **Transpilation Time Overhead:** Linear routing adds heuristic layout and routing pass overhead, increasing median compile time by $+6.4\%$ to $+51.6\%$ relative to the unconstrained topology.

### 4.3 The Optimization Trade-off: 2Q Reduction vs. 1Q Gate Inflation
Does higher transpiler optimization reduce resource usage? The empirical data reveals distinct behaviors depending on topology:

1. **Fully Connected Invariance:**
   On Fully Connected topology, Optimization Levels 0, 1, 2, and 3 produce **completely identical structural circuits**:
   $$\text{1Q} = 12, \quad \text{2Q} = 8, \quad \text{Depth} = 14, \quad \text{Total Ops} = 24$$
   Increasing optimization level from 0 to 3 more than doubles the median compilation runtime (from $8.74\text{ ms}$ to $18.24\text{ ms}$, a **$+108.7\%$ time penalty**) with **zero reduction in gates or depth**. For this benchmark under unconstrained connectivity, Level 0 is objectively optimal.
2. **Linear Topology Structural Reconfiguration:**
   On Linear topology, Optimization Levels 2 and 3 achieve an empirical reduction of 2 CX gates ($14 \to 12$, a **$-14.3\%$ reduction**). However, this reduction comes with a structural trade-off:
   * **Single-Qubit Gate Increase:** Single-qubit rotations increase from 12 to 17 (**$+41.7\%$ increase**).
   * **Total Operations Increase:** Total compiled operations increase from 30 to 33 (**$+10.0\%$ increase**).
   * **Depth Invariance:** Gate-only circuit depth remains pinned at 18.
   * **Compilation Time Cost:** Median compilation time increases from $13.24\text{ ms}$ (Opt 0) to $20.28\text{ ms}$ (Opt 2), a **$+53.2\%$ increase**.

#### Physical Interpretation:
In NISQ quantum hardware, two-qubit gate operations typically have lower fidelities than single-qubit gates. Consequently, reducing two-qubit gate count may reduce exposure to two-qubit gate errors; however, the magnitude of any reliability improvement cannot be established from these resource-count measurements alone without hardware execution or noise-model simulation. Furthermore, trading 2 CX gates for 5 single-qubit rotations requires a +53.2% classical compilation time investment at Optimization Level 2.

---

## 5. Pareto-Frontier Analysis

Pareto optimality provides a principled, multi-objective framework to identify non-dominated compilation choices without arbitrarily weighting competing metrics.

### 5.1 Mathematical Dominance Definition
Let each compilation configuration $C$ be characterized by an objective vector $M(C) = [m_1(C), m_2(C), \dots, m_k(C)]$. All objectives are strictly minimized (lower is better).

A configuration $A$ **strictly Pareto-dominates** configuration $B$ ($A \prec B$) if and only if:
$$\forall i \in \{1, \dots, k\}, \quad m_i(A) \le m_i(B) \quad \text{and} \quad \exists j \in \{1, \dots, k\}, \quad m_j(A) < m_j(B)$$

A configuration is **Pareto-optimal** if no other configuration in the evaluated set dominates it.

### 5.2 Evaluated Objective Spaces

#### 1. Primary Multi-Objective Space (2Q Gates $\downarrow$, Depth $\downarrow$, Median Transpilation Time $\downarrow$)
* **Evaluated Set:** All 8 compiled configurations in `results/qtrace_results.csv`.
* **Global Non-Dominated Frontier:**
  $$\text{Frontier} = \{\mathbf{FC\text{-}Opt0}\}$$
* **Dominance Analysis:** `fully_connected / Opt 0` achieves $2Q = 8$, $\text{depth} = 14$, and $\text{time} = 8.74\text{ ms}$. Because it is strictly superior or equal to every other compiled configuration across all three dimensions, it mathematically dominates all other candidates in this specific global dataset.

#### 2. Structural Space (2Q Gates $\downarrow$, Gate-Only Depth $\downarrow$)
* **Non-Dominated Frontier:**
  $$\text{Frontier} = \{\mathbf{FC\text{-}Opt0}, \; \mathbf{FC\text{-}Opt1}, \; \mathbf{FC\text{-}Opt2}, \; \mathbf{FC\text{-}Opt3}\}$$
* **Dominance Analysis:** All four Fully Connected levels produce identical objective vectors $(8, 14)$. Because duplicate vectors do not strictly dominate each other, all four populate the structural frontier. Both Linear clusters, $(14, 18)$ and $(12, 18)$, are strictly dominated by $(8, 14)$.

#### 3. Compilation Trade-off Space (2Q Gates $\downarrow$, Median Transpilation Time $\downarrow$)
* **Non-Dominated Frontier:**
  $$\text{Frontier} = \{\mathbf{FC\text{-}Opt0}\}$$

### 5.3 Within-Topology Pareto Frontier (Constrained Linear Hardware)
When evaluating real-world physical devices, quantum processors possess fixed coupling architectures; an experimenter targeting a linear superconducting qubit chain cannot arbitrarily deploy an idealized fully connected topology.

Evaluating the Pareto frontier **restricted strictly to the Linear topology** yields a genuine engineering trade-off:

| Linear Configuration | 2Q Gates (CX) | Circuit Depth | Median Transpilation Time | Pareto Status (Within Linear) | Engineering Trade-off Profile |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Linear Opt 0** | 14 | 18 | **13.24 ms** | **Pareto-Optimal** | **Fastest Compilation:** Minimizes classical pre-processing overhead. Ideal for rapid simulation or compilation-sensitive loops. |
| **Linear Opt 1** | 14 | 18 | 14.22 ms | Dominated | Dominated by Linear Opt 0 (equal gates and depth, but slower compile time). |
| **Linear Opt 2** | **12** | 18 | 20.28 ms | **Pareto-Optimal** | **Minimal 2Q Errors:** Eliminates 2 CX gates ($-14.3\%$), reducing physical two-qubit decoherence at the cost of $+53.2\%$ compile time. |
| **Linear Opt 3** | 12 | 18 | 20.50 ms | Dominated | Dominated by Linear Opt 2 (equal gates and depth, but slower compile time). |

---

## 6. Generated Visualizations

All four figures were generated programmatically by [`analysis/plot_integrated.py`](file:///Users/shaheeq.s/q-trace/analysis/plot_integrated.py) and saved in [`plots/analysis/`](file:///Users/shaheeq.s/q-trace/plots/analysis):

### Figure 1: Two-Qubit Gates vs. Transpilation Time
**File:** [`plots/analysis/2q_gates_vs_transpilation_time.png`](file:///Users/shaheeq.s/q-trace/plots/analysis/2q_gates_vs_transpilation_time.png)  
* **Visual Representation:** Scatter plot with asymmetric horizontal error bars displaying the observed min-max transpilation duration $[t_{\text{median}} - t_{\min}, \; t_{\max} - t_{\text{median}}]$ across 5 trials.
* **Research Takeaway:** Demonstrates the runtime cost of higher synthesis passes. Fully Connected points cluster at $2Q=8$ with runtimes stretching from $8.74\text{ ms}$ (Opt 0) to $18.24\text{ ms}$ (Opt 3). Linear points reveal the discrete jump between Opt 0/1 ($14\text{ CX}$) and Opt 2/3 ($12\text{ CX}$), highlighting the skew in compilation duration (notably Linear Opt 0 ranging up to $49.88\text{ ms}$).

### Figure 2: Structural Comparison (Depth vs. Two-Qubit Gates)
**File:** [`plots/analysis/depth_vs_2q_gates.png`](file:///Users/shaheeq.s/q-trace/plots/analysis/depth_vs_2q_gates.png)  
* **Visual Representation:** Gate-only critical-path depth plotted against two-qubit gate count. Identical coordinate pairs are consolidated into clean cluster labels.
* **Research Takeaway:** Clearly separates the design space into three distinct operational regimes:
  1. Idealized unconstrained compilation at $(8, 14)$.
  2. Basic linear compilation (Opt 0, 1) at $(14, 18)$.
  3. Optimized linear compilation (Opt 2, 3) at $(12, 18)$.
  The figure visually underscores that higher optimization reduces entangling gate count on linear lattices, but is unable to compress critical-path depth below 18.

### Figure 3: Multi-Objective Pareto Frontier
**File:** [`plots/analysis/pareto_frontier.png`](file:///Users/shaheeq.s/q-trace/plots/analysis/pareto_frontier.png)  
* **Visual Representation:** Highlights dominated vs. non-dominated points across the evaluated objective space, marking the global non-dominated point (`fully_connected / Opt 0`) with a prominent star.
* **Research Takeaway:** Illustrates why unconstrained connectivity provides an overwhelming advantage across all resource metrics when available, while positioning dominated points relative to their distance from the frontier.

### Figure 4: Observed Connectivity-Associated Overhead
**File:** [`plots/analysis/routing_overhead_integrated.png`](file:///Users/shaheeq.s/q-trace/plots/analysis/routing_overhead_integrated.png)  
* **Visual Representation:** Grouped bar chart depicting percentage increases for Linear connectivity relative to Fully Connected connectivity across all four optimization levels.
* **Research Takeaway:** Highlights that two-qubit gate overhead is highest at lower optimization levels ($+75.0\%$) and drops to $+50.0\%$ at Levels 2 and 3. Meanwhile, critical path depth overhead remains locked at $+28.6\%$ regardless of optimization effort.

---

## 7. Scope, Methodological Precautions, and Limitations

To maintain academic rigor and prevent overgeneralization, several experimental boundaries must be emphasized:

1. **Specific Benchmark Instance:**
   These findings are derived exclusively from a single 4-qubit QAOA Max-Cut benchmark on a cycle graph $C_4$ at depth $p=1$. Findings should **not** be extrapolated to arbitrary quantum algorithms, larger problem graphs ($N \gg 4$), higher QAOA depths ($p > 1$), or unstructured circuits without further empirical validation.
2. **Idealized vs. Physical Coupling:**
   A fully connected coupling map is an idealized analytical model used to establish a theoretical lower bound for routing overhead. Commercial NISQ devices (e.g., IBM heavy-hex, Google Sycamore square lattices, Rigetti octagonal rings) possess sparse connectivity; physical execution will always incur routing overhead.
3. **Timing Sample Size ($N=5$):**
   Classical compilation runtimes were measured over five repeated trials per configuration using a fixed transpiler seed (`2026`). While medians provide a robust measure of central tendency against occasional cold-start outliers (e.g., $4.58\text{ s}$ on trial 1 in `connectivity_experiments.csv`), $N=5$ represents an exploratory sample size. Observed runtimes describe compiler latency under fixed settings, not definitive statistical execution bounds.
4. **Classical Compilation vs. Quantum Execution:**
   Transpilation duration represents classical CPU wall-clock execution time during pass manager operation. It has no direct relationship to quantum circuit execution time (pulse duration), coherence decay, or physical hardware error rates.
5. **Software Versioning Sensitivity:**
   Cross-dataset audits established that while structural circuit transformations are identical between Qiskit `2.5.1` and `2.5.2`, compilation pass runtimes vary between minor releases and operating systems. Transpiler performance comparisons must always control for software version and host platform.

---

## 8. Reproducibility Instructions

The entire integrated analysis and plotting pipeline is fully reproducible from the repository root:

### Step 1: Environment Setup
Ensure Python 3.10+ is available and initialize the local environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pytest matplotlib numpy
```

### Step 2: Run Unit Tests
Execute the Pareto mathematical and data handling test suite:
```bash
python -m pytest tests/test_pareto_analysis.py -v
```
*Expected result:* 8 passed tests.

### Step 3: Run Trade-off & Pareto Analysis
Generate the markdown trade-off report from the primary dataset:
```bash
python -m analysis.tradeoff_analysis \
  --csv results/qtrace_results.csv \
  --name "Q-TRACE Primary Experiments" \
  --output results/tradeoff_analysis.md
```

### Step 4: Generate Publication Figures
Render all four analysis plots:
```bash
python -m analysis.plot_integrated
```
*Outputs generated in:* `plots/analysis/`
* `2q_gates_vs_transpilation_time.png`
* `depth_vs_2q_gates.png`
* `pareto_frontier.png`
* `routing_overhead_integrated.png`

---

## 9. Conclusion

The Q-TRACE integrated resource trade-off analysis confirms that transpiler optimization and physical qubit connectivity interact non-trivially in NISQ circuit compilation:
* Constrained connectivity imposes both an entangling gate penalty ($+50\% \text{ to } +75\%$) and a critical-path serialization penalty ($+28.6\%$).
* Higher optimization levels (Levels 2 and 3) do not alter compiled metrics on unconstrained topologies, but successfully eliminate 2 CX gates under linear connectivity at the expense of increased single-qubit rotations and greater classical compilation time.
* Declaring a single "universal best" compilation setting is physically misleading: under hardware connectivity constraints, **Optimization Level 0** minimizes classical compilation overhead, while **Optimization Level 2** provides the preferred structural configuration for minimizing two-qubit gate exposure (though any reliability improvement cannot be assumed without hardware validation).
