# Optimization-Level Experiments: Summary & Findings

**Author:** K Prerana (Member 3 - 2024BCS0048)  
**Module:** `experiments/optimization`  
**Project:** Q-TRACE (EIGEN5)  

## 1. Experimental Overview

This study isolates the empirical impact of Qiskit transpiler optimization levels (0, 1, 2, and 3) while holding fixed: basis gates (`['u', 'cx']`), initial layout (`identity`), transpiler seed (`2026`), and 5 repeated trials per configuration to measure runtime variability.

## 2. Quantitative Results Table

| Topology | Opt Level | 1Q Gates | 2Q Gates (CX) | Depth | Median Time (ms) | Min-Max Range (ms) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| fully_connected | 0 | 12 | 8 | 14 | 5.99 ms | 3.43 - 43.49 ms |
| fully_connected | 1 | 12 | 8 | 14 | 6.18 ms | 4.74 - 8.16 ms |
| fully_connected | 2 | 12 | 8 | 14 | 8.54 ms | 5.59 - 10.78 ms |
| fully_connected | 3 | 12 | 8 | 14 | 9.35 ms | 7.47 - 10.43 ms |
| linear | 0 | 12 | 14 | 18 | 4.28 ms | 3.77 - 4.36 ms |
| linear | 1 | 12 | 14 | 18 | 5.61 ms | 4.81 - 7.46 ms |
| linear | 2 | 17 | 12 | 18 | 8.22 ms | 6.68 - 9.18 ms |
| linear | 3 | 17 | 12 | 18 | 7.65 ms | 6.64 - 10.35 ms |

## 3. Key Observations & Trade-Off Analysis

1. **Gate Count Optimization:**
   - **Linear Topology:** Optimization level 0 and 1 yield 14 two-qubit operations. Optimization levels 2 and 3 reduce two-qubit operations to 12 (a **14.3% reduction** in 2Q gates) alongside an increase in single-qubit operations (from 12 to 17). Rather than asserting specific internal pulse cancellation mechanisms without transpiler pass-manager execution traces, we report this as an empirical structural reduction achieved through Qiskit's higher-level synthesis and heuristic optimization passes, which restructure entangling blocks at the expense of additional single-qubit rotations.
   - **Fully Connected Topology:** Optimization levels 0 through 3 consistently produce 8 two-qubit operations under the chosen basis gates (`['u', 'cx']`) and transpilation settings. This is an observed result for this configuration, not a universal theoretical lower bound.

2. **Circuit Depth Invariance:**
   - For this 4-vertex cycle QAOA circuit, gate-only depth is 18 on linear and 14 on fully connected connectivity across all optimization levels. While optimization levels 2 and 3 eliminate 2 CX gates on linear topology, the critical path length remains bounded by the routing dependencies.

3. **Transpilation Time Overhead & Sample Size Considerations:**
   - Classical transpilation duration generally increases from Level 0/1 to Level 2/3 as additional synthesis passes are invoked.
   - **Timing Outlier & Sample Size Note:** For fully connected topology at optimization level 0, the five trials (N=5) have a median transpilation time of 5.99 ms and a range of 3.43–43.49 ms. The recorded environment was Qiskit 2.5.2, Python 3.14.4, Windows 64-bit. The cause of the outlier is unknown. With only five trials per configuration, timing conclusions are preliminary and should be interpreted cautiously.
   - **Candidate Choice for this Benchmark:** Comparing Level 2 and Level 3, both produce identical compiled structural metrics (12 CX gates on linear, 8 on fully connected, depth 18 on linear and 14 on fully connected). Level 2 is a candidate choice for this specific QAOA benchmark based on its observed gate reductions; the small sample and variable measured times do not establish a reliable timing advantage. Wider benchmark suites and varied topologies are needed before generalizing this finding to all NISQ QAOA circuits.

## 4. Generated Plots
- `plots/optimization/opt_level_vs_gate_counts.png`
- `plots/optimization/opt_level_vs_circuit_depth.png`
- `plots/optimization/opt_level_vs_transpilation_time.png`
- `plots/optimization/optimization_tradeoff_pareto.png`
