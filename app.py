import json

import pandas as pd
import streamlit as st

from vla_inspect.analyze_rollout import analyze_steps, parse_jsonl


st.set_page_config(
    page_title="VLAudit",
    page_icon="🤖",
    layout="wide",
)

st.title("VLAudit")
st.write("Analyze robot-policy rollouts and investigate failures.")

# Let the user choose a rollout file.
uploaded_file = st.file_uploader(
    "Upload a rollout (.jsonl)",
    type=["jsonl"],
)

if uploaded_file is None:
    st.info("Upload a JSONL file to begin.")
    st.stop()

# Read the file and run our existing analyzer.
try:
    text = uploaded_file.getvalue().decode("utf-8")
    steps = parse_jsonl(text)
    result = analyze_steps(steps)

except (UnicodeError, ValueError, KeyError, TypeError) as error:
    st.error(f"Could not analyze file: {error}")
    st.stop()

metrics = result["metrics"]
timeline = result["timeline"]

# Display summary statistics.
st.subheader("Rollout summary")

if metrics["success"]:
    st.success("Result: SUCCESS")
else:
    st.error("Result: FAIL")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Steps", metrics["steps"])
col2.metric("Path length", f"{metrics['path_length']:.3f} m")
col3.metric("Gripper toggles", metrics["gripper_toggles"])
col4.metric("Stalled steps", f"{metrics['stall_fraction']:.1%}")

# Display automatic warnings.
st.subheader("Heuristic diagnostics")

if result["warnings"]:
    for warning in result["warnings"]:
        st.warning(warning)
else:
    st.success("No heuristic warnings detected.")

# Turn the recorded timeline into a table for plotting.
df = pd.DataFrame(timeline)

st.subheader("End-effector position")
st.line_chart(df.set_index("step")[["x", "y", "z"]])

st.subheader("Gripper command")
st.line_chart(df.set_index("step")[["gripper"]])

# Optional episode video.
st.subheader("Episode video")

video_file = st.file_uploader(
    "Optional: upload an MP4 recording",
    type=["mp4"],
)

if video_file is not None:
    st.video(video_file)
    st.caption(
        "Video playback is not yet synchronized with control steps."
    )

# Let users save their diagnostic results.
report = {
    "metrics": metrics,
    "warnings": result["warnings"],
}

st.download_button(
    "Download JSON report",
    data=json.dumps(report, indent=2),
    file_name="vla_inspect_report.json",
    mime="application/json",
)