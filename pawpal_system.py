from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str       # "low", "medium", "high"
    task_type: str      # "walk", "feeding", "meds", "grooming", "enrichment", etc.
    completed: bool = False

    def priority_value(self) -> int:
        """Convert priority string to a number for sorting (high=3, medium=2, low=1)."""
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority.lower(), 0)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __repr__(self) -> str:
        """Return a formatted string showing priority, title, duration, type, and status."""
        status = "done" if self.completed else "pending"
        return (
            f"[{self.priority.upper()}] {self.title} "
            f"({self.duration_minutes} min, {self.task_type}) — {status}"
        )


@dataclass
class Pet:
    name: str
    species: str            # "dog", "cat", "other"
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]

    def get_info(self) -> str:
        """Return a readable summary of the pet."""
        return (
            f"{self.name} ({self.species}, age {self.age}) — "
            f"{len(self.tasks)} task(s), "
            f"{len(self.get_pending_tasks())} pending"
        )


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != name]

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_all_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks across all pets."""
        return [t for t in self.get_all_tasks() if not t.completed]

    def has_time_for(self, task: Task, time_used: int) -> bool:
        """Return True if the task fits within the remaining available time."""
        return (time_used + task.duration_minutes) <= self.available_minutes


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self._remaining_minutes = owner.available_minutes
        self._plan: List[Task] = []
        self._skipped: List[Task] = []

    def generate_plan(self) -> List[Task]:
        """Sort pending tasks by priority and greedily fit them into the owner's time budget."""
        self._plan = []
        self._skipped = []
        self._remaining_minutes = self.owner.available_minutes

        pending = self.owner.get_all_pending_tasks()
        sorted_tasks = sorted(pending, key=lambda t: t.priority_value(), reverse=True)

        time_used = 0
        for task in sorted_tasks:
            if self.owner.has_time_for(task, time_used):
                self._plan.append(task)
                time_used += task.duration_minutes
            else:
                self._skipped.append(task)

        self._remaining_minutes = self.owner.available_minutes - time_used
        return self._plan

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the generated plan."""
        if not self._plan and not self._skipped:
            return "No plan generated yet. Call generate_plan() first."

        lines = [
            f"=== Daily Plan for {self.owner.name} ===",
            f"Time budget: {self.owner.available_minutes} min | "
            f"Time used: {self.owner.available_minutes - self._remaining_minutes} min | "
            f"Remaining: {self._remaining_minutes} min",
            "",
            "Scheduled tasks:",
        ]

        for i, task in enumerate(self._plan, start=1):
            lines.append(f"  {i}. {task}")

        if self._skipped:
            lines.append("")
            lines.append("Skipped tasks (did not fit in time budget):")
            for task in self._skipped:
                lines.append(f"  - {task}")
        else:
            lines.append("")
            lines.append("All tasks fit within the time budget.")

        return "\n".join(lines)

    def mark_task_complete(self, title: str) -> None:
        """Mark a scheduled task as complete by title."""
        for task in self._plan:
            if task.title == title:
                task.mark_complete()
                return
        raise ValueError(f"Task '{title}' not found in the current plan.")
