from pawpal_system import Owner, Pet, Task, Scheduler


# --- Create Owner ---
owner = Owner(name="Jordan", available_minutes=90)

# --- Create Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Add Tasks to Mochi (dog) ---
mochi.add_task(Task(title="Morning walk",   duration_minutes=30, priority="high",   task_type="walk"))
mochi.add_task(Task(title="Breakfast",      duration_minutes=10, priority="high",   task_type="feeding"))
mochi.add_task(Task(title="Flea medicine",  duration_minutes=5,  priority="medium", task_type="meds"))

# --- Add Tasks to Luna (cat) ---
luna.add_task(Task(title="Brush coat",      duration_minutes=15, priority="low",    task_type="grooming"))
luna.add_task(Task(title="Dinner",          duration_minutes=10, priority="high",   task_type="feeding"))
luna.add_task(Task(title="Puzzle feeder",   duration_minutes=20, priority="medium", task_type="enrichment"))

# --- Register Pets with Owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Print Pet Summaries ---
print("=== Pets ===")
for pet in owner.pets:
    print(" ", pet.get_info())
print()

# --- Run Scheduler ---
scheduler = Scheduler(owner)
scheduler.generate_plan()

# --- Print Today's Schedule ---
print(scheduler.explain_plan())
