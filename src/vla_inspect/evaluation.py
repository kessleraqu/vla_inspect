from pathlib import Path

from .analyze_rollout import parse_jsonl, analyze_steps


def load_evaluation(results_dir):
    root = Path(results_dir)

    if not root.is_dir():
        raise ValueError(f"Directory not found: {root}")

    # Locate episode recordings.
    episode_root = root / "episodes"

    if not episode_root.is_dir():
        episode_root = root

    files = sorted(episode_root.rglob("*.jsonl"))

    if not files:
        raise ValueError("No JSONL episodes found.")

    episodes = []
    skipped = []

    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
            steps = parse_jsonl(text)
            analysis = analyze_steps(steps)

        except (OSError, ValueError, TypeError, KeyError) as error:
            skipped.append({
                "file": str(file),
                "error": str(error),
            })
            continue

        video = file.with_suffix(".mp4")

        episodes.append({
            "file": str(file.relative_to(root)),
            "benchmark": file.parent.name,
            "video": str(video) if video.exists() else None,
            "metrics": analysis["metrics"],
            "warnings": analysis["warnings"],
        })

    if not episodes:
        raise ValueError("No valid episodes could be analyzed.")

    successes = sum(
        episode["metrics"]["success"]
        for episode in episodes
    )

    return {
        "summary": {
            "episodes": len(episodes),
            "successes": successes,
            "failures": len(episodes) - successes,
            "success_rate": successes / len(episodes),
        },
        "episodes": episodes,
        "skipped": skipped,
    }