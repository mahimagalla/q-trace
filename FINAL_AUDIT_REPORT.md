# Q-TRACE Final Repository Audit

**Audit date:** 19 October 2026 (Asia/Calcutta)<br>
**Repository:** `D:\Docs\q-trace`<br>
**Branch:** `fix/integrated-report-consistency`<br>
**HEAD at audit start:** `a48183c1dd28f27bb4a9dea290dc4fb552f94b44` (`docs: update README and integrated analysis`)

## 1. Executive Summary

Q-TRACE is a coherent, small academic benchmarking project. The current implementation, datasets, and primary integrated analysis support the reported structural results. I independently reran the test suite and QAOA validation: **31 tests passed**, the expected Max-Cut value was **2.708073 / 4**, the optimal-cut probability was **0.358374**, and transpilation preserved the measured output distributions for all eight topology/optimization configurations to within **4.2×10⁻¹⁶**.

The audit found and corrected a compatibility-grouping defect, a working-directory-dependent output path, a missing-license-file reference, and a stale connectivity timing summary. The connectivity timing plot source uses a labeled logarithmic y-axis, and the tracked PNG was subsequently regenerated from the current plot function and saved CSV and visually reviewed.

**Readiness verdict:** Ready for an academic demonstration and static submission of the code, QAOA validation, structural findings, and reviewed connectivity timing figure. Timing claims should remain exploratory and dataset-specific. No hardware performance or quantum advantage is demonstrated.

## 2. Repository State and Inventory

At audit start, the working tree was clean, with no untracked files. The current branch tracked `origin/fix/integrated-report-consistency` and had no reported ahead/behind commits. The fetch/push remote was `https://github.com/mahimagalla/q-trace.git`. No branch switch, reset, history rewrite, commit, push, or merge was performed.

The repository had **46 tracked files** at audit start, in these groups:

| Area | Contents and purpose |
|---|---|
| Root | README, dependency pins, and `.gitignore` |
| `src/` | QAOA circuit and baseline experiment construction, transpilation configuration, metric collection, validation, and simple plots |
| `experiments/connectivity/` | Connectivity runner, connectivity plots, and connectivity findings |
| `experiments/optimization/` | Optimization-level runner, plots/report generation, and optimization findings |
| `analysis/` | CSV loader and compatibility audit, Pareto calculations, integrated analysis, plotting, and report |
| `results/` | Three CSV datasets and generated trade-off Markdown report |
| `plots/` | 15 tracked PNG figures spanning root, connectivity, optimization, and integrated analysis |
| `tests/` | Circuit/runner, connectivity, optimization, and Pareto tests |

The local `circuits/` directory contained no tracked files. There is no `LICENSE` file. At audit start, ignored local state included `.venv/`, `.pytest_cache/`, and Python `__pycache__/` directories; no secret values were inspected or reported. The changes from this audit are listed in Section 5.

## 3. Audit Coverage and Checklist

| Audit area | Status | Evidence / notes |
|---|---|---|
| Git state, branch, HEAD, tracking, history, tracked/untracked/ignored inventory | Complete | Captured before edits; short recent history reviewed |
| README, setup, dependencies, integrated report, experiment reports | Complete | Reviewed tracked documentation and cross-checked claims against CSVs |
| Source modules and plot/report generation code | Complete | Reviewed `src/`, `analysis/`, and both experiment modules |
| Existing tests | Complete | Full pytest suite rerun after changes |
| CSV schema, record counts, configuration/trial completeness, structural consistency | Complete | All three CSV files parsed; each compiled configuration has trial IDs 1–5 and consistent structural metrics |
| QAOA expected value and ideal/transpiled output distributions | Complete | `src.validate_qaoa` executed successfully |
| Pareto outputs and stored trade-off report | Complete | Recomputed primary frontier; stored Markdown exactly matches an in-memory render |
| Saved and generated plot integrity | Complete | All 15 tracked PNGs decoded; all 12 plot functions rendered and decoded to a temporary directory. The connectivity timing PNG was regenerated from current code and CSV and matched the temporary render pixel-for-pixel |
| Hardware execution, noise-model fidelity, and physical runtime | Not in project scope | No hardware or noise-model evidence is present; none was inferred |
| External PR review or team-member confirmation | Not performed | Audit was confined to the local repository and its recorded Git history |

## 4. Findings

Severity scale: **Critical** means the project cannot safely or correctly be used; **High** means a major result or workflow is invalid; **Medium** means a material correctness, interpretation, or presentation issue; **Low** means a limited reproducibility or maintainability issue; **Informational** records scope or context without indicating a defect.

### Confirmed defects corrected

| Severity | Evidence and impact | Resolution |
|---|---|---|
| Medium | `analysis/data_loader.py` claimed to audit Python versions and layouts, but its compatibility grouping key included neither. Datasets with the same Qiskit version but different Python versions/layouts could be marked compatible, which is unsafe for timing comparisons. | Added Python version, initial layout, and routing method to the compatibility signature; missing Python metadata is represented as `unknown`; added regression tests. Notes now call out Python-version differences. |
| Medium | `experiments/connectivity/CONNECTIVITY_FINDINGS.md` reported Linear Opt 0 median as 5.49 ms and the difference from Fully Connected as 0.17 ms (3.2%). The current CSV’s five Linear Opt 0 trials have median **6.6507 ms**; Fully Connected has median **5.3233 ms**. | Corrected the report to **6.65 ms**, **+1.33 ms (+24.9%)**. Also removed unverified cold-start/causal explanations for timing differences and documented the outlier cause as unknown. |
| Medium | `plots/connectivity/connectivity_transpilation_time.png` had a linear axis spanning to the observed 4.59-second trial, making the other timing points unreadable near zero. | Changed the plot generator to a labeled logarithmic y-axis and regenerated the canonical PNG from the current code and CSV; visually reviewed the result. |
| Low | `src/experiment_runner.py` used a path relative to the caller’s current directory for `results/qtrace_results.csv`; importing and saving from another working directory could write the canonical file elsewhere. | Anchored the output path to the repository root and added a regression test for the resolved path. |
| Low | README’s license section referred readers to a nonexistent `LICENSE` file. | README now states that the repository does not declare a license and warns against assuming reuse permission. |

### Confirmed limitations and unresolved risks

| Severity | Evidence and impact | Status |
|---|---|---|
| Medium | The three CSVs do not all describe one timing environment. `qtrace_results.csv` and `optimization_experiments.csv` record Qiskit 2.5.2 / Python 3.14.4; `connectivity_experiments.csv` records Qiskit 2.5.1 / Python 3.14.2. Do not pool their timings. | Documented in the integrated report and compatibility audit; structural results agree across corresponding configurations. |
| Medium | Five trials per configuration and fixed transpiler seed provide only exploratory timing evidence. Connectivity Linear Opt 0 includes a **4.587496-second** observation among approximately 5–7 ms trials; its cause is unknown. The OS/CPU/host and process-load protocol are not recorded in the CSV. | Preserved and called out; no trial was discarded. Runtime conclusions remain preliminary. |
| Low | `DataLoader` checks required columns, parses values, and checks within-configuration structural consistency, but does not enforce the full expected configuration/trial matrix, unique trial IDs, positive finite times, or uniform metadata. | The checked-in datasets pass independent completeness checks. Additional semantic validation and tests are recommended before accepting arbitrary future CSVs. |
| Low | Plot generation has no automated test suite. Temporary smoke checks passed, but future figure/data regressions would not be caught by pytest. | Recommended as follow-up; no plotting dependency was added. |
| Informational | The project has no declared license file. | Accurately disclosed in README; maintainers must choose licensing terms if redistribution rights need to be explicit. |

No Critical or High severity defect was found. The five-trial sample and unrecorded host conditions limit timing reproducibility, but do not invalidate the measured structural counts or the QAOA distribution check.

## 5. Fixes Applied

| File | Change |
|---|---|
| `analysis/data_loader.py` | Compatibility keys now distinguish Python version, initial layout, and routing method; missing Python metadata is handled safely; Python differences produce an audit note. |
| `tests/test_data_loader.py` | Added regression coverage for Python-version grouping and absent Python-version metadata. |
| `src/experiment_runner.py` | Resolve the primary CSV output path from the repository root rather than current working directory. |
| `tests/test_experiment_runner.py` | Added a check that the primary results path is repository-anchored. |
| `experiments/connectivity/CONNECTIVITY_FINDINGS.md` | Corrected the saved-data median and derived comparison; removed unsupported causal wording for timing; clarified that the outlier cause is unknown. |
| `experiments/connectivity/plot_connectivity.py` | Use a labeled logarithmic time axis so the 4.59-second outlier does not flatten the millisecond-scale observations. |
| `plots/connectivity/connectivity_transpilation_time.png` | Regenerated only this timing figure from the corrected plotting function and current connectivity CSV; confirmed it matches a temporary render pixel-for-pixel. |
| `README.md` | Replace the broken `LICENSE` reference with the actual no-license status. |
| `FINAL_AUDIT_REPORT.md` | Added this audit record. |

No CSV or experiment result was overwritten. No experiment runner or plotting script entry point was run. Plot functions were called directly with temporary output paths during audit validation; the later requested regeneration changed only `plots/connectivity/connectivity_transpilation_time.png`.

## 6. Validation Results

### Environment

Validation used the repository’s `.venv` on Windows 64-bit:

- Python **3.14.4**
- Qiskit **2.5.2**
- pandas **3.0.6**
- NumPy **2.5.4**
- Matplotlib **3.11.2**
- pytest **9.1.1**

`requirements.txt` pins the runtime libraries used by the project. It does not pin pytest or specify a Python-version constraint; README setup installs pytest separately.

### Checks run

| Command/check | Result |
|---|---|
| `.venv\Scripts\python.exe -m pytest -q` | **Passed: 31 tests** (3.44 seconds on final run) |
| `.venv\Scripts\python.exe -m pytest -v` | **Passed: 31 tests** (3.92 seconds during final working-tree validation) |
| `.venv\Scripts\python.exe -m src.validate_qaoa` | **Passed**: expected value, optimal probability, and all eight distribution checks passed |
| `.venv\Scripts\python.exe -m compileall -q analysis experiments src tests` | **Passed**: no syntax/bytecode compilation errors |
| DataLoader audit over all three CSVs | **Passed**: 40, 41, and 40 rows; eight compiled configurations per file; no loader validation errors |
| Independent completeness check | **Passed**: each compiled configuration has five records with trial IDs 1–5 and identical structural metrics across its trials |
| `results/tradeoff_analysis.md` consistency | **Passed**: exact match to a fresh in-memory render from `results/qtrace_results.csv` |
| Primary Pareto calculation | **Passed**: `fully_connected / Opt 0` is the sole frontier member for the documented three minimized objectives |
| Existing PNG integrity | **Passed**: all 15 tracked PNGs opened and decoded |
| Temporary plot smoke check | **Passed**: all 12 integrated, connectivity, and optimization plot functions generated decodable PNGs under a temporary directory; temporary files were removed |
| `git diff --check` | **Passed**: no whitespace errors |
| Connectivity timing PNG validation | **Passed**: PNG opens as 1750 × 1250 RGBA; pixel-for-pixel identical to a temporary render from `plot_transpilation_time()` using `results/connectivity_experiments.csv`; logarithmic axis label, title, series, and legend visually reviewed |

The first temporary-plot attempt used the host’s restricted system temp directory and failed on file permissions. Repeating with a temporary directory inside the repository workspace passed. Matplotlib emitted a benign font-weight fallback (`semibold` to `700`) during the temporary plot render. The later timing-plot check used a temporary output directory and confirmed the canonical PNG is identical to the current-code render.

## 7. Scientific Validation

### Benchmark and circuit

The implementation uses the four-vertex cycle (C_4), with edges ((0,1),(1,2),(2,3),(3,0)), (p=1), γ = 0.5, and β = 0.25. The cost Hamiltonian is (H_C=\sum_{(u,v)\in E}(I-Z_uZ_v)/2). The circuit uses `RZZ(-gamma)` for each edge and `RX(2*beta)` for each mixer qubit. The RZZ sign implements the cost unitary up to its global phase. The classical cut calculation reverses Qiskit’s displayed bitstring order before indexing graph vertices.

Independent execution of the project validator returned:

- Expected cut value: **2.708073 out of 4**.
- Probability of a maximum cut: **0.358374**.
- Maximum absolute output-probability difference after transpilation: between **2.776×10⁻¹⁶** and **4.163×10⁻¹⁶** across all eight configurations, below the code’s `1e-8` tolerance.

The comparison validates the measured output distributions, which is the relevant quantity for this computational-basis Max-Cut readout. It is not a hardware-fidelity test.

### Structural results

All three CSVs contain the same structural metrics for matching configurations:

| Topology | Optimization levels | 1Q gates | CX gates | Gate-only depth | Total operations |
|---|---|---:|---:|---:|---:|
| Linear | 0–1 | 12 | 14 | 18 | 30 |
| Linear | 2–3 | 17 | 12 | 18 | 33 |
| Fully connected (K_4) | 0–3 | 12 | 8 | 14 | 24 |

The logical baseline has 8 one-qubit operations, 4 RZZ operations, gate-only depth 6, and 4 measurements (16 total operations). Under the chosen `['u', 'cx']` basis and current transpilation configuration, eight CX gates were observed for fully connected connectivity. This does not establish a universal theoretical lower bound. The fully connected coupling map is an idealized complete graph; the linear map is the bidirectional chain (0-1-2-3). The non-local problem edge ((3,0)) distinguishes the two maps.

The counts and depth are structural indicators. They do not directly quantify hardware fidelity, calibrated error, pulse duration, scheduling, or quantum execution time. `explicit_swap_count == 0` does not establish that connectivity incurred no routing cost because SWAPs can be decomposed into CX gates.

## 8. Data and Figure Integrity

| Dataset | Rows | Environment recorded | Structural / record checks |
|---|---:|---|---|
| `results/qtrace_results.csv` | 40 | Qiskit 2.5.2, Python 3.14.4 | 8 × 5 compiled trials; complete trial IDs; consistent structural metrics |
| `results/optimization_experiments.csv` | 40 | Qiskit 2.5.2, Python 3.14.4 | 8 × 5 compiled trials; complete trial IDs; consistent structural metrics |
| `results/connectivity_experiments.csv` | 41 | Qiskit 2.5.1, Python 3.14.2 | 40 compiled trials plus one baseline; 8 × 5 compiled trials; complete IDs and consistent structural metrics |

The primary dataset and dedicated optimization dataset agree structurally but have different timing medians despite the same recorded Qiskit/Python versions (for example, Fully Connected Opt 0 is 8.74 ms versus 5.99 ms; Linear Opt 0 is 13.24 ms versus 4.28 ms). The host and OS are not encoded in those CSV records, so these timings must remain attached to their dataset and should not be pooled. The connectivity dataset has different software versions and its distinct timing outlier. The integrated report correctly uses `qtrace_results.csv` as its primary quantitative dataset; `results/tradeoff_analysis.md` matches the same source exactly.

All existing PNGs were confirmed readable. Temporary regenerations exercised all plot functions against their intended datasets. The tracked `plots/connectivity/connectivity_transpilation_time.png` was regenerated using the current `plot_transpilation_time()` function and `results/connectivity_experiments.csv`. Its logarithmic y-axis is labeled, the title identifies median and min–max with N=5, all eight configurations and ranges are visible, and the legend is readable. It retains the 4.59-second maximum; the cause of that outlier remains unknown.

## 9. Limitations

- The benchmark covers one four-qubit, one-layer QAOA instance; it does not establish behavior for larger circuits, other graphs, or other algorithms.
- Timing uses only five trials per cell, a fixed transpiler seed, no documented warm-up protocol, and no recorded CPU/host/process-load details. Runtime comparisons are preliminary and environment-sensitive.
- The connectivity dataset contains a single large outlier. Its cause is unknown and it was retained.
- The loader does not yet reject incomplete trial matrices or duplicate trial IDs for arbitrary future datasets, even though all current datasets passed those checks independently.
- No hardware backend execution, noise-model comparison, physical error-rate estimate, or quantum-advantage analysis was performed.
- No project license is declared in the repository.
- The connectivity, optimization, and integrated plots have temporary smoke validation, but no automated plotting tests are in the committed suite.

## 10. Project Quality Assessment

**Strengths:** The project separates baseline, experiment runners, analysis, and plotting; stores per-trial CSV data; fixes important transpiler factors (basis, layout, seed, optimization level); reports structural metrics separately from classical compile time; includes a reproducible statevector validator; computes Pareto frontiers with strict minimization semantics; and uses cautious scope language in its integrated analysis. The tests exercise actual transpilation and the result count is now independently verified.

**Weaknesses:** Timing evidence is statistically small and has environment/run-to-run variation; metadata does not identify host hardware or a warm-up protocol; CSV validation does not yet enforce all completeness/uniqueness invariants; plot code has no persistent automated smoke tests. The repository also has no license file.

## 11. Suggested Improvements

### Next reproducibility improvements

1. Preserve per-run environment provenance (OS, CPU/host class, software versions, seed, and timing protocol) whenever generating new timing datasets.

### High value

3. Extend `DataLoader` validation to enforce unique `(experiment_id, trial_id)` rows, expected topology/optimization/trial coverage, finite nonnegative timings, and stable run metadata; add malformed/incomplete CSV tests.
4. Add plotting smoke tests that write to `tmp_path`, assert expected labels/scales/series, and never overwrite canonical artifacts.
5. Define a warm-up and repeated-run protocol, increase trial counts, and report robust summaries/dispersion before making timing comparisons.
6. Pin the supported Python version and include the test dependency in a documented development dependency set or lock file.

### Optional research extensions

7. Expand to multiple graph sizes, graph families, QAOA depths, transpiler seeds, and realistic coupling maps.
8. Add a calibrated noise model or hardware execution only if the project intends to make fidelity or device-performance claims.
9. Add a project license only after the team selects and confirms the intended terms.

## 12. Final Readiness Verdict

Q-TRACE is **ready for an academic demonstration and static submission** of its code path, QAOA calculations, benchmark-specific structural resource findings, and reviewed connectivity timing figure. The reproduced results and 31 passing tests support that use. Retain the report’s clear caveats about five-trial timing, the unknown outlier cause, and environment differences. The project supports no claim about physical hardware performance, improved fidelity, a universal gate lower bound, or quantum advantage.
