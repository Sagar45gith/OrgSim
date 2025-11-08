"""Demo agents helper.

Provides get_demo_agents() which returns a dictionary of agent dictionaries.
Each agent value contains: role, skills (list[str]), morale, fatigue,
current_task (None) and log (string).
"""
from typing import Dict, Any


def get_demo_agents() -> Dict[str, Dict[str, Any]]:
    """Return a dictionary of demo agents keyed by agent ID.

    Each agent dictionary has the following keys:
    - role: str
    - skills: list[str]
    - morale: int
    - fatigue: int
    - current_task: None (initially)
    - log: str

    Example keys: 'A-01', 'A-02', ...
    """
    agents = {
        "A-01": {
            "role": "Engineer",
            "skills": ["coding", "debugging", "design"],
            "morale": 80,
            "fatigue": 10,
            "current_task": None,
            "log": "Just hired.",
        },
        "A-02": {
            "role": "Product Manager",
            "skills": ["roadmapping", "communication", "prioritization"],
            "morale": 75,
            "fatigue": 12,
            "current_task": None,
            "log": "Just hired.",
        },
        "A-03": {
            "role": "Data Analyst",
            "skills": ["pandas", "sql", "visualization"],
            "morale": 78,
            "fatigue": 8,
            "current_task": None,
            "log": "Just hired.",
        },
        "A-04": {
            "role": "Designer",
            "skills": ["ux", "ui", "prototyping"],
            "morale": 82,
            "fatigue": 9,
            "current_task": None,
            "log": "Just hired.",
        },
    }

    return agents


def get_agent_decision_prompt(agent: Dict[str, Any], backlog_summary: str) -> str:
        """Build a Gemini prompt instructing the model to decide an agent action.

        The prompt instructs the model to act as the employee described by `agent`.
        It must decide one of: 'pick', 'continue', or 'idle' and MUST return ONLY a
        single JSON object with the keys: 'action', 'task_id', and 'rationale'.

        - action: one of the strings 'pick', 'continue', or 'idle'
        - task_id: a task identifier like 'T-01' when relevant, otherwise null
        - rationale: a short explanation for the choice

        The function does not call any model; it only returns the prompt string.
        """

        role = agent.get("role", "")
        skills = agent.get("skills", [])
        morale = agent.get("morale", "")
        fatigue = agent.get("fatigue", "")
        current_task = agent.get("current_task")

        skills_str = ", ".join(skills) if isinstance(skills, (list, tuple)) else str(skills)

        prompt = f"""
You are a helpful assistant running as an employee in a workplace simulation. Act AS the employee described below and make a single decision about what to do next.

Persona:
- role: {role}
- skills: {skills_str}
- morale: {morale}
- fatigue: {fatigue}
- current_task: {current_task}

Current situation:
{backlog_summary}

Decision instructions:
- You must decide exactly one action from the following set: 'pick', 'continue', 'idle'.
    - 'pick' means choose a new task from the backlog to start working on.
    - 'continue' means continue working on the agent's current_task.
    - 'idle' means do not take or continue any task right now.
- If you choose 'pick', set 'task_id' to the selected task's ID (format like 'T-01').
- If you choose 'continue', set 'task_id' to the current task ID (or null if no current task).
- If you choose 'idle', set 'task_id' to null.

Output requirements (MANDATORY):
- Return ONLY a single JSON object and nothing else (no prose, no code fences, no explanation).
- The JSON object MUST contain exactly these three keys: "action", "task_id", and "rationale".
- "action" must be one of the strings: "pick", "continue", "idle".
- "task_id" must be a string task id (e.g. "T-01") when relevant, otherwise null.
- "rationale" must be a brief plain-text explanation (one or two sentences) describing why you chose the action.

Example of valid output (the model must produce exactly a JSON object like this):
{{"action": "pick", "task_id": "T-02", "rationale": "I have the skills required and moderate fatigue so I can start a new task."}}

Produce the JSON now.
"""

        return prompt
