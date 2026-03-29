import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session state init ─────────────────────────────────────────────────────────
# Guard: only create these objects once; survive every Streamlit rerun
if "owner" not in st.session_state:
    st.session_state.owner = None       # set when owner form is submitted

if "current_pet" not in st.session_state:
    st.session_state.current_pet = None # set when pet form is submitted

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None   # set when Generate Schedule is clicked

# ── Section 1: Owner setup ─────────────────────────────────────────────────────
st.header("1. Owner Info")

with st.form("owner_form"):
    owner_name       = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=90)
    submitted = st.form_submit_button("Save owner")

if submitted:
    # Owner.init → stores name + available_minutes, creates empty pets list
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    st.session_state.current_pet = None   # reset pet when owner changes
    st.session_state.scheduler   = None
    st.success(f"Owner '{owner_name}' saved with {available_minutes} min available.")

owner: Owner = st.session_state.owner

if owner is None:
    st.info("Fill in owner info above to get started.")
    st.stop()   # nothing else renders until an owner exists

# ── Section 2: Add a Pet ───────────────────────────────────────────────────────
st.header("2. Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species  = st.selectbox("Species", ["dog", "cat", "other"])
    age      = st.number_input("Age", min_value=0, max_value=30, value=3)
    pet_submitted = st.form_submit_button("Add pet")

if pet_submitted:
    new_pet = Pet(name=pet_name, species=species, age=age)
    owner.add_pet(new_pet)                          # Owner.add_pet() stores it in owner.pets
    st.session_state.current_pet = new_pet          # make it the active pet for task-adding
    st.success(f"Added pet: {new_pet.get_info()}")  # Pet.get_info() drives the confirmation

if owner.pets:
    st.write("**Registered pets:**")
    for pet in owner.pets:
        st.write(f"- {pet.get_info()}")             # Pet.get_info() updates live
else:
    st.info("No pets added yet.")

# ── Section 3: Add Tasks to a Pet ─────────────────────────────────────────────
st.header("3. Add Tasks")

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    pet_names    = [p.name for p in owner.pets]
    selected_name = st.selectbox("Select pet to add task to", pet_names)
    selected_pet  = next(p for p in owner.pets if p.name == selected_name)

    with st.form("task_form"):
        task_title = st.text_input("Task title", value="Morning walk")
        duration   = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority   = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        task_type  = st.selectbox("Task type", ["walk", "feeding", "meds", "grooming", "enrichment", "other"])
        task_submitted = st.form_submit_button("Add task")

    if task_submitted:
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            task_type=task_type,
        )
        selected_pet.add_task(new_task)   # Pet.add_task() appends to pet.tasks
        st.success(f"Added: {new_task}")  # Task.__repr__() drives the confirmation message

    if selected_pet.tasks:
        st.write(f"**Tasks for {selected_pet.name}:**")
        for task in selected_pet.tasks:
            st.write(f"- {task}")         # Task.__repr__() renders each row
    else:
        st.info(f"No tasks for {selected_pet.name} yet.")

# ── Section 4: Generate Schedule ──────────────────────────────────────────────
st.header("4. Today's Schedule")

if st.button("Generate schedule"):
    # Scheduler takes only owner; it pulls all pets + tasks through owner.get_all_pending_tasks()
    scheduler = Scheduler(owner)
    scheduler.generate_plan()                       # greedy sort by priority, fits time budget
    st.session_state.scheduler = scheduler

if st.session_state.scheduler:
    st.text(st.session_state.scheduler.explain_plan())  # Scheduler.explain_plan() renders reasoning
