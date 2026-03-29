from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    species: str  # "dog", "cat", "other"
    age: int

    def get_info(self) -> str:
        """Return a readable summary of the pet."""
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str       # "low", "medium", "high"
    task_type: str      # "walk", "feeding", "meds", "grooming", "enrichment", etc.
    completed: bool = False

    def priority_value(self) -> int:
        """Convert priority string to a number for sorting (high=3, medium=2, low=1)."""
        pass

    def __repr__(self) -> str:
        """Return a readable string representation of the task."""
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes

    def has_time_for(self, task: Task) -> bool:
        """Return True if the task duration fits within available time."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: List[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_plan(self) -> List[Task]:
        """Sort tasks by priority, fit them into available time, return the ordered plan."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why each task was included or skipped."""
        pass
