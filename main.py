from pawpal_system import Owner, Pet, Task, Scheduler


# --- Create Owner ---
owner = Owner(name="Jordan", available_minutes=90)

# --- Create Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Add Tasks OUT OF ORDER (times are intentionally scrambled) ---
mochi.add_task(Task(title="Evening walk",   duration_minutes=30, priority="high",   task_type="walk",    scheduled_time="18:00"))
mochi.add_task(Task(title="Flea medicine",  duration_minutes=5,  priority="medium", task_type="meds",    scheduled_time="09:00"))
mochi.add_task(Task(title="Breakfast",      duration_minutes=10, priority="high",   task_type="feeding", scheduled_time="07:30"))
mochi.add_task(Task(title="Afternoon nap",  duration_minutes=20, priority="low",    task_type="other"))   # no time set

luna.add_task(Task(title="Dinner",          duration_minutes=10, priority="high",   task_type="feeding", scheduled_time="17:00"))
luna.add_task(Task(title="Puzzle feeder",   duration_minutes=20, priority="medium", task_type="enrichment", scheduled_time="10:30"))
luna.add_task(Task(title="Brush coat",      duration_minutes=15, priority="low",    task_type="grooming", scheduled_time="08:00"))
luna.add_task(Task(title="Midnight snack",  duration_minutes=5,  priority="low",    task_type="feeding", scheduled_time="23:00"))

# --- Intentional conflicts: two tasks at the same time slot ---
mochi.add_task(Task(title="Morning walk",   duration_minutes=20, priority="high",   task_type="walk",    scheduled_time="08:00"))  # conflicts with Luna's Brush coat
luna.add_task( Task(title="Morning meds",   duration_minutes=5,  priority="medium", task_type="meds",    scheduled_time="09:00"))  # conflicts with Mochi's Flea medicine

# --- Register Pets with Owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Mark some tasks complete to test filtering ---
mochi.tasks[2].mark_complete()   # Breakfast → done
luna.tasks[0].mark_complete()    # Dinner → done

# ── Test 1: Sort by time ───────────────────────────────────────────────────────
print("=" * 50)
print("MOCHI — tasks sorted by scheduled time:")
for task in mochi.get_tasks_sorted_by_time():
    time = task.scheduled_time or "no time"
    print(f"  {time:>8}  {task.title}")

print()
print("LUNA — tasks sorted by scheduled time:")
for task in luna.get_tasks_sorted_by_time():
    time = task.scheduled_time or "no time"
    print(f"  {time:>8}  {task.title}")

# ── Test 2: Filter by status ───────────────────────────────────────────────────
print()
print("=" * 50)
print("MOCHI — pending tasks:")
for task in mochi.get_pending_tasks():
    print(f"  [ ] {task.title}")

print()
print("MOCHI — completed tasks:")
for task in mochi.get_completed_tasks():
    print(f"  [x] {task.title}")

print()
print("LUNA — filter_tasks_by_status(completed=True):")
for task in luna.filter_tasks_by_status(completed=True):
    print(f"  [x] {task.title}")

print()
print("LUNA — filter_tasks_by_status(completed=False):")
for task in luna.filter_tasks_by_status(completed=False):
    print(f"  [ ] {task.title}")

# ── Test 3: Filter by pet name ─────────────────────────────────────────────────
print()
print("=" * 50)
print("Owner.get_tasks_for_pet('Mochi'):")
for task in owner.get_tasks_for_pet("Mochi"):
    print(f"  {task.title}")

print()
print("Owner.get_tasks_for_pet('luna')  ← lowercase, should still work:")
for task in owner.get_tasks_for_pet("luna"):
    print(f"  {task.title}")

print()
print("Owner.get_tasks_for_pet('Rex')  ← not found:")
result = owner.get_tasks_for_pet("Rex")
print(f"  Result: {result}")

# ── Test 4: Conflict detection ────────────────────────────────────────────────
print()
print("=" * 50)
scheduler = Scheduler(owner)
scheduler.generate_plan()

print("CONFLICT REPORT:")
print(scheduler.explain_conflicts())

# ── Test 5: Full schedule (conflicts also appear at the bottom) ────────────────
print()
print("=" * 50)
print(scheduler.explain_plan())
