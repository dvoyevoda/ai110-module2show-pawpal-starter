from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    available_time: int  # minutes per day
    preferences: list[str] = field(default_factory=list)


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0


@dataclass
class Task:
    name: str
    category: str  # e.g. "walk", "feeding", "meds", "enrichment", "grooming"
    duration: int  # minutes
    priority: int  # 1 (low) – 5 (high)
    description: str = ""


@dataclass
class Schedule:
    date: str
    tasks: list[Task] = field(default_factory=list)
    total_duration: int = 0

    def generate_schedule(
        self, tasks: list[Task], available_time: int
    ) -> list[Task]:
        """Select and order tasks that fit within available_time, respecting priorities."""
        pass

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of why this schedule was chosen."""
        pass

    def get_total_duration(self) -> int:
        """Return the sum of durations for all scheduled tasks."""
        pass
