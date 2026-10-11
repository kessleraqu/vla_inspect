# VLAudit

**Diagnostics for robot-policy evaluation rollouts.**

VLAudit is an early-stage, open-source tool for inspecting recorded trajectories from vision-language-action (VLA) and other robot-policy evaluations. It turns step-by-step rollout logs into readable metrics, plots, and heuristic warnings that help identify episodes worth investigating.

It provides a **command-line interface (CLI)** for repeatable analysis and a **Streamlit web interface** for interactive inspection. VLAudit analyzes existing evaluations; it does **not** run robot simulations or VLA policies itself.

> **Status:** Preparing the first `v0.1.0` release. Interfaces and supported log formats may change during early development.

## What it does

- Reads per-step **JSONL** episode logs containing robot state and action arrays.
- Reports trajectory length, displacement, path efficiency, gripper changes, and stall indicators.
- Flags potentially unusual behavior using heuristic thresholds.
- Displays position and gripper timelines in Streamlit.
- Accepts an optional episode video in the web interface.
- Summarizes multiple episodes from an evaluation-results directory through the CLI.
- Exports diagnostic information as JSON.

**Important:** A warning is a clue, not a diagnosis. Repeated gripper commands do not by themselves prove that the model, controller, or simulation interface is faulty.

## Supported input

The initial implementation has been exercised with JSONL episode logs from the [VLA Evaluation Harness](https://github.com/allenai/vla-evaluation-harness), including LIBERO/SmolVLA evaluation.

Each nonempty line is a JSON object representing one timestep.

| Field | Description |
| --- | --- |
| `state` | Array containing at least end-effector position `(x, y, z)`. |
| `action` | Array containing at least seven values: six motion components and a gripper command. |
| `step` | Timestep identifier, when recorded. |
| `reward`, `success` | Evaluation outcomes, when recorded. |

Other benchmark formats may require conversion. Metrics are not automatically normalized across robots or benchmarks.

## Installation

Requires **Python 3.11 or newer**.

```bash
git clone https://github.com/kessleraqu/vla_inspect.git
cd vla_inspect
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[web,plots]'
```

Editable installation means local Python source edits take effect without rebuilding Docker.

## Command-line usage

```bash
vlaudit --help

vlaudit analyze /path/to/episode.jsonl

vlaudit report /path/to/results

vlaudit report /path/to/results --output report.json
```

The older `vla-inspect` command is retained as a backward-compatible alias. Both point to the Typer application in `src/vla_inspect/cli.py`.

## Streamlit web interface

Run locally:

```bash
python -m streamlit run app.py
```

Open the local address printed by Streamlit, normally `http://localhost:8501`.

Upload an episode JSONL file to inspect metrics, warnings, and timelines. You can optionally upload a video and download diagnostic JSON.

A hosted Streamlit deployment also exists; its public URL will be linked here once confirmed.

## Docker

Build and run the container locally:

```bash
docker build -t vlaudit:dev .
docker run --rm -p 8502:8501 vlaudit:dev
```

Visit `http://localhost:8502`.

After the first GitHub Release has been successfully published and its Docker package made public:

```bash
docker run --rm -p 8502:8501 ghcr.io/kessleraqu/vlaudit:v0.1.0
```

Until that release is available, use the local Docker build.

## Development and tests

```bash
python -m pip install -e '.[web,plots,dev]'
python -m pytest -v
```

If external ROS-related pytest plugins interfere with your local test environment:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -v
```

GitHub Actions runs automated tests on pushes and pull requests.

## Project layout

```text
app.py                                  Streamlit interface
src/vla_inspect/cli.py                  CLI
src/vla_inspect/analyze_rollout.py      Episode diagnostics
src/vla_inspect/evaluation.py           Evaluation summaries
src/vla_inspect/plot_rollout.py         Plotting helpers
tests/                                  Automated tests
Dockerfile                              Container definition
.github/workflows/                      CI and publishing workflows
```

## Limitations

- VLAudit inspects existing logs; it does not run policies or control robots.
- The web interface currently focuses on one episode at a time.
- Heuristic thresholds may not generalize across robots, controllers, or benchmarks.
- A suspicious trajectory does not establish the root cause of failure.
- Comparisons require compatible tasks, seeds, coordinate conventions, and success criteria.

## License

MIT — see [LICENSE](LICENSE). Ensure the license file is present before the release.