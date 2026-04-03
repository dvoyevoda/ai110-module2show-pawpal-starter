from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Schedule, detect_conflicts, sort_by_time_slot


# ── Existing tests ────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task(name="Morning Walk", category="walk", duration=30, priority=5)
    assert task.is_complete() is False
    task.mark_complete()
    assert task.is_complete() is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feeding", category="feeding", duration=10, priority=4))
    pet.add_task(Task(name="Grooming", category="grooming", duration=15, priority=2))
    assert len(pet.tasks) == 2


# ── Sorting Correctness ──────────────────────────────────────

def test_sort_returns_chronological_order():
    """Tasks added in reverse order come back morning → midday → evening → anytime."""
    tasks = [
        Task(name="T1", category="walk",       duration=10, priority=3, time_slot="anytime"),
        Task(name="T2", category="feeding",    duration=10, priority=3, time_slot="evening"),
        Task(name="T3", category="enrichment", duration=10, priority=3, time_slot="morning"),
        Task(name="T4", category="meds",       duration=10, priority=3, time_slot="midday"),
    ]
    result = sort_by_time_slot(tasks)
    slots = [t.time_slot for t in result]
    assert slots == ["morning", "midday", "evening", "anytime"]


def test_sort_preserves_order_within_same_slot():
    """Multiple tasks in the same slot keep their relative (stable) order."""
    tasks = [
        Task(name="A", category="walk",    duration=10, priority=3, time_slot="morning"),
        Task(name="B", category="feeding", duration=10, priority=3, time_slot="morning"),
        Task(name="C", category="meds",    duration=10, priority=3, time_slot="morning"),
    ]
    result = sort_by_time_slot(tasks)
    names = [t.name for t in result]
    assert names == ["A", "B", "C"]


def test_sort_handles_empty_list():
    assert sort_by_time_slot([]) == []


def test_sort_unknown_slot_goes_last():
    """A task with an unrecognized time_slot sorts after 'anytime'."""
    tasks = [
        Task(name="Bad", category="walk", duration=10, priority=3, time_slot="afternoon"),
        Task(name="Good", category="walk", duration=10, priority=3, time_slot="morning"),
    ]
    result = sort_by_time_slot(tasks)
    assert result[0].name == "Good"
    assert result[1].name == "Bad"


# ── Recurrence Logic ─────────────────────────────────────────

def test_daily_recurrence_creates_next_day_task():
    """Completing a daily task returns a new task due tomorrow."""
    today = str(date.today())
    tomorrow = str(date.today() + timedelta(days=1))

    task = Task(
        name="Grooming",
        category="grooming",
        duration=15,
        priority=2,
        recurrence="daily",
        due_date=today,
    )
    next_task = task.mark_complete()

    assert task.is_complete() is True
    assert next_task is not None
    assert next_task.is_complete() is False
    assert next_task.due_date == tomorrow
    assert next_task.recurrence == "daily"


def test_weekly_recurrence_creates_task_seven_days_out():
    today = str(date.today())
    next_week = str(date.today() + timedelta(days=7))

    task = Task(name="Bath", category="grooming", duration=30, priority=2,
                recurrence="weekly", due_date=today)
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == next_week


def test_monthly_recurrence_creates_task_thirty_days_out():
    today = str(date.today())
    next_month = str(date.today() + timedelta(days=30))

    task = Task(name="Flea Meds", category="meds", duration=10, priority=5,
                recurrence="monthly", due_date=today)
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == next_month


def test_non_recurring_task_returns_none():
    """A task with recurrence='none' should not spawn a new instance."""
    task = Task(name="Walk", category="walk", duration=30, priority=5,
                recurrence="none")
    next_task = task.mark_complete()

    assert task.is_complete() is True
    assert next_task is None


def test_pet_mark_task_complete_adds_next_to_list():
    """Pet.mark_task_complete should auto-append the next occurrence."""
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", category="walk", duration=30, priority=5,
                      recurrence="daily", due_date=str(date.today())))

    assert len(pet.tasks) == 1
    pet.mark_task_complete("Walk")
    assert len(pet.tasks) == 2
    assert pet.tasks[0].is_complete() is True
    assert pet.tasks[1].is_complete() is False


def test_recurrence_with_no_due_date_defaults_to_today():
    """If due_date is empty, mark_complete should use today as the base."""
    task = Task(name="Walk", category="walk", duration=30, priority=5,
                recurrence="daily", due_date="")
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == str(date.today() + timedelta(days=1))


# ── Conflict Detection ───────────────────────────────────────

def test_duplicate_task_name_flagged():
    """Two tasks with the same name for the same pet produce a warning."""
    tasks = [
        Task(name="Walk", category="walk", duration=30, priority=5,
             time_slot="morning", pet_name="Buddy"),
        Task(name="Walk", category="walk", duration=20, priority=3,
             time_slot="morning", pet_name="Buddy"),
    ]
    warnings = detect_conflicts(tasks)
    assert any("Duplicate" in w and "Buddy" in w for w in warnings)


def test_same_category_same_slot_flagged():
    """Two walk tasks in the same slot for one pet should trigger a warning."""
    tasks = [
        Task(name="Morning Walk", category="walk", duration=30, priority=5,
             time_slot="morning", pet_name="Buddy"),
        Task(name="Short Walk",   category="walk", duration=15, priority=3,
             time_slot="morning", pet_name="Buddy"),
    ]
    warnings = detect_conflicts(tasks)
    assert any("walk" in w and "morning" in w for w in warnings)


def test_cross_pet_same_slot_flagged():
    """Different pets with tasks in the same slot produce a warning."""
    tasks = [
        Task(name="Walk",      category="walk",    duration=30, priority=5,
             time_slot="morning", pet_name="Buddy"),
        Task(name="Breakfast", category="feeding",  duration=10, priority=4,
             time_slot="morning", pet_name="Whiskers"),
    ]
    warnings = detect_conflicts(tasks)
    assert any("Multiple pets" in w and "morning" in w for w in warnings)


def test_anytime_tasks_produce_no_slot_conflicts():
    """Tasks set to 'anytime' should not trigger any time-slot warnings."""
    tasks = [
        Task(name="Walk",  category="walk",    duration=30, priority=5,
             time_slot="anytime", pet_name="Buddy"),
        Task(name="Feed",  category="feeding", duration=10, priority=4,
             time_slot="anytime", pet_name="Whiskers"),
    ]
    warnings = detect_conflicts(tasks)
    slot_warnings = [w for w in warnings if "slot" in w or "Multiple pets" in w]
    assert slot_warnings == []


def test_empty_task_list_no_conflicts():
    assert detect_conflicts([]) == []


# ── Schedule Packing ─────────────────────────────────────────

def test_schedule_never_exceeds_available_time():
    tasks = [
        Task(name="A", category="walk",    duration=40, priority=5, time_slot="morning"),
        Task(name="B", category="feeding", duration=40, priority=4, time_slot="midday"),
        Task(name="C", category="meds",    duration=40, priority=3, time_slot="evening"),
    ]
    schedule = Schedule(date=str(date.today()))
    schedule.generate_schedule(tasks, available_time=60)

    assert schedule.total_duration <= 60


def test_schedule_prefers_higher_priority():
    low  = Task(name="Low",  category="enrichment", duration=20, priority=1, time_slot="morning")
    high = Task(name="High", category="meds",       duration=20, priority=5, time_slot="morning")
    schedule = Schedule(date=str(date.today()))
    schedule.generate_schedule([low, high], available_time=20)

    assert len(schedule.tasks) == 1
    assert schedule.tasks[0].name == "High"


def test_preference_boost_can_change_outcome():
    """A preferred category's +2 bonus should beat a higher base priority."""
    regular = Task(name="Regular", category="enrichment", duration=20, priority=5, time_slot="morning")
    boosted = Task(name="Boosted", category="walk",       duration=20, priority=4, time_slot="morning")

    schedule = Schedule(date=str(date.today()))
    schedule.generate_schedule([regular, boosted], available_time=20,
                               preferences=["walk"])

    assert schedule.tasks[0].name == "Boosted"
