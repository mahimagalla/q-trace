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
   - **Linear Topology:** Optimization level 0 and 1 yield 14 two-qubit operations. Optimization levels 2 and 3 reduce two-qubit operations to 12 (a **14.3% reduction** in 2Q gates) alongside an increase in single-qubit operations (from 12 to 17). Rather than asserting specific internal pulse cancellation mechanisms without transpiler pass-manager execution traces, we report this as an empirical structural reduction achieved through Qiskit's higher-level synthesis and heuristic optimization passes, which restructure entangling blocks at the expense of additional single-qubit rotations.
   - **Fully Connected Topology:** Optimization levels 0 through 3 consistently produce 8 two-qubit operations (the theoretical minimum for 4 cost unitary edges with 2 CX gates per RZZ).

2. **Circuit Depth Invariance:**
   - For this 4-vertex cycle QAOA circuit, gate-only depth is 18 on linear and 14 on fully connected connectivity across all optimization levels. While optimization levels 2 and 3 eliminate 2 CX gates on linear topology, the critical path length remains bounded by the routing dependencies.

3. **Transpilation Time Overhead & Sample Size Considerations:**
   - Classical transpilation duration generally increases from Level 0/1 to Level 2/3 as additional synthesis passes are invoked.
   - **Timing Outlier & Sample Size Note:** In the fully connected Level 0 run, trial 1 recorded 80.61 ms before settling to a median of 4.58 ms across remaining trials, likely reflecting initial Python runtime and transpiler module cold-start overhead. Because each configuration was evaluated across five trials (N=5), these execution times capture observed runtime variability under fixed settings rather than definitive latency distributions. Timing conclusions should therefore be interpreted with appropriate caution.
   - **Candidate Choice for this Benchmark:** Comparing Level 2 and Level 3, both produce identical compiled structural metrics (12 CX gates on linear, 8 on fully connected, depth 18). Level 2 serves as a favorable candidate choice for this specific QAOA benchmark by achieving the observed gate reductions without the additional classical compilation overhead of Level 3. Wider benchmark suites and varied topologies are needed before generalizing this finding to all NISQ QAOA circuits.

## 4. Generated Plots
- `plots/optimization/opt_level_vs_gate_counts.png`
- `plots/optimization/opt_level_vs_circuit_depth.png`
- `plots/optimization/opt_level_vs_transpilation_time.png`
- `plots/optimization/optimization_tradeoff_pareto.png`