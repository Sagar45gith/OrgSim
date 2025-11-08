import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import plotly.express as px
from tasks import get_demo_tasks
from agents import get_demo_agents, get_agent_decision_prompt


class GeminiModelWrapper:
    """Light wrapper exposing a generate_content(prompt=..., generation_config=...) method.

    This keeps the rest of the app-facing API stable while using the genai SDK
    under the hood with a fixed model name.
    """
    def __init__(self, model_name: str = "gemini-1.5-flash-latest"):
        self.model_name = model_name

    def generate_content(self, prompt: str, generation_config=None, **kwargs):
        # Call genai.generate with the configured model name. Pass generation_config
        # when available; fall back to calling without it if the client raises.
        if generation_config is not None:
            return genai.generate(model=self.model_name, prompt=prompt, generation_config=generation_config, **kwargs)
        return genai.generate(model=self.model_name, prompt=prompt, **kwargs)


def run_simulation_tick() -> None:
    """Advance the simulation by one day.

    This increments `st.session_state.current_day` (initializing it to 0 if
    missing) and appends a simple log entry to `st.session_state.event_log`
    (initializing it as a list if missing).
    """
    # Ensure session state keys exist
    if "current_day" not in st.session_state:
        st.session_state.current_day = 0
    if "event_log" not in st.session_state:
        st.session_state.event_log = []

    # Increment the day
    st.session_state.current_day += 1

    # Log the new day
    entry = {
        "type": "day_start",
        "day": st.session_state.current_day,
        "message": f"Day {st.session_state.current_day} started.",
    }
    st.session_state.event_log.append(entry)

    # Update metrics: count completed tasks and append to metrics_history DataFrame
    tasks = st.session_state.get("tasks", {})
    try:
        tasks_completed = sum(1 for t in tasks.values() if t.get("status") == "done")
    except Exception:
        tasks_completed = 0

    new_row = pd.DataFrame([{"day": st.session_state.current_day, "tasks_completed": tasks_completed}])

    if "metrics_history" not in st.session_state or not isinstance(st.session_state.metrics_history, pd.DataFrame):
        st.session_state.metrics_history = new_row
    else:
        try:
            st.session_state.metrics_history = pd.concat([st.session_state.metrics_history, new_row], ignore_index=True)
        except Exception:
            st.session_state.metrics_history = new_row

def main():
    st.set_page_config(page_title="OrgSim GenAI Demo", layout="wide")
    st.title("OrgSim — Streamlit + Google Generative AI (demo)")

    st.markdown(
        "This minimal app imports the requested libraries and shows a small DataFrame and Plotly chart."
    )

    # Initialize session state defaults
    if "current_day" not in st.session_state:
        st.session_state.current_day = 0
    if "agents" not in st.session_state:
        st.session_state.agents = {}
    if "tasks" not in st.session_state:
        st.session_state.tasks = {}
    if "event_log" not in st.session_state:
        st.session_state.event_log = []
    if "metrics_history" not in st.session_state or not isinstance(st.session_state.metrics_history, pd.DataFrame):
        st.session_state.metrics_history = pd.DataFrame(columns=["day", "tasks_completed"])

    with st.sidebar:
        st.title("OrgSim")
        st.header("Configuration")
        api_key = st.text_input("Google API Key (optional)", type="password")
        show_json = st.checkbox("Show sample JSON", value=True)

        # Gemini API key input and client initialization
        gemini_api_key = st.text_input("Gemini API Key (optional)", type="password")
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                # Create a model wrapper for gemini-1.5-flash-latest and store in session
                st.session_state.gemini_model = GeminiModelWrapper("gemini-1.5-flash-latest")
                st.session_state.api_key_set = True
                st.sidebar.success("Gemini model configured")
            except Exception as e:
                st.sidebar.error(f"Failed to configure Gemini model: {e}")
        # Load demo scenario button
        if st.button("Load Demo Scenario"):
            try:
                st.session_state.agents = get_demo_agents()
                st.session_state.tasks = get_demo_tasks()
                st.session_state.current_day = 0
                st.session_state.event_log = []
                st.session_state.metrics_history = pd.DataFrame(columns=["day", "tasks_completed"])
                st.success("Demo scenario loaded: agents, tasks, and simulation state initialized.")
            except Exception as e:
                st.error(f"Failed to load demo scenario: {e}")

        # Advance 1 Day button: requires API key set
        if st.button("Advance 1 Day"):
            if st.session_state.get("api_key_set"):
                try:
                    run_simulation_tick()
                    # Try to rerun the app; prefer st.rerun() if available
                    try:
                        st.rerun()
                    except Exception:
                        # Fallback to experimental rerun for older Streamlit versions
                        try:
                            st.experimental_rerun()
                        except Exception:
                            # If rerun isn't available, just show a notice
                            st.info("Advanced one day. Please refresh the app to see updates.")
                except Exception as e:
                    st.error(f"Error advancing simulation: {e}")
            else:
                st.warning("Gemini API key not set. Please enter the Gemini API Key in the sidebar to enable model-driven actions.")

    # NOTE: We don't call the genai API here — only configure the client if a key is present.
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.sidebar.success("GenAI client configured")
        except Exception as e:
            st.sidebar.error(f"Failed to configure GenAI client: {e}")

    # Build backlog summary from demo tasks: join the names of tasks in 'backlog' status
    try:
        tasks = get_demo_tasks()
        backlog_names = [t.get("name", "") for t in tasks.values() if t.get("status") == "backlog"]
        backlog_summary = ", ".join(backlog_names)
    except Exception:
        backlog_summary = ""

    # Ensure agents exist in session state and loop through them
    if "agents" not in st.session_state:
        try:
            st.session_state.agents = get_demo_agents()
        except Exception:
            st.session_state.agents = {}

    st.subheader("Agents")

    # Ensure tasks are stored in session state so agents can reference them
    if "tasks" not in st.session_state:
        try:
            st.session_state.tasks = get_demo_tasks()
        except Exception:
            st.session_state.tasks = {}

    # Ensure event_log exists
    if "event_log" not in st.session_state:
        st.session_state.event_log = []

    for agent_id, agent in st.session_state.agents.items():
        # Display a concise summary for each agent
        role = agent.get("role", "")
        skills = ", ".join(agent.get("skills", []))
        morale = agent.get("morale")
        fatigue = agent.get("fatigue")
        st.write(f"{agent_id}: {role} — skills: {skills}; morale: {morale}; fatigue: {fatigue}")

        # If the agent is currently assigned to a task, they are busy.
        current_task_id = agent.get("current_task")
        if current_task_id is not None:
            tasks = st.session_state.tasks

            # Find the task in session_state.tasks
            task = tasks.get(current_task_id)
            if task is None:
                # Task not found; log and clear the agent's current_task to avoid stuck states
                st.session_state.event_log.append({
                    "type": "error",
                    "agent": agent_id,
                    "message": f"Assigned task {current_task_id} not found for agent {agent_id}. Clearing assignment.",
                })
                agent["current_task"] = None
                continue

            # Decrement task complexity
            try:
                task["complexity"] = int(task.get("complexity", 0)) - 1
            except Exception:
                task["complexity"] = 0

            if task["complexity"] <= 0:
                # Task finished
                task["complexity"] = 0
                task["status"] = "done"
                agent["current_task"] = None
                st.session_state.event_log.append({
                    "type": "task_finished",
                    "agent": agent_id,
                    "task_id": current_task_id,
                    "message": f"Agent {agent_id} finished task {current_task_id}.",
                })
            else:
                # Task still ongoing
                st.session_state.event_log.append({
                    "type": "task_continued",
                    "agent": agent_id,
                    "task_id": current_task_id,
                    "message": f"Agent {agent_id} continues work on {current_task_id}; remaining complexity {task['complexity']}.",
                })

            # Move to next agent after processing a busy agent
            continue

        # If the agent is idle (no current task), ask the Gemini model for a decision
        if current_task_id is None:
            prompt = get_agent_decision_prompt(agent, backlog_summary)

            model = st.session_state.get("gemini_model")
            decision = None

            if model and hasattr(model, "generate_content"):
                try:
                    # Request JSON response using the genai GenerationConfig
                    gen_cfg = genai.types.GenerationConfig(response_mime_type="application/json")
                    response = model.generate_content(prompt=prompt, generation_config=gen_cfg)

                    # Extract response text; the client may expose .text or a dict
                    response_text = None
                    if hasattr(response, "text"):
                        response_text = getattr(response, "text")
                    elif isinstance(response, dict):
                        response_text = response.get("text") or response.get("content")
                    else:
                        response_text = str(response)

                    # Parse the JSON decision from response.text
                    try:
                        decision = json.loads(response_text) if response_text else None
                    except Exception:
                        decision = None
                        st.session_state.event_log.append({
                            "type": "parse_error",
                            "agent": agent_id,
                            "message": "Model response could not be parsed as JSON",
                            "raw": response_text,
                        })
                except Exception as e:
                    st.session_state.event_log.append({
                        "type": "model_error",
                        "agent": agent_id,
                        "message": f"Model call failed: {e}",
                    })
            else:
                st.session_state.event_log.append({
                    "type": "no_model",
                    "agent": agent_id,
                    "message": "No Gemini model configured in session_state.gemini_model; skipping decision.",
                })

            # If we got a valid decision, act on it
            if isinstance(decision, dict):
                action = decision.get("action")
                task_id = decision.get("task_id")
                rationale = decision.get("rationale", "")

                if action == "pick" and task_id:
                    task = st.session_state.tasks.get(task_id)
                    if task and task.get("status") == "backlog":
                        # Assign task to agent
                        agent["current_task"] = task_id
                        task["status"] = "in_progress"
                        # Set the assigned_to field on the task
                        task["assigned_to"] = agent_id

                        # Log the agent's rationale explicitly
                        st.session_state.event_log.append({
                            "type": "rationale",
                            "agent": agent_id,
                            "task_id": task_id,
                            "rationale": rationale,
                        })

                        st.session_state.event_log.append({
                            "type": "task_assigned",
                            "agent": agent_id,
                            "task_id": task_id,
                            "message": f"Agent {agent_id} picked task {task_id}.",
                        })
                    else:
                        st.session_state.event_log.append({
                            "type": "assign_failed",
                            "agent": agent_id,
                            "task_id": task_id,
                            "message": f"Agent {agent_id} attempted to pick {task_id} but it was unavailable.",
                        })
                elif action == "continue":
                    st.session_state.event_log.append({
                        "type": "continue_requested",
                        "agent": agent_id,
                        "message": f"Agent {agent_id} requested to continue but had no task. Rationale: {rationale}",
                    })
                elif action == "idle":
                    st.session_state.event_log.append({
                        "type": "idle",
                        "agent": agent_id,
                        "message": f"Agent {agent_id} remains idle. Rationale: {rationale}",
                    })
                else:
                    st.session_state.event_log.append({
                        "type": "invalid_decision",
                        "agent": agent_id,
                        "raw_decision": decision,
                        "message": "Model returned an invalid or unknown action.",
                    })
            # If no decision, we simply continue to next agent
            continue


    st.header("Sample data and visualization")

    # Create a small sample dataframe
    df = pd.DataFrame({"category": ["A", "B", "C", "D"], "value": [10, 23, 17, 9]})
    st.subheader("Sample DataFrame")
    st.dataframe(df)

    # Plot with Plotly Express
    fig = px.bar(df, x="category", y="value", title="Sample bar chart")
    st.plotly_chart(fig, use_container_width=True)

    if show_json:
        st.subheader("Sample JSON")
        sample = {"project": "OrgSim", "features": ["streamlit", "genai", "plotly"], "meta": {"version": "0.1"}}
        st.json(sample)


if __name__ == "__main__":
    main()
