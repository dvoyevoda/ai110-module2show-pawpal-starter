from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule, detect_conflicts, sort_by_time_slot

def print_task_list(tasks: list[Task], indent: str = "  ") -> None:
    """Helper to print a list of tasks with consistent formatting."""
    for t in tasks:
        status = "done" if t.completed else "pending"
        due = f", due {t.due_date}" if t.due_date else ""
        recur = f", recurs {t.recurrence}" if t.recurrence != "none" else ""
        print(
            f"{indent}• {t.name} ({t.pet_name}) [{t.category}] "
            f"— {t.duration} min, {t.time_slot}, priority {t.priority}, "
            f"{status}{due}{recur}"
        )

# ── Setup owner ──────────────────────────────────────────────
owner = Owner(name="Alex", available_time=90, preferences=["walk", "meds"])
today = str(date.today())

buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby", age=5)

# ── Add tasks DELIBERATELY OUT OF TIME ORDER ─────────────────
# Two tasks for DIFFERENT pets in the SAME morning slot → cross-pet conflict
# Two walk tasks for Buddy in the SAME morning slot → same-category conflict
buddy.add_task(Task(name="Fetch Play",    category="enrichment", duration=20, priority=3, time_slot="midday"))
buddy.add_task(Task(name="Evening Walk",  category="walk",       duration=25, priority=4, time_slot="evening"))
buddy.add_task(Task(name="Flea Medicine", category="meds",       duration=10, priority=5, time_slot="morning", recurrence="monthly", due_date=today))
buddy.add_task(Task(name="Morning Walk",  category="walk",       duration=30, priority=5, time_slot="morning"))
buddy.add_task(Task(name="Short Walk",    category="walk",       duration=15, priority=3, time_slot="morning"))

whiskers.add_task(Task(name="Grooming Brush", category="grooming",   duration=15, priority=2, time_slot="evening", recurrence="daily", due_date=today))
whiskers.add_task(Task(name="Breakfast",      category="feeding",    duration=10, priority=4, time_slot="morning"))
whiskers.add_task(Task(name="Catnip Play",    category="enrichment", duration=10, priority=2, time_slot="midday"))

owner.add_pet(buddy)
owner.add_pet(whiskers)


# ═══════════════════════════════════════════════════════════════
# 1. SORTING BY TIME — before vs. after
# ═══════════════════════════════════════════════════════════════
print("=" * 58)
print("  1. SORTING DEMO — tasks added out of time order")
print("=" * 58)

all_tasks = []
for pet in owner.pets:
    all_tasks.extend(pet.tasks)

print("\nBefore sorting (insertion order):")
print_task_list(all_tasks)

sorted_tasks = sort_by_time_slot(all_tasks)
print("\nAfter sort_by_time_slot() — morning → midday → evening → anytime:")
print_task_list(sorted_tasks)


# ═══════════════════════════════════════════════════════════════
# 2. FILTERING BY STATUS AND PET NAME
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 58)
print("  2. FILTERING DEMO")
print("=" * 58)

print("\nBuddy's tasks only:")
print_task_list(owner.filter_tasks(pet_name="Buddy"))

print("\nWhiskers' tasks only:")
print_task_list(owner.filter_tasks(pet_name="Whiskers"))

print("\nAll pending tasks:")
print_task_list(owner.filter_tasks(status="pending"))


# ═══════════════════════════════════════════════════════════════
# 3. RECURRING TASK AUTO-CREATION (Step 3)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 58)
print("  3. RECURRING TASKS — auto-create next occurrence")
print("=" * 58)

print(f"\nBuddy's tasks BEFORE completing 'Flea Medicine' (due {today}):")
print_task_list([t for t in buddy.tasks if "Flea" in t.name or "flea" in t.name])

next_flea = buddy.mark_task_complete("Flea Medicine")
print(f"\nCalled buddy.mark_task_complete('Flea Medicine')")
print(f"  → Original task marked done.")
if next_flea:
    print(f"  → New instance auto-created with due_date = {next_flea.due_date}")

print(f"\nBuddy's Flea Medicine tasks AFTER completion:")
print_task_list([t for t in buddy.tasks if "Flea" in t.name])

print(f"\nWhiskers' tasks BEFORE completing 'Grooming Brush' (due {today}):")
print_task_list([t for t in whiskers.tasks if "Grooming" in t.name])

next_groom = whiskers.mark_task_complete("Grooming Brush")
print(f"\nCalled whiskers.mark_task_complete('Grooming Brush')")
print(f"  → Original task marked done.")
if next_groom:
    print(f"  → New instance auto-created with due_date = {next_groom.due_date} (daily = today + 1 day)")

print(f"\nWhiskers' Grooming Brush tasks AFTER completion:")
print_task_list([t for t in whiskers.tasks if "Grooming" in t.name])


# ═══════════════════════════════════════════════════════════════
# 4. CONFLICT DETECTION (Step 4)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 58)
print("  4. CONFLICT DETECTION — same-time task warnings")
print("=" * 58)

pending_tasks = owner.get_all_tasks()
conflicts = detect_conflicts(pending_tasks)

if conflicts:
    print(f"\n⚠  {len(conflicts)} conflict(s) detected:\n")
    for c in conflicts:
        print(f"   • {c}")
else:
    print("\n  No conflicts detected.")


# ═══════════════════════════════════════════════════════════════
# 5. FULL SCHEDULE GENERATION
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 58)
print("  5. GENERATED SCHEDULE (with embedded conflict warnings)")
print("=" * 58)

schedule = Schedule(date=today)
schedule.generate_schedule(
    tasks=owner.get_all_tasks(),
    available_time=owner.available_time,
    preferences=owner.preferences,
)
print()
print(schedule.explain_reasoning())

remaining = schedule.get_remaining_time(owner.available_time)
if remaining > 0:
    print(f"\n  🕐 {remaining} min of free time remaining")
    fillers = schedule.suggest_fillers(owner.available_time)
    if fillers:
        print("  Could still fit:")
        for t in fillers:
            print(f"    • {t.name} ({t.pet_name}) — {t.duration} min")

print("=" * 58)
