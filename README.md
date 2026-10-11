# VLAudit

**Robot-policy evaluation diagnostics, from rollout logs to actionable inspection.**

[**Launch Web App**](https://vlaudit.streamlit.app/) · [**GitHub Repository**](https://github.com/kessleraqu/vla_inspect)

VLAudit is an open-source diagnostic tool for inspecting recorded robot-policy evaluations, including vision-language-action (VLA) policy rollouts.

It helps researchers and developers understand *what happened during an episode* using trajectory metrics, visualizations, and heuristic warnings.

VLAudit analyzes recorded evaluations. It does **not** run robot simulations, execute VLA models, or determine the root cause of failures automatically.

## Features

- **Episode analysis:** inspect JSONL robot evaluation recordings.
- **Trajectory metrics:** path length, displacement, path-to-displacement ratio, and motion statistics.
- **Gripper analysis:** detect frequent changes in gripper commands.
- **Heuristic warnings:** flag stalling, excessive switching, and inefficient trajectories.
- **Evaluation reports:** summarize successes and failures across episode files.
- **Web interface:** upload an episode and optionally its video.
- **Command-line interface:** analyze episodes directly or as part of evaluation workflows.
- **Docker support:** run the CLI without installing project dependencies into your local Python environment.

## Online Web App

Use VLAudit without installing anything:

**https://vlaudit.streamlit.app/**

Upload a supported JSONL episode to see diagnostic metrics, warnings, and timelines. An associated video can be uploaded for manual inspection.

The current web interface focuses on individual episodes.

## Installation

Requires Python 3.11 or newer.

```bash
git clone https://github.com/kessleraqu/vla_inspect.git
cd vla_inspect

python3 -m venv .venv
source .venv/bin/activate

python -m pip install '.[web,plots]'
```

For development, use `python -m pip install -e '.[web,plots,dev]'` instead.

## Command-Line Interface

Analyze one episode:

```bash
vlaudit analyze /path/to/episode.jsonl
```

Summarize an evaluation directory:

```bash
vlaudit report /path/to/results
```

Export a report:

```bash
vlaudit report /path/to/results --output report.json
```

See available commands with `vlaudit --help`.

The previous command name, `vla-inspect`, is retained for compatibility.

## Docker

Docker is the recommended option for using the packaged CLI without setting up a Python environment.

Build the image locally:

```bash
docker build -t vlaudit:dev .
```

Check the CLI:

```bash
docker run --rm vlaudit:dev --help
```

Analyze local evaluation results:

```bash
docker run --rm \
  -v "/absolute/path/to/results:/data:ro" \
  vlaudit:dev report /data
```

The `-v` option makes the host's results directory accessible inside the container as `/data`. The `:ro` suffix mounts it read-only.

After the first official release is published and its container package is public, the corresponding image will be available as:

`ghcr.io/kessleraqu/vlaudit:v0.1.0`

## Supported Input

The initial version has been tested with JSONL evaluation episodes produced by the [VLA Evaluation Harness](https://github.com/allenai/vla-evaluation-harness), including LIBERO evaluations.

Each nonempty JSONL line represents an episode timestep with fields including:

- `step`: timestep identifier.
- `state`: robot state array containing at least the end-effector XYZ position.
- `action`: action array containing at least seven values, including the gripper command.

Other datasets, robot representations, or benchmarks may require conversion.

## Testing

Install development dependencies:

```bash
python -m pip install -e '.[web,plots,dev]'
python -m pytest -v
```

On systems where external ROS pytest plugins interfere with testing:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -v
```

GitHub Actions runs automated tests on pushes and pull requests.

## Limitations

VLAudit's diagnostic rules are heuristic. For example, frequent gripper switching suggests a behavior worth inspecting, but does not prove that the policy itself is faulty.

Thresholds and trajectory comparisons may not generalize across robots, control frequencies, coordinate conventions, or benchmarks.

VLAudit currently does not provide validated automatic root-cause analysis or general-purpose video understanding.

## License

MIT License. See [LICENSE](LICENSE).

Third-party benchmarks, datasets, model weights, and dependencies retain their respective licenses.