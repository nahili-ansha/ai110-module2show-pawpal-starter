import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Task Completion ---

def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=30, priority="high", task_type="walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


# --- Task Addition ---

def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Breakfast", duration_minutes=10, priority="high", task_type="feeding"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Evening walk", duration_minutes=20, priority="medium", task_type="walk"))
    assert len(pet.tasks) == 2


# --- Sorting Correctness ---

def test_tasks_sorted_by_time_chronological_order():
    pet = Pet(name="Mochi", species="dog", age=3)
    # Added out of order intentionally
    pet.add_task(Task(title="Evening walk", duration_minutes=30, priority="high",   task_type="walk",    scheduled_time="18:00"))
    pet.add_task(Task(title="Flea meds",    duration_minutes=5,  priority="medium", task_type="meds",    scheduled_time="09:00"))
    pet.add_task(Task(title="Breakfast",    duration_minutes=10, priority="high",   task_type="feeding", scheduled_time="07:30"))

    sorted_tasks = pet.get_tasks_sorted_by_time()
    times = [t.scheduled_time for t in sorted_tasks]
    assert times == ["07:30", "09:00", "18:00"]


def test_tasks_with_no_time_sort_last():
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Afternoon nap", duration_minutes=20, priority="low", task_type="other"))           # no time
    pet.add_task(Task(title="Breakfast",     duration_minutes=10, priority="high", task_type="feeding", scheduled_time="07:30"))

    sorted_tasks = pet.get_tasks_sorted_by_time()
    assert sorted_tasks[0].title == "Breakfast"
    assert sorted_tasks[-1].title == "Afternoon nap"


# --- Recurrence Logic ---

def test_daily_recurring_task_creates_next_occurrence():
    pet = Pet(name="Luna", species="cat", age=5)
    today = date.today()
    pet.add_task(Task(title="Breakfast", duration_minutes=10, priority="high",
                      task_type="feeding", recurrence="daily", due_date=today))

    pet.complete_task("Breakfast")

    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False
    assert pet.tasks[1].due_date == today + timedelta(days=1)


def test_weekly_recurring_task_due_seven_days_later():
    pet = Pet(name="Luna", species="cat", age=5)
    today = date.today()
    pet.add_task(Task(title="Grooming", duration_minutes=15, priority="low",
                      task_type="grooming", recurrence="weekly", due_date=today))

    pet.complete_task("Grooming")

    assert pet.tasks[1].due_date == today + timedelta(days=7)


def test_non_recurring_task_does_not_create_next_occurrence():
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="One-time bath", duration_minutes=20, priority="medium",
                      task_type="grooming", recurrence=""))

    pet.complete_task("One-time bath")

    assert len(pet.tasks) == 1          # no new task appended
    assert pet.tasks[0].completed is True


# --- Conflict Detection ---

def test_scheduler_detects_same_time_conflict():
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)

    mochi.add_task(Task(title="Morning walk", duration_minutes=20, priority="high",
                        task_type="walk", scheduled_time="08:00"))
    luna.add_task( Task(title="Brush coat",   duration_minutes=15, priority="low",
                        task_type="grooming", scheduled_time="08:00"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    conflict_time, entries = conflicts[0]
    assert conflict_time == "08:00"
    assert len(entries) == 2


def test_scheduler_no_false_positive_when_times_differ():
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)

    mochi.add_task(Task(title="Morning walk", duration_minutes=20, priority="high",
                        task_type="walk", scheduled_time="08:00"))
    luna.add_task( Task(title="Brush coat",   duration_minutes=15, priority="low",
                        task_type="grooming", scheduled_time="09:00"))  # different time

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 0
