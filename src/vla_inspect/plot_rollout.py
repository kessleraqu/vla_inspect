import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    if len(sys.argv) != 2:
        print("Usage: python plot_rollout.py <episode.jsonl>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    with file_path.open() as f:
        steps = [json.loads(line) for line in f if line.strip()]

    step_numbers = [step["step"] for step in steps]

    x = [step["state"][0] for step in steps]
    y = [step["state"][1] for step in steps]
    z = [step["state"][2] for step in steps]

    gripper = [step["action"][6] for step in steps]

    output_dir = Path("plots")
    output_dir.mkdir(exist_ok=True)

    plt.figure()
    plt.plot(step_numbers, x, label="X")
    plt.plot(step_numbers, y, label="Y")
    plt.plot(step_numbers, z, label="Z")
    plt.xlabel("Control step")
    plt.ylabel("Position (m)")
    plt.title("End-Effector Position")
    plt.legend()
    plt.savefig(output_dir / "position_vs_step.png")
    plt.close()

    plt.figure()
    plt.plot(step_numbers, gripper)
    plt.xlabel("Control step")
    plt.ylabel("Gripper command")
    plt.title("Gripper Command")
    plt.savefig(output_dir / "gripper_vs_step.png")
    plt.close()

    print("Saved plots/position_vs_step.png")
    print("Saved plots/gripper_vs_step.png")


if __name__ == "__main__":
    main()