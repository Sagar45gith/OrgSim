"""Demo tasks helper.

Provides get_demo_tasks() which returns a dictionary of task dictionaries keyed by ID.
Each task dictionary contains: name, skills_required (list[str]), complexity (int),
status (str), and assigned_to (None initially).
"""
from typing import Dict, Any


def get_demo_tasks() -> Dict[str, Dict[str, Any]]:
    """Return a dictionary of demo tasks keyed by task ID.

    Each task dictionary has the following keys:
    - name: str
    - skills_required: list[str]
    - complexity: int
    - status: str (initially 'backlog')
    - assigned_to: None (initially)
    """
    tasks = {
        "T-01": {
            "name": "Implement auth module",
            "skills_required": ["python", "security", "oauth"],
            "complexity": 3,
            "status": "backlog",
            "assigned_to": None,
        },
        "T-02": {
            "name": "Create analytics dashboard",
            "skills_required": ["pandas", "plotly", "streamlit"],
            "complexity": 2,
            "status": "backlog",
            "assigned_to": None,
        },
        "T-03": {
            "name": "Design landing page",
            "skills_required": ["ui", "ux", "figma"],
            "complexity": 2,
            "status": "backlog",
            "assigned_to": None,
        },
        "T-04": {
            "name": "Set up CI pipeline",
            "skills_required": ["ci/cd", "docker", "github-actions"],
            "complexity": 3,
            "status": "backlog",
            "assigned_to": None,
        },
    }

    return tasks
