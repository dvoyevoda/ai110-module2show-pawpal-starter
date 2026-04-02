from pawpal_system import Task, Pet


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
