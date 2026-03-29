from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str       # "low", "medium", "high"
    task_type: str      # "walk", "feeding", "meds", "grooming", "enrichment", etc.
    completed: bool = False
    scheduled_time: str = ""        # optional "HH:MM" format, e.g. "08:30"
    recurrence: str = ""            # "", "daily", or "weekly"
    due_date: Optional[date] = None # set automatically on recurring tasks

    def priority_value(self) -> int:
        """Convert priority string to a number for sorting (high=3, medium=2, low=1)."""
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority.lower(), 0)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task":
        """Return a fresh copy of this task due on the next occurrence date."""
        intervals = {"daily": 1, "weekly": 7}
        days_ahead = intervals.get(self.recurrence, 1)
        base = self.due_date if self.due_date else date.today()
        next_due = base + timedelta(days=days_ahead)
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            task_type=self.task_type,
            scheduled_time=self.scheduled_time,
            recurrence=self.recurrence,
            due_date=next_due,
        )

    def __repr__(self) -> str:
        """Return a formatted string showing priority, title, duration, type, status, and due date."""
        status = "done" if self.completed else "pending"
        due = f", due {self.due_date}" if self.due_date else ""
        return (
            f"[{self.priority.upper()}] {self.title} "
            f"({self.duration_minutes} min, {self.task_type}) — {status}{due}"
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

    def complete_task(self, title: str) -> None:
        """Mark a task complete by title. If it recurs, append the next occurrence."""
        for task in self.tasks:
            if task.title == title and not task.completed:
                task.mark_complete()
                if task.recurrence in ("daily", "weekly"):
                    self.tasks.append(task.next_occurrence())
                return
        raise ValueError(f"No pending task named '{title}' found for {self.name}.")

    def remove_task(self, title: str) -> None:
        """Remove a task by title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return only tasks that have been completed."""
        return [t for t in self.tasks if t.completed]

    def filter_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return tasks matching the given completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def get_tasks_sorted_by_time(self) -> List[Task]:
        """Return tasks sorted by scheduled_time (HH:MM). Tasks with no time set go last."""
        return sorted(
            self.tasks,
            key=lambda t: t.scheduled_time if t.scheduled_time else "99:99"
        )

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

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks for the pet with the given name, or [] if not found."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.tasks
        return []

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

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("")
            lines.append("⚠ Conflicts detected:")
            for slot, entries in conflicts:
                names = ", ".join(f"{p}: {t.title}" for p, t in entries)
                lines.append(f"  {slot} → {names}")

        return "\n".join(lines)

    def detect_conflicts(self) -> List[Tuple[str, List[Tuple[str, Task]]]]:
        """Return a list of time-slot conflicts across all pets.

        Each entry is (time_slot, [(pet_name, task), ...]) for slots where
        more than one task is scheduled at the same time.
        """
        # Build a dict: scheduled_time -> list of (pet_name, task) pairs
        time_map: Dict[str, List[Tuple[str, Task]]] = {}
        for pet in self.owner.pets:
            for task in pet.tasks:
                if not task.scheduled_time or task.completed:
                    continue
                if task.scheduled_time not in time_map:
                    time_map[task.scheduled_time] = []
                time_map[task.scheduled_time].append((pet.name, task))

        # Keep only slots with more than one task
        return [
            (slot, entries)
            for slot, entries in sorted(time_map.items())
            if len(entries) > 1
        ]

    def explain_conflicts(self) -> str:
        """Return a human-readable conflict report."""
        conflicts = self.detect_conflicts()
        if not conflicts:
            return "No scheduling conflicts detected."

        lines = ["=== Scheduling Conflicts ==="]
        for slot, entries in conflicts:
            lines.append(f"\n  {slot} — {len(entries)} tasks overlap:")
            for pet_name, task in entries:
                lines.append(f"    [{pet_name}] {task.title} ({task.duration_minutes} min)")
        return "\n".join(lines)

    def mark_task_complete(self, title: str) -> None:
        """Mark a scheduled task complete by title, triggering recurrence if set."""
        for task in self._plan:
            if task.title == title:
                # Find which pet owns this task and use complete_task() so
                # recurrence logic runs in one place (Pet.complete_task).
                for pet in self.owner.pets:
                    if task in pet.tasks:
                        pet.complete_task(title)
                        return
        raise ValueError(f"Task '{title}' not found in the current plan.")
