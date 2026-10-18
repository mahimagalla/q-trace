# Q-TRACE Trade-off Analysis: Q-TRACE Primary Experiments

All Pareto objectives are minimized. Transpilation times are descriptive measurements, not quantum execution times.

## Configuration Metrics

| Topology | Optimization level | 2Q gates | Depth | Median transpilation time (ms) |
| --- | --- | --- | --- | --- |
| fully_connected | 0 | 8 | 14 | 8.74 |
| fully_connected | 1 | 8 | 14 | 13.37 |
| fully_connected | 2 | 8 | 14 | 14.17 |
| fully_connected | 3 | 8 | 14 | 18.24 |
| linear | 0 | 14 | 18 | 13.24 |
| linear | 1 | 14 | 18 | 14.22 |
| linear | 2 | 12 | 18 | 20.28 |
| linear | 3 | 12 | 18 | 20.50 |

## Primary Pareto Frontier

Objectives: two-qubit gates, circuit depth, and median transpilation time.

| Topology | Optimization level | 2Q gates | Depth | Median transpilation time (ms) |
| --- | --- | --- | --- | --- |
| fully_connected | 0 | 8 | 14 | 8.74 |

## Structural Pareto Frontier

Objectives: two-qubit gates and circuit depth.

| Topology | Optimization level | 2Q gates | Depth | Median transpilation time (ms) |
| --- | --- | --- | --- | --- |
| fully_connected | 0 | 8 | 14 | 8.74 |
| fully_connected | 1 | 8 | 14 | 13.37 |
| fully_connected | 2 | 8 | 14 | 14.17 |
| fully_connected | 3 | 8 | 14 | 18.24 |

## Compilation Trade-off Frontier

Objectives: two-qubit gates and median transpilation time.

| Topology | Optimization level | 2Q gates | Depth | Median transpilation time (ms) |
| --- | --- | --- | --- | --- |
| fully_connected | 0 | 8 | 14 | 8.74 |
