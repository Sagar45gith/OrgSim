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
