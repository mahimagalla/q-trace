# Optimization-Level Experiments: Summary & Findings

**Author:** K Prerana (Member 3 - 2024BCS0048)  
**Module:** `experiments/optimization`  
**Project:** Q-TRACE (EIGEN5)  

## 1. Experimental Overview

This study isolates the empirical impact of Qiskit transpiler optimization levels (0, 1, 2, and 3) while holding fixed: basis gates (`['u', 'cx']`), initial layout (`identity`), transpiler seed (`2026`), and 5 repeated trials per configuration to measure runtime variability.

## 2. Quantitative Results Table

| Topology | Opt Level | 1Q Gates | 2Q Gates (CX) | Depth | Median Time (ms) | Min-Max Range (ms) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| fully_connected | 0 | 12 | 8 | 14 | 4.58 ms | 4.20 - 80.61 ms |
| fully_connected | 1 | 12 | 8 | 14 | 6.61 ms | 5.94 - 8.40 ms |
| fully_connected | 2 | 12 | 8 | 14 | 10.16 ms | 9.70 - 11.10 ms |
| fully_connected | 3 | 12 | 8 | 14 | 12.04 ms | 9.49 - 12.42 ms |
| linear | 0 | 12 | 14 | 18 | 6.20 ms | 5.05 - 6.40 ms |
| linear | 1 | 12 | 14 | 18 | 9.06 ms | 7.06 - 10.39 ms |
| linear | 2 | 17 | 12 | 18 | 11.10 ms | 9.60 - 13.70 ms |
| linear | 3 | 17 | 12 | 18 | 10.71 ms | 9.72 - 13.87 ms |

## 3. Key Observations & Trade-Off Analysis

1. **Gate Count Optimization:**
   - **Linear Topology:** Optimization level 0 and 1 yield 14 two-qubit operations. Optimization levels 2 and 3 reduce two-qubit operations to 12 (a **14.3% reduction** in 2Q gates) by canceling redundant single- and two-qubit pulse sequences.
   - **Fully Connected Topology:** Optimization levels 0 through 3 consistently produce 8 two-qubit operations (the theoretical minimum for 4 cost unitary edges with 2 CX gates per RZZ).

2. **Circuit Depth Invariance:**
   - For this 4-vertex cycle QAOA circuit, gate-only depth is 18 on linear and 14 on fully connected connectivity across all optimization levels. While optimization levels 2 and 3 eliminate 2 CX gates on linear topology, the critical path length remains bounded by the routing dependencies.

3. **Transpilation Time Overhead vs. Diminishing Returns:**
   - Increasing from Level 1 to Level 3 increases classical transpilation time noticeably.
   - Comparing Level 2 and Level 3: both achieve identical 2Q gate counts (12 for linear, 8 for fully connected) and identical circuit depth, but Level 3 spends additional synthesis iterations without further structural improvements on this benchmark.
   - **Recommendation:** Optimization Level 2 represents the Pareto-efficient configuration for NISQ QAOA under constrained connectivity, balancing compile runtime and gate noise minimization.

## 4. Generated Plots
- `plots/optimization/opt_level_vs_gate_counts.png`
- `plots/optimization/opt_level_vs_circuit_depth.png`
- `plots/optimization/opt_level_vs_transpilation_time.png`
- `plots/optimization/optimization_tradeoff_pareto.png`