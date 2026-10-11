import json
from pathlib import Path

import typer

from .analyze_rollout import parse_jsonl, analyze_steps
from .evaluation import load_evaluation


app = typer.Typer(
    help="Inspect and diagnose robot policy rollouts."
)


@app.command()
def analyze(episode: Path):
    """Analyze one robot rollout."""

    try:
        text = episode.read_text(encoding="utf-8")
        steps = parse_jsonl(text)
        result = analyze_steps(steps)

    except (OSError, ValueError, TypeError, KeyError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)

    metrics = result["metrics"]

    typer.echo("\n=== Episode Report ===")
    typer.echo(f"Steps: {metrics['steps']}")
    typer.echo(f"Success: {metrics['success']}")
    typer.echo(f"Path length: {metrics['path_length']:.3f} m")
    typer.echo(f"Gripper toggles: {metrics['gripper_toggles']}")

    for warning in result["warnings"]:
        typer.echo(f"WARNING: {warning}")


@app.command()
def report(
    directory: Path,
    output: Path | None = typer.Option(
        None, "--output", "-o"
    ),
):
    """Analyze an entire benchmark results directory."""

    try:
        result = load_evaluation(directory)

    except (OSError, ValueError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)

    summary = result["summary"]

    typer.echo("\n=== VLA Evaluation Report ===")
    typer.echo(f"Episodes: {summary['episodes']}")
    typer.echo(f"Successes: {summary['successes']}")
    typer.echo(f"Failures: {summary['failures']}")
    typer.echo(f"Imported success rate: {summary['success_rate']:.1%}")

    for episode in result["episodes"]:
        status = (
            "SUCCESS"
            if episode["metrics"]["success"]
            else "FAIL"
        )

        typer.echo(f"\n{status}: {episode['file']}")

        for warning in episode["warnings"]:
            typer.echo(f"  WARNING: {warning}")

    if result["skipped"]:
        typer.echo(f"\nSkipped files: {len(result['skipped'])}")

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, indent=2),
            encoding="utf-8",
        )
        typer.echo(f"\nSaved report to {output}")