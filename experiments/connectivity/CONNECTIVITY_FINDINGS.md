# Connectivity and Routing Experiments: Summary & Findings

**Author:** Mounika Kolluru (Member 4)  
**Module:** `experiments/connectivity`  
**Project:** Q-TRACE (EIGEN5)  

## 1. Experimental Overview

This module evaluates the structural and compilation overhead imposed by physical qubit connectivity constraints on a 4-vertex cycle QAOA Max-Cut benchmark ($p=1$, $\gamma=0.5, \beta=0.25$, edges: `(0,1), (1,2), (2,3), (3,0)`).

All experimental factors were held strictly constant across comparisons:
- **Basis gates:** `['u', 'cx']`
- **Initial layout:** Identity layout `[0, 1, 2, 3]`
- **Routing method:** Qiskit default preset pass manager
- **Transpiler seed:** `2026`
- **Repetitions:** 5 trials per configuration (40 compiled trials + 1 baseline row)
- **Environment:** Qiskit `2.5.1`, Python `3.14.2` (Windows 64-bit)

## 2. Quantitative Results & Routing Overhead Table

| Optimization Level | Metric | Linear Topology | Fully Connected (Ideal) | Routing Overhead |
|:---:|:---|:---:|:---:|:---:|
| **Level 0** | Two-qubit gates (CX)<br>Gate-only depth<br>Median time (ms) | 14<br>18<br>6.65 ms | 8<br>14<br>5.32 ms | **+75.0%** (CX overhead)<br>**+28.6%** (Depth overhead)<br>+1.33 ms (+24.9%) |
| **Level 1** | Two-qubit gates (CX)<br>Gate-only depth<br>Median time (ms) | 14<br>18<br>15.59 ms | 8<br>14<br>7.42 ms | **+75.0%** (CX overhead)<br>**+28.6%** (Depth overhead)<br>+8.17 ms (+110.1%) |
| **Level 2** | Two-qubit gates (CX)<br>Gate-only depth<br>Median time (ms) | 12<br>18<br>13.55 ms | 8<br>14<br>10.98 ms | **+50.0%** (CX overhead)<br>**+28.6%** (Depth overhead)<br>+2.57 ms (+23.4%) |
| **Level 3** | Two-qubit gates (CX)<br>Gate-only depth<br>Median time (ms) | 12<br>18<br>12.21 ms | 8<br>14<br>11.13 ms | **+50.0%** (CX overhead)<br>**+28.6%** (Depth overhead)<br>+1.08 ms (+9.7%) |

## 3. Key Observations & Routing Mechanism Analysis

1. **Origin of the Routing Penalty:**
   - The logical problem graph contains four cycle edges: $(0,1)$, $(1,2)$, $(2,3)$, and $(3,0)$.
   - In the **Fully Connected** topology, all pairs have direct hardware links (12 directed edges). Under our chosen standard decomposition of 2 CX gates per $R_{ZZ}$ block across the four problem edges, the compiled circuit consistently produces **8 CX gates** across all optimization levels.
   - In the **Linear** topology, the physical hardware only allows $(0,1)$, $(1,2)$, and $(2,3)$ (6 directed edges). The non-adjacent edge $(3,0)$ requires routing mediation.

2. **SWAP Decomposition & Metric Nuance:**
   - Under target basis `['u', 'cx']`, routing SWAP gates are decomposed into CX and single-qubit gates.
   - Consequently, `explicit_swap_count` is **0** in all runs.
   - The routing penalty manifests entirely as an increase in two-qubit CX count (14 at Level 0/1; 12 at Level 2/3) and an increase in gate-only depth (18 vs. 14).
   - Calling `explicit_swap_count` the "routing SWAP count" would be misleading; two-qubit gate counts and critical-path depth serve as the rigorous empirical measures of routing overhead.

3. **Optimization-Connectivity Interaction:**
   - On Fully Connected topology, optimization levels 0 through 3 consistently yield 8 two-qubit operations, reflecting the baseline structure under our chosen decomposition.
   - On Linear topology, optimization levels 2 and 3 yield **12 CX gates** compared to 14 CX at levels 0 and 1 (a 14.3% reduction in two-qubit operations alongside an increase from 12 to 17 single-qubit rotations). Rather than asserting specific internal pulse or gate cancellation mechanisms without transpiler pass-manager execution traces, we report this as an empirical structural reduction observed under Qiskit's higher-level synthesis and heuristic optimization passes.
   - Across all optimization levels, critical path depth on Linear connectivity remains locked at 18 due to dependency serialization along the 1D chain.

4. **Transpilation Runtime Considerations:**
   - Linear connectivity has higher median transpilation times than Fully Connected at Levels 0–3 in this dataset (for example, 15.59 ms vs. 7.42 ms at Level 1). These measurements do not isolate the cause of the timing differences.
   - At Levels 2 and 3, the observed median differences are 2.57 ms and 1.08 ms, respectively. With five trials per configuration, these timing comparisons are preliminary.

## 4. Generated Plots

- `plots/connectivity/connectivity_2q_gates.png`: Bar comparison of 2Q CX gate count across optimization levels.
- `plots/connectivity/connectivity_circuit_depth.png`: Critical-path depth comparison across levels.
- `plots/connectivity/connectivity_transpilation_time.png`: Median transpilation time with min-max variability error bars.
- `plots/connectivity/connectivity_routing_overhead_pct.png`: Relative percentage routing penalty of Linear vs. Fully Connected.

## 5. Experimental Scope & Limitations

- **Timing Sample Size & Variability:** Compilation durations are based on five repeated trials per cell ($N=5$) with a fixed seed (`2026`). The Linear Level 0 group includes one observed runtime of approximately 4.59 seconds; its cause is unknown. The small sample measures observed runtime variability under fixed compilation settings, not definitive latency distributions. Strong conclusions regarding classical runtime advantages should therefore be avoided.
- **Software Environment:** All experiments were executed and recorded using Qiskit `2.5.1` and Python `3.14.2` on Windows 64-bit.
- **Circuit Scope:** These empirical observations are specific to a single 4-qubit QAOA Max-Cut instance at depth $p=1$ with identity initial layout and basis `['u', 'cx']`. They should not be generalized to larger graph instances, arbitrary hardware topologies, or alternate transpiler pass configurations without further empirical studies.
