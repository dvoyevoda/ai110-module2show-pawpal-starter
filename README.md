# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Beyond the basic greedy scheduler, PawPal+ includes several algorithmic improvements that make the daily plan more realistic for a pet owner:

- **Time-of-day sorting** — Every task has a `time_slot` (morning, midday, evening, or anytime). After the scheduler selects which tasks fit the time budget, it sorts them chronologically using `sort_by_time_slot()` so the output reads like a real daily agenda.
- **Multi-criteria filtering** — `Owner.filter_tasks()` lets you narrow tasks by pet name, completion status, and/or time slot in a single call. Filters are independent and composable.
- **Recurring task automation** — Tasks with a `recurrence` of daily, weekly, or monthly automatically generate a new instance when marked complete. The next due date is calculated with Python's `timedelta` (e.g. daily = today + 1 day, monthly = today + 30 days).
- **Conflict detection** — `detect_conflicts()` scans the task list for four kinds of problems and returns human-readable warnings instead of crashing:
  1. Duplicate task names for the same pet.
  2. A single pet's time-slot load exceeding 90 minutes.
  3. Multiple tasks of the same category in one slot for the same pet.
  4. Different pets with tasks in the same slot (the owner can't be in two places at once).
- **Leftover-time suggestions** — After scheduling, `suggest_fillers()` identifies skipped tasks that would still fit in the remaining free minutes.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
