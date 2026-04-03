from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta

TIME_SLOT_ORDER = {"morning": 0, "midday": 1, "evening": 2, "anytime": 3}

RECURRENCE_DELTAS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(days=7),
    "monthly": timedelta(days=30),
}


@dataclass
class Task:
    name: str
    category: str       # e.g. "walk", "feeding", "meds", "enrichment", "grooming"
    duration: int       # minutes
    priority: int       # 1 (low) – 5 (high)
    description: str = ""
    completed: bool = False
    time_slot: str = "anytime"   # "morning", "midday", "evening", "anytime"
    recurrence: str = "none"     # "none", "daily", "weekly", "monthly"
    pet_name: str = ""
    due_date: str = ""           # ISO date string, e.g. "2026-04-02"

    def mark_complete(self) -> Task | None:
        """Mark this task as completed.  If the task is recurring, return a
        new Task instance whose due_date is advanced by the appropriate
        timedelta (1 day / 7 days / 30 days).  Returns None for non-recurring
        tasks."""
        self.completed = True

        delta = RECURRENCE_DELTAS.get(self.recurrence)
        if delta is None:
            return None

        base = date.fromisoformat(self.due_date) if self.due_date else date.today()
        next_due = base + delta

        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            description=self.description,
            completed=False,
            time_slot=self.time_slot,
            recurrence=self.recurrence,
            pet_name=self.pet_name,
            due_date=str(next_due),
        )

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
        """Add a care task for this pet, stamping it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def mark_task_complete(self, task_name: str) -> Task | None:
        """Mark a task complete by name.  If the task recurs, the next
        occurrence is automatically added to this pet's task list and
        returned.  Returns None when the task is non-recurring or not found."""
        for task in self.tasks:
            if task.name == task_name and not task.completed:
                next_task = task.mark_complete()
                if next_task is not None:
                    self.tasks.append(next_task)
                return next_task
        return None

    def remove_task(self, task_name: str) -> bool:
        """Remove a task by name (single-pass). Returns True if found."""
        for i, task in enumerate(self.tasks):
            if task.name == task_name:
                self.tasks.pop(i)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]

    def get_tasks_by_status(self, completed: bool) -> list[Task]:
        """Filter this pet's tasks by completion status.

        Args:
            completed: True to return finished tasks, False for pending.

        Returns:
            A new list containing only tasks whose completed flag matches.
        """
        return [t for t in self.tasks if t.completed == completed]

    def get_tasks_by_time_slot(self, slot: str) -> list[Task]:
        """Filter this pet's tasks by their assigned time of day.

        Args:
            slot: One of "morning", "midday", "evening", or "anytime".

        Returns:
            A new list containing only tasks in the given time slot.
        """
        return [t for t in self.tasks if t.time_slot == slot]


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

    def get_tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to a specific pet."""
        for pet in self.pets:
            if pet.name == pet_name:
                return list(pet.tasks)
        return []

    def sort_tasks_by_time(self, pet_name: str | None = None) -> list[Task]:
        """Collect tasks and return them sorted chronologically by time slot.

        Uses the TIME_SLOT_ORDER mapping so that morning tasks come first,
        followed by midday, evening, and finally flexible ("anytime") tasks.

        Args:
            pet_name: If provided, only that pet's tasks are included.
                      If None, tasks from every pet are collected.

        Returns:
            A new list sorted in morning → midday → evening → anytime order.
        """
        if pet_name:
            tasks = self.get_tasks_for_pet(pet_name)
        else:
            tasks = []
            for pet in self.pets:
                tasks.extend(pet.tasks)
        return sort_by_time_slot(tasks)

    def filter_tasks(
        self,
        pet_name: str | None = None,
        status: str | None = None,
        time_slot: str | None = None,
    ) -> list[Task]:
        """Multi-criteria filter across all pets' tasks.

        Applies up to three independent filters in sequence: pet name,
        completion status, and time slot.  Each filter that is None (or
        "all" for time_slot) is skipped, so callers can combine any subset.

        Args:
            pet_name:  Restrict to a single pet, or None for all pets.
            status:    "pending" (incomplete only), "completed" (done only),
                       or None (both).
            time_slot: "morning", "midday", "evening", "anytime", or
                       "all"/None to skip this filter.

        Returns:
            A new list of Task objects satisfying every active filter.
        """
        tasks: list[Task] = []
        sources = self.pets
        if pet_name:
            sources = [p for p in self.pets if p.name == pet_name]

        for pet in sources:
            tasks.extend(pet.tasks)

        if status == "pending":
            tasks = [t for t in tasks if not t.completed]
        elif status == "completed":
            tasks = [t for t in tasks if t.completed]

        if time_slot and time_slot != "all":
            tasks = [t for t in tasks if t.time_slot == time_slot]

        return tasks

    def expand_recurring_tasks(self) -> None:
        """For each recurring task that is already completed, reset it so it
        appears again in the next schedule generation.  In a production app
        this would check dates; here it simply marks recurring tasks incomplete
        so they reappear each day."""
        for pet in self.pets:
            for task in pet.tasks:
                if task.recurrence != "none" and task.completed:
                    task.completed = False


def detect_conflicts(tasks: list[Task]) -> list[str]:
    """Detect scheduling conflicts among a list of tasks.

    Conflicts detected:
    1. Duplicate task names for the same pet (likely accidental).
    2. Same pet has two tasks in a time slot whose total exceeds 90 min.
    3. Same pet has multiple tasks of the same category in one slot.
    4. Different pets have tasks in the same time slot — the owner
       would need to attend to both pets simultaneously.
    """
    warnings: list[str] = []

    # --- 1. Duplicate task names per pet ---
    seen_names: dict[str, list[str]] = {}
    for task in tasks:
        key = f"{task.pet_name}|{task.name}"
        seen_names.setdefault(key, []).append(task.time_slot)
    for key, slots in seen_names.items():
        if len(slots) > 1:
            pet, name = key.split("|", 1)
            warnings.append(
                f"Duplicate task \"{name}\" for {pet} — "
                f"appears {len(slots)} times."
            )

    # --- Per-pet slot analysis (checks 2 & 3) ---
    pet_slot_loads: dict[str, list[Task]] = {}
    for task in tasks:
        if task.time_slot == "anytime":
            continue
        bucket = f"{task.pet_name}|{task.time_slot}"
        pet_slot_loads.setdefault(bucket, []).append(task)

    for bucket, bucket_tasks in pet_slot_loads.items():
        pet, slot = bucket.split("|", 1)
        total = sum(t.duration for t in bucket_tasks)
        if total > 90:
            names = ", ".join(t.name for t in bucket_tasks)
            warnings.append(
                f"{pet}'s {slot} tasks ({names}) total {total} min — "
                f"may be unrealistic for a single time slot."
            )

        categories = [t.category for t in bucket_tasks]
        for cat in set(categories):
            if categories.count(cat) > 1:
                warnings.append(
                    f"{pet} has multiple \"{cat}\" tasks in the {slot} slot."
                )

    # --- 4. Cross-pet same-slot conflict ---
    slot_pets: dict[str, set[str]] = {}
    for task in tasks:
        if task.time_slot == "anytime":
            continue
        slot_pets.setdefault(task.time_slot, set()).add(task.pet_name)
    for slot, pets in slot_pets.items():
        if len(pets) > 1:
            pet_list = ", ".join(sorted(pets))
            warnings.append(
                f"Multiple pets ({pet_list}) have tasks in the {slot} slot "
                f"— owner may need to handle them at the same time."
            )

    return warnings


def sort_by_time_slot(tasks: list[Task]) -> list[Task]:
    """Sort tasks into chronological time-of-day order.

    Uses the module-level TIME_SLOT_ORDER dict to map each task's
    time_slot string to a numeric rank (morning=0, midday=1, evening=2,
    anytime=3).  Tasks with an unrecognized slot sort last.

    Algorithm: Python's built-in Timsort (stable), O(n log n).

    Args:
        tasks: The list of Task objects to sort.

    Returns:
        A new list ordered morning → midday → evening → anytime.
    """
    return sorted(tasks, key=lambda t: TIME_SLOT_ORDER.get(t.time_slot, 99))


@dataclass
class Schedule:
    date: str
    tasks: list[Task] = field(default_factory=list)
    _skipped: list[Task] = field(default_factory=list, repr=False)
    _conflicts: list[str] = field(default_factory=list, repr=False)
    total_duration: int = 0

    def generate_schedule(
        self,
        tasks: list[Task],
        available_time: int,
        preferences: list[str] | None = None,
    ) -> list[Task]:
        """Build an optimized daily schedule using a greedy algorithm.

        Steps:
        1. Compute each task's *effective priority* — base priority plus a
           +2 bonus if its category is in the owner's preference list.
        2. Sort candidates by (effective_priority DESC, duration DESC) so
           high-value, longer tasks are considered first.
        3. Greedily pack tasks into the available time budget; tasks that
           don't fit are placed on the skipped list.
        4. Sort the accepted tasks by time slot (morning → evening) so the
           output reads like a chronological agenda.
        5. Run detect_conflicts() on the final list and store any warnings.

        Args:
            tasks:          Candidate tasks (typically from Owner.get_all_tasks).
            available_time: The owner's daily time budget in minutes.
            preferences:    Category strings that receive a scheduling boost.

        Returns:
            The list of scheduled Task objects (also stored in self.tasks).
        """
        prefs = [p.lower() for p in (preferences or [])]

        def effective_priority(task: Task) -> int:
            bonus = 2 if task.category.lower() in prefs else 0
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

        scheduled = sort_by_time_slot(scheduled)

        self.tasks = scheduled
        self._skipped = skipped
        self._conflicts = detect_conflicts(scheduled)
        self.total_duration = time_used
        return scheduled

    def get_conflicts(self) -> list[str]:
        """Return any conflict warnings from the last schedule generation."""
        return list(self._conflicts)

    def get_skipped_tasks(self) -> list[Task]:
        """Return tasks that were skipped because they did not fit in time."""
        return list(self._skipped)

    def get_remaining_time(self, available_time: int) -> int:
        """Minutes of unused available time."""
        return available_time - self.total_duration

    def suggest_fillers(self, available_time: int) -> list[Task]:
        """Suggest skipped tasks that could still fit in leftover time.

        After the greedy packer runs, there may be a gap between
        total_duration and available_time.  This scans the skipped list
        for any individual task whose duration is <= the remaining gap.

        Args:
            available_time: The owner's daily time budget in minutes.

        Returns:
            A list of Task objects from the skipped list that would fit.
        """
        remaining = self.get_remaining_time(available_time)
        return [t for t in self._skipped if t.duration <= remaining]

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of the scheduling decisions."""
        if not self.tasks:
            return "No tasks were scheduled."

        lines: list[str] = [
            f"Schedule for {self.date}",
            f"Total time used: {self.total_duration} min",
            "",
            "Scheduled tasks (sorted by time of day):",
        ]
        for task in self.tasks:
            slot_label = task.time_slot if task.time_slot != "anytime" else "flexible"
            lines.append(
                f"  • [{slot_label}] {task.name} ({task.pet_name}) "
                f"[{task.category}] — {task.duration} min "
                f"(priority {task.priority})"
            )

        if self._conflicts:
            lines.append("")
            lines.append("⚠ Conflicts detected:")
            for warning in self._conflicts:
                lines.append(f"  • {warning}")

        if self._skipped:
            lines.append("")
            lines.append("Skipped (not enough time remaining):")
            for task in self._skipped:
                lines.append(
                    f"  • {task.name} ({task.pet_name}) [{task.category}] "
                    f"— {task.duration} min (priority {task.priority})"
                )

        return "\n".join(lines)

    def get_total_duration(self) -> int:
        """Return the sum of durations for all scheduled tasks."""
        return sum(t.duration for t in self.tasks)
