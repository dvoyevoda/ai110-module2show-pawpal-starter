import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule, detect_conflicts

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------- Session state: persist the Owner across reruns ----------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_time=60)

owner: Owner = st.session_state.owner

# ---------- Header ----------
st.title("🐾 PawPal+")
st.caption("A pet-care planning assistant — add your info, your pets, their tasks, then generate a daily schedule.")

# ---------- Owner info ----------
st.subheader("Owner Info")
col_name, col_time = st.columns(2)
with col_name:
    new_name = st.text_input("Your name", value=owner.name)
    owner.name = new_name
with col_time:
    new_time = st.number_input(
        "Available time (minutes/day)", min_value=1, max_value=480, value=owner.available_time
    )
    owner.available_time = new_time

owner.preferences = st.multiselect(
    "Preferred task categories (get a scheduling boost)",
    options=["walk", "feeding", "meds", "enrichment", "grooming"],
    default=owner.preferences,
)

st.divider()

# ---------- Add a Pet ----------
st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    st.markdown("**Add a new pet**")
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        pet_name = st.text_input("Pet name")
    with p_col2:
        pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
    with p_col3:
        pet_breed = st.text_input("Breed (optional)")
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=1)
    add_pet = st.form_submit_button("Add Pet")

if add_pet and pet_name:
    owner.add_pet(Pet(name=pet_name, species=pet_species, breed=pet_breed, age=pet_age))
    st.success(f"Added {pet_name}!")
    st.rerun()

# ---------- Filter controls ----------
if owner.pets:
    st.markdown("**Filter tasks**")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        filter_pet = st.selectbox("By pet", ["All"] + [p.name for p in owner.pets])
    with f_col2:
        filter_status = st.selectbox("By status", ["All", "Pending", "Completed"])
    with f_col3:
        filter_time = st.selectbox("By time slot", ["all", "morning", "midday", "evening", "anytime"])

    pet_filter = None if filter_pet == "All" else filter_pet
    status_filter = None if filter_status == "All" else filter_status.lower()
    time_filter = filter_time

    filtered = owner.filter_tasks(pet_name=pet_filter, status=status_filter, time_slot=time_filter)

    if not filtered:
        st.info("No tasks match the current filters.")
    else:
        pets_to_show = [p for p in owner.pets if (pet_filter is None or p.name == pet_filter)]
        for pet in pets_to_show:
            pet_tasks = [t for t in filtered if t.pet_name == pet.name]
            if not pet_tasks:
                continue
            with st.expander(f"🐾 {pet.name} ({pet.species})", expanded=True):
                for task in pet_tasks:
                    status = "✅" if task.completed else "⬜"
                    recur_badge = f" 🔁 {task.recurrence}" if task.recurrence != "none" else ""
                    slot_badge = f" 🕐 {task.time_slot}" if task.time_slot != "anytime" else ""
                    st.write(
                        f"{status} **{task.name}** [{task.category}] — "
                        f"{task.duration} min, priority {task.priority}"
                        f"{slot_badge}{recur_badge}"
                    )
else:
    st.info("No pets yet — add one above.")

st.divider()

# ---------- Add a Task to a Pet ----------
if owner.pets:
    st.subheader("Add a Task")

    with st.form("add_task_form", clear_on_submit=True):
        target_pet_name = st.selectbox(
            "Assign to pet", [p.name for p in owner.pets]
        )
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            task_name = st.text_input("Task name")
            task_category = st.selectbox(
                "Category", ["walk", "feeding", "meds", "enrichment", "grooming"]
            )
            task_time_slot = st.selectbox(
                "Time of day", ["anytime", "morning", "midday", "evening"]
            )
        with t_col2:
            task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=15)
            task_priority = st.slider("Priority", min_value=1, max_value=5, value=3)
            task_recurrence = st.selectbox(
                "Recurrence", ["none", "daily", "weekly", "monthly"]
            )
        task_desc = st.text_input("Description (optional)")
        add_task = st.form_submit_button("Add Task")

    if add_task and task_name:
        target_pet = next(p for p in owner.pets if p.name == target_pet_name)
        target_pet.add_task(
            Task(
                name=task_name,
                category=task_category,
                duration=int(task_duration),
                priority=int(task_priority),
                description=task_desc,
                time_slot=task_time_slot,
                recurrence=task_recurrence,
            )
        )
        st.success(f"Added \"{task_name}\" to {target_pet_name}!")
        st.rerun()

    st.divider()

# ---------- Generate Schedule ----------
st.subheader("Build Schedule")

if st.button("Generate Schedule"):
    owner.expand_recurring_tasks()
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("No pending tasks found. Add tasks to your pets first.")
    else:
        pre_conflicts = detect_conflicts(all_tasks)
        if pre_conflicts:
            st.markdown("#### ⚠️ Conflict Warnings")
            for warning in pre_conflicts:
                st.warning(warning)

        schedule = Schedule(date=str(date.today()))
        schedule.generate_schedule(
            tasks=all_tasks,
            available_time=owner.available_time,
            preferences=owner.preferences,
        )
        st.markdown("---")
        st.markdown(f"### 📅 Schedule for {schedule.date}")
        st.markdown(f"**Time used:** {schedule.total_duration} / {owner.available_time} min")

        remaining = schedule.get_remaining_time(owner.available_time)
        if remaining > 0:
            st.caption(f"🕐 {remaining} min of free time remaining")

        st.markdown("#### Scheduled Tasks")
        current_slot = None
        for i, task in enumerate(schedule.tasks, 1):
            if task.time_slot != current_slot:
                current_slot = task.time_slot
                label = current_slot if current_slot != "anytime" else "Flexible"
                st.markdown(f"**— {label.capitalize()} —**")
            recur_tag = f" 🔁" if task.recurrence != "none" else ""
            st.write(
                f"{i}. **{task.name}** ({task.pet_name}) [{task.category}] "
                f"— {task.duration} min (priority {task.priority}){recur_tag}"
            )

        if schedule._skipped:
            st.markdown("#### Skipped (not enough time)")
            for task in schedule._skipped:
                st.write(
                    f"- ~~{task.name}~~ ({task.pet_name}) [{task.category}] "
                    f"— {task.duration} min (priority {task.priority})"
                )

            fillers = schedule.suggest_fillers(owner.available_time)
            if fillers:
                st.markdown("#### 💡 Could still fit")
                for task in fillers:
                    st.write(
                        f"- {task.name} ({task.pet_name}) — {task.duration} min"
                    )

        with st.expander("📝 Full reasoning"):
            st.text(schedule.explain_reasoning())
