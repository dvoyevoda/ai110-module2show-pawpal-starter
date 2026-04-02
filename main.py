from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule

# --- Setup owner ---
owner = Owner(name="Alex", available_time=90, preferences=["walk", "meds"])

# --- Setup pets ---
buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby", age=5)

# --- Add tasks to Buddy ---
buddy.add_task(Task(name="Morning Walk",   category="walk",       duration=30, priority=5))
buddy.add_task(Task(name="Flea Medicine",  category="meds",       duration=10, priority=5))
buddy.add_task(Task(name="Fetch Play",     category="enrichment", duration=20, priority=3))

# --- Add tasks to Whiskers ---
whiskers.add_task(Task(name="Breakfast",      category="feeding",   duration=10, priority=4))
whiskers.add_task(Task(name="Grooming Brush", category="grooming",  duration=15, priority=2))

# --- Link pets to owner ---
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Generate schedule ---
schedule = Schedule(date=str(date.today()))
schedule.generate_schedule(
    tasks=owner.get_all_tasks(),
    available_time=owner.available_time,
    preferences=owner.preferences,
)

# --- Print Today's Schedule ---
print("=" * 45)
print("         TODAY'S SCHEDULE — PawPal+")
print("=" * 45)
print(schedule.explain_reasoning())
print("=" * 45)
