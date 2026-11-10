import os
import streamlit as st
from dotenv import load_dotenv
from omnisight.agent import run_task
from omnisight.vision import inspect_screenshot

load_dotenv()
st.set_page_config(page_title="OmniSight RPA Agent", page_icon="🧭", layout="wide")
st.title("🧭 OmniSight")
st.subheader("Multimodal UI Self-Healing & RPA Agent")
st.caption("Describe a browser task in plain language. OmniSight plans, executes, recovers, and records the workflow.")

with st.sidebar:
    st.header("Configuration")
    st.write("AI planner:", "Enabled" if os.getenv("OPENAI_API_KEY") else "Fallback mode")
    st.write("Browser:", "Headless" if os.getenv("HEADLESS", "false").lower() == "true" else "Visible")
    st.info("For first run, keep the browser visible and use the included demo page.")
    st.markdown("[Project README](README.md)")

start_url = st.text_input("Starting URL (optional)", placeholder="http://127.0.0.1:8000/demo/index.html")
task = st.text_area(
    "What should the agent do?",
    height=130,
    placeholder="Open the demo page, fill the name field with Dharana, fill the email field with dharana@example.com, choose AI from the interest dropdown, and submit the form."
)
run = st.button("Run automation", type="primary", disabled=not task.strip())
if run:
    with st.spinner("Starting browser and executing task..."):
        try:
            result = run_task(task, start_url or None)
            st.session_state["last_result"] = result
        except Exception as exc:
            st.error(f"Could not run task: {type(exc).__name__}: {exc}")

result = st.session_state.get("last_result")
if result:
    left, right = st.columns([1, 1])
    with left:
        st.markdown("### Execution log")
        for item in result["log"]:
            st.write("• " + item)
        st.markdown("### Extracted page content")
        st.text_area("Result", result["extracted"], height=220)
    with right:
        st.markdown("### Browser screenshot")
        path = result.get("screenshot")
        if path:
            st.image(path, use_container_width=True)
            if st.button("Analyze screenshot with vision AI"):
                try:
                    st.write(inspect_screenshot(path))
                except Exception as exc:
                    st.error(f"Vision analysis failed: {exc}")
        st.markdown("### Generated action plan")
        st.json(result["plan"])
