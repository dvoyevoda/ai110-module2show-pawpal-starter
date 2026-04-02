from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Task:
    name: str
    category: str       # e.g. "walk", "feeding", "meds", "enrichment", "grooming"
    duration: int       # minutes
    priority: int       # 1 (low) – 5 (high)
    description: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_complete(self) -> bool:
        """Return whether this task has been completed."""
        return self.completed


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> bool:
        """Remove a task by name. Returns True if found and removed, False otherwise."""
        for task in self.tasks:
            if task.name == task_name:
                self.tasks.remove(task)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    name: str
    available_time: int             # minutes per day
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect and return all pending tasks across every pet."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_pending_tasks())
        return all_tasks


@dataclass
class Schedule:
    date: str
    tasks: list[Task] = field(default_factory=list)
    _skipped: list[Task] = field(default_factory=list, repr=False)
    total_duration: int = 0

    def generate_schedule(
        self,
        tasks: list[Task],
        available_time: int,
        preferences: list[str] | None = None,
    ) -> list[Task]:
        """Greedily select and order tasks by priority (boosted by owner preferences) that fit within available_time."""
        prefs = [p.lower() for p in (preferences or [])]

        def effective_priority(task: Task) -> int:
            bonus = 1 if task.category.lower() in prefs else 0
            return task.priority + bonus

        candidates = sorted(
            tasks,
            key=lambda t: (effective_priority(t), -t.duration),
            reverse=True,
        )

        scheduled: list[Task] = []
        skipped: list[Task] = []
        time_used = 0

        for task in candidates:
            if time_used + task.duration <= available_time:
                scheduled.append(task)
                time_used += task.duration
            else:
                skipped.append(task)

        self.tasks = scheduled
        self._skipped = skipped
        self.total_duration = time_used
        return scheduled

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of the scheduling decisions."""
        if not self.tasks:
            return "No tasks were scheduled."

        lines: list[str] = [
            f"Schedule for {self.date}",
            f"Total time used: {self.total_duration} min",
            "",
            "Scheduled tasks (highest effective priority first):",
        ]
        for task in self.tasks:
            lines.append(
                f"  • {task.name} [{task.category}] — {task.duration} min"
                f" (priority {task.priority})"
            )

        if self._skipped:
            lines.append("")
            lines.append("Skipped (not enough time remaining):")
            for task in self._skipped:
                lines.append(
                    f"  • {task.name} [{task.category}] — {task.duration} min"
                    f" (priority {task.priority})"
                )

        return "\n".join(lines)

    def get_total_duration(self) -> int:
        """Return the sum of durations for all scheduled tasks."""
        return sum(t.duration for t in self.tasks)
