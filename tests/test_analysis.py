import pytest

from vla_inspect.analyze_rollout import analyze_steps, parse_jsonl


def test_rollout_metrics():
    steps = [
        {
            "step": 0,
            "state": [0.0, 0.0, 1.0],
            "action": [0, 0, 0, 0, 0, 0, -1],
            "success": False,
            "reward": 0.0,
        },
        {
            "step": 1,
            "state": [0.0, 0.0, 1.0],
            "action": [0, 0, 0, 0, 0, 0, 1],
            "success": False,
            "reward": 0.0,
        },
        {
            "step": 2,
            "state": [0.1, 0.0, 1.0],
            "action": [0, 0, 0, 0, 0, 0, -1],
            "success": True,
            "reward": 1.0,
        },
    ]

    result = analyze_steps(steps)
    metrics = result["metrics"]

    assert metrics["steps"] == 3
    assert metrics["success"] is True
    assert metrics["gripper_toggles"] == 2
    assert metrics["path_length"] == pytest.approx(0.1)
    assert metrics["stall_fraction"] == pytest.approx(0.5)


def test_empty_file():
    with pytest.raises(ValueError):
        parse_jsonl("")


def test_invalid_json():
    with pytest.raises(ValueError, match="line 2"):
        parse_jsonl('{"step": 0}\nnot-valid-json\n')


def test_invalid_state():
    steps = [
        {
            "step": 0,
            "state": [1.0],
            "action": [0, 0, 0, 0, 0, 0, -1],
        }
    ]

    with pytest.raises(ValueError, match="Invalid state"):
        analyze_steps(steps)