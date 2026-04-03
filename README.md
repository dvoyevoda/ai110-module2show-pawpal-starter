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

## Features

PawPal+ includes the following scheduling and usability features:

- **Time-of-day sorting** — Every task has a `time_slot` (`morning`, `midday`, `evening`, or `anytime`). The scheduler returns accepted tasks in chronological order so the plan reads like a real day.
- **Multi-criteria filtering** — `Owner.filter_tasks()` filters by pet name, status (`pending` / `completed`), and time slot in one call.
- **Recurring task automation** — Completing a task with `daily`, `weekly`, or `monthly` recurrence automatically creates the next instance and advances the due date with `timedelta`.
- **Conflict detection and warnings** — `detect_conflicts()` returns warning messages (instead of crashing) for:
  1. Duplicate task names for the same pet.
  2. A single pet's time-slot load exceeding 90 minutes.
  3. Multiple tasks of the same category in one slot for the same pet.
  4. Different pets with tasks in the same slot (the owner can't be in two places at once).
- **Leftover-time suggestions** — `suggest_fillers()` recommends skipped tasks that can still fit the remaining minutes.
- **UI integration of scheduler logic** — `app.py` displays sorted/filtered task tables and presents conflict warnings with `st.warning`, success states with `st.success`, and schedule summaries in table format.

## Architecture (UML)

- Mermaid source: `uml_final.mmd`
- Exported diagram image: `uml_final.png`

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest tests/test_pawpal.py -v
```

The suite contains 20 tests across four areas:

- **Sorting Correctness** — Verifies tasks come back in morning → midday → evening → anytime order, stable ordering within the same slot, and safe handling of empty lists and unrecognized slot names.
- **Recurrence Logic** — Confirms that completing a daily task creates a new instance due tomorrow (`today + 1 day`), weekly adds 7 days, monthly adds 30 days, non-recurring tasks return None, and `Pet.mark_task_complete` auto-appends the next occurrence.
- **Conflict Detection** — Checks that duplicate task names, same-category collisions in one slot, and cross-pet same-slot overlaps all produce warnings, while `"anytime"` tasks and empty lists produce none.
- **Schedule Packing** — Ensures the greedy algorithm never exceeds the time budget, picks higher-priority tasks first, and correctly applies the +2 preference bonus.

**Confidence Level: 4 / 5** — All 20 tests pass and cover the core scheduling logic, sorting, recurrence, and conflict detection. The main gaps are integration-level tests for the Streamlit UI and edge cases around very large task lists, which would be the next areas to cover.

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
