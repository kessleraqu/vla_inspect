import json
import math
import sys
from pathlib import Path


def distance(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def parse_jsonl(text):
    steps = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON on line {line_number}"
            ) from error

        if not isinstance(record, dict):
            raise ValueError(
                f"Line {line_number} must contain a JSON object"
            )

        steps.append(record)

    if not steps:
        raise ValueError("The rollout file is empty.")

    return steps


def analyze_steps(steps):
    # Check that each record contains the data we need.
    for index, record in enumerate(steps):
        state = record.get("state")
        action = record.get("action")

        if not isinstance(state, list) or len(state) < 3:
            raise ValueError(f"Invalid state at record {index}")

        if not isinstance(action, list) or len(action) < 7:
            raise ValueError(f"Invalid action at record {index}")

    # Extract robot positions and gripper commands.
    positions = [record["state"][:3] for record in steps]
    gripper = [record["action"][6] for record in steps]

    step_numbers = [
        record.get("step", index)
        for index, record in enumerate(steps)
    ]

    # Calculate end-effector movement.
    movements = [
        distance(positions[i - 1], positions[i])
        for i in range(1, len(positions))
    ]

    path_length = sum(movements)
    displacement = distance(positions[0], positions[-1])

    stall_fraction = (
        sum(m < 0.001 for m in movements) / len(movements)
        if movements else 0.0
    )

    # Count gripper command changes.
    gripper_toggles = sum(
        gripper[i] != gripper[i - 1]
        for i in range(1, len(gripper))
    )

    gripper_toggle_rate = (
        gripper_toggles / (len(gripper) - 1)
        if len(gripper) > 1 else 0.0
    )

    path_ratio = (
        path_length / displacement
        if displacement > 1e-6 else None
    )

    # Detect suspicious behaviors.
    warnings = []

    if gripper_toggle_rate > 0.15:
        warnings.append(
            f"Excessive gripper switching "
            f"({gripper_toggle_rate:.1%} of transitions)"
        )

    if stall_fraction > 0.05:
        warnings.append(
            f"Frequent low-motion steps "
            f"({stall_fraction:.1%} stalled)"
        )

    if path_ratio is not None and path_ratio > 2.5:
        warnings.append(
            f"High path-to-displacement ratio "
            f"({path_ratio:.2f}x), suggesting meandering or reversals"
        )

    if path_ratio is None and path_length > 0.1:
        warnings.append(
            "Robot moved but ended near its starting position"
        )

    metrics = {
        "success": any(record.get("success", False) for record in steps),
        "steps": len(steps),
        "total_reward": sum(record.get("reward", 0) for record in steps),
        "path_length": path_length,
        "displacement": displacement,
        "lowest_z": min(p[2] for p in positions),
        "highest_z": max(p[2] for p in positions),
        "start_position": positions[0],
        "end_position": positions[-1],
        "gripper_toggles": gripper_toggles,
        "gripper_toggle_rate": gripper_toggle_rate,
        "stall_fraction": stall_fraction,
        "path_ratio": path_ratio,
    }

    timeline = {
        "step": step_numbers,
        "x": [p[0] for p in positions],
        "y": [p[1] for p in positions],
        "z": [p[2] for p in positions],
        "gripper": gripper,
    }

    return {
        "metrics": metrics,
        "warnings": warnings,
        "timeline": timeline,
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_rollout.py <episode.jsonl>")
        sys.exit(1)

    try:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
        steps = parse_jsonl(text)
        result = analyze_steps(steps)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Error: {error}")
        sys.exit(1)

    m = result["metrics"]

    print("\n=== VLA Rollout Report ===")
    print(f"Result: {'SUCCESS' if m['success'] else 'FAIL'}")
    print(f"Steps: {m['steps']}")
    print(f"Total reward: {m['total_reward']:.3f}")

    print("\nEnd-effector motion:")
    print(f"  Start position: {m['start_position']}")
    print(f"  End position:   {m['end_position']}")
    print(f"  Path length:    {m['path_length']:.3f} m")
    print(f"  Net displacement: {m['displacement']:.3f} m")
    print(f"  Lowest Z:       {m['lowest_z']:.3f} m")
    print(f"  Highest Z:      {m['highest_z']:.3f} m")

    print("\nBehavior:")
    print(f"  Gripper command toggles: {m['gripper_toggles']}")
    print(f"  Stall fraction: {m['stall_fraction']:.1%}")

    print("\nHeuristic diagnostics:")
    if result["warnings"]:
        for warning in result["warnings"]:
            print(f"  WARNING: {warning}")
    else:
        print("  No heuristic warnings detected.")


if __name__ == "__main__":
    main()