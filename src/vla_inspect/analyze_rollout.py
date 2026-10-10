import json
import math
import sys
from pathlib import Path


def distance(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_rollout.py <episode.jsonl>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    with file_path.open() as f:
        steps = [json.loads(line) for line in f if line.strip()]

    if not steps:
        print("No rollout data found.")
        return

    positions = [step["state"][:3] for step in steps]

    movements = [
        distance(positions[i - 1], positions[i])
        for i in range(1, len(positions))
    ]

    path_length = sum(movements)
    displacement = distance(positions[0], positions[-1])

    z_values = [position[2] for position in positions]

    gripper_commands = [step["action"][6] for step in steps]

    gripper_toggles = sum(
        gripper_commands[i] != gripper_commands[i - 1]
        for i in range(1, len(gripper_commands))
    )

    stall_threshold = 0.001  # 1 mm

    stalled_steps = sum(
        movement < stall_threshold
        for movement in movements
    )

    stall_fraction = (
        stalled_steps / len(movements)
        if movements
        else 0.0
    )

    success = any(step["success"] for step in steps)
    total_reward = sum(step["reward"] for step in steps)

    print("\n=== VLA Rollout Report ===")
    print(f"Result: {'SUCCESS' if success else 'FAIL'}")
    print(f"Steps: {len(steps)}")
    print(f"Total reward: {total_reward:.3f}")

    print("\nEnd-effector motion:")
    print(f"  Start position: {positions[0]}")
    print(f"  End position:   {positions[-1]}")
    print(f"  Path length:    {path_length:.3f} m")
    print(f"  Net displacement: {displacement:.3f} m")
    print(f"  Lowest Z:       {min(z_values):.3f} m")
    print(f"  Highest Z:      {max(z_values):.3f} m")

    print("\nBehavior:")
    print(f"  Gripper command toggles: {gripper_toggles}")
    print(f"  Stall fraction: {stall_fraction:.1%}")


if __name__ == "__main__":
    main()