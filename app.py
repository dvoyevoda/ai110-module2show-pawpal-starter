import streamlit as st
from datetime import date
from html import escape
from pawpal_system import Owner, Pet, Task, Schedule, sort_by_time_slot

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ---------- Session state: persist the Owner across reruns ----------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_time=60)

owner: Owner = st.session_state.owner


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --pp-bg-start: #f8fbff;
            --pp-bg-end: #eef4ff;
            --pp-surface: #ffffff;
            --pp-border: #dbe5f2;
            --pp-text: #0f172a;
            --pp-muted: #475569;
            --pp-brand: #1d4ed8;
            --pp-brand-dark: #1e3a8a;
        }

        .stApp {
            background:
                radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.15), transparent 40%),
                radial-gradient(circle at 95% 5%, rgba(14, 165, 233, 0.12), transparent 35%),
                linear-gradient(180deg, var(--pp-bg-start) 0%, var(--pp-bg-end) 100%);
            color: var(--pp-text);
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        .block-container {
            max-width: 1150px;
            padding-top: 1.4rem;
            padding-bottom: 2.4rem;
        }
        .stApp,
        .stApp [data-testid="stMarkdownContainer"] {
            font-size: 16px;
            line-height: 1.45;
        }
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stCaptionContainer"] {
            color: var(--pp-text) !important;
        }
        [data-testid="stMarkdownContainer"] h1 {
            font-size: 2rem;
            line-height: 1.2;
            margin: 0.2rem 0 0.7rem 0;
            letter-spacing: -0.01em;
        }
        [data-testid="stMarkdownContainer"] h2 {
            font-size: 1.6rem;
            line-height: 1.25;
            margin: 0.2rem 0 0.7rem 0;
            letter-spacing: -0.01em;
        }
        [data-testid="stMarkdownContainer"] h3 {
            font-size: 1.35rem;
            line-height: 1.3;
            margin: 0.15rem 0 0.65rem 0;
            letter-spacing: -0.005em;
            padding-left: 0.5rem;
        }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            font-size: 1rem;
            line-height: 1.55;
        }
        [data-testid="stCaptionContainer"] {
            font-size: 0.9rem !important;
            line-height: 1.45 !important;
            color: #5b6b81 !important;
        }
        [data-testid="stWidgetLabel"] {
            margin-bottom: 0.24rem;
        }
        [data-testid="stWidgetLabel"] p {
            color: var(--pp-muted) !important;
            font-size: 0.95rem !important;
            line-height: 1.35 !important;
            font-weight: 500 !important;
            padding-left: 0.46rem !important;
        }
        .pp-inline-heading {
            color: var(--pp-text) !important;
            font-size: 1.03rem !important;
            font-weight: 600 !important;
            margin: 0.1rem 0 0.55rem 0 !important;
            padding-left: 0.5rem !important;
            line-height: 1.35 !important;
        }
        .hero-card {
            border-radius: 18px;
            padding: 1.25rem 1.4rem;
            background: linear-gradient(120deg, #1d4f91, #1a6f8e);
            box-shadow: 0 10px 28px rgba(20, 52, 95, 0.2);
            margin-bottom: 1rem;
        }
        .hero-kicker {
            font-size: 0.82rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.9;
            font-weight: 600;
            margin-bottom: 0.25rem;
            display: inline-block;
            color: #e7f2ff !important;
        }
        .hero-card h1 {
            margin: 0.1rem 0 0.35rem 0;
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff !important;
        }
        .hero-card p {
            margin: 0;
            font-size: 1rem;
            line-height: 1.45;
            color: #e6f4ff !important;
        }
        .pp-metric-card {
            border: 1px solid var(--pp-border);
            background: var(--pp-surface);
            border-radius: 14px;
            min-height: 5.2rem;
            padding: 0.9rem 1.25rem 0.95rem !important;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
            margin-bottom: 0.3rem;
        }
        .pp-metric-label {
            color: var(--pp-muted) !important;
            font-size: 0.9rem !important;
            line-height: 1.2 !important;
            font-weight: 600 !important;
            margin: 0 !important;
            padding-left: 0.5rem !important;
        }
        .pp-metric-value {
            color: var(--pp-text) !important;
            font-size: 2.1rem !important;
            line-height: 1.05 !important;
            margin-top: 0.3rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em;
            padding-left: 0.5rem !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--pp-surface);
            border: 1px solid var(--pp-border);
            border-radius: 14px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }
        [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }
        button[data-baseweb="tab"] {
            color: var(--pp-muted) !important;
            background: rgba(255, 255, 255, 0.65) !important;
            border-radius: 10px 10px 0 0 !important;
            border: 1px solid #d8e2ef !important;
            font-size: 0.98rem !important;
            line-height: 1.2 !important;
            padding: 0.52rem 0.88rem !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--pp-brand-dark) !important;
            background: #ffffff !important;
            border-bottom: 2px solid var(--pp-brand) !important;
            font-weight: 600 !important;
        }
        .stButton > button, .stFormSubmitButton > button {
            border: none !important;
            border-radius: 10px !important;
            background: linear-gradient(120deg, #2563eb, #0f766e) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            padding: 0.48rem 1.05rem !important;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            filter: brightness(1.03);
        }
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
            background: #ffffff !important;
            color: var(--pp-text) !important;
            border: 1px solid var(--pp-border) !important;
            border-radius: 10px !important;
            font-size: 1rem !important;
            line-height: 1.35 !important;
            padding: 0.62rem 0.85rem !important;
        }
        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            color: var(--pp-text) !important;
            border: 1px solid var(--pp-border) !important;
            border-radius: 10px !important;
            min-height: 2.7rem !important;
            padding-left: 0.72rem !important;
            padding-right: 0.72rem !important;
        }
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] input {
            color: var(--pp-text) !important;
            font-size: 1rem !important;
            line-height: 1.35 !important;
        }
        .stMultiSelect [data-baseweb="tag"] {
            background: #e8efff !important;
            color: #1e3a8a !important;
            border: 1px solid #c7d6fb !important;
            font-size: 0.88rem !important;
            line-height: 1.25 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def task_rows(tasks: list[Task]) -> list[dict[str, str | int]]:
    """Convert Task objects into table-friendly dictionaries."""
    rows: list[dict[str, str | int]] = []
    for task in tasks:
        rows.append(
            {
                "Pet": task.pet_name or "-",
                "Task": task.name,
                "Category": task.category,
                "Time": task.time_slot,
                "Duration (min)": task.duration,
                "Priority": task.priority,
                "Recurs": task.recurrence,
                "Status": "Completed" if task.completed else "Pending",
                "Due Date": task.due_date or "-",
            }
        )
    return rows


def pet_rows(pets: list[Pet]) -> list[dict[str, str | int]]:
    """Create a compact pet summary table."""
    rows: list[dict[str, str | int]] = []
    for pet in pets:
        pending = len([task for task in pet.tasks if not task.completed])
        completed = len(pet.tasks) - pending
        rows.append(
            {
                "Name": pet.name,
                "Species": pet.species,
                "Breed": pet.breed or "-",
                "Age": pet.age,
                "Pending Tasks": pending,
                "Completed Tasks": completed,
            }
        )
    return rows


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <span class="hero-kicker">Pet Care Command Center</span>
            <h1>🐾 PawPal+</h1>
            <p>
                Build smart daily plans for walks, feeding, meds, enrichment, and grooming
                with a cleaner workflow and scheduling transparency.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str | int) -> None:
    """Render a custom metric card with predictable text inset."""
    safe_label = escape(str(label))
    safe_value = escape(str(value))
    st.markdown(
        f"""
        <div class="pp-metric-card">
            <p class="pp-metric-label">{safe_label}</p>
            <p class="pp-metric-value">{safe_value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(current_owner: Owner) -> None:
    all_tasks = [task for pet in current_owner.pets for task in pet.tasks]
    pending_count = len([task for task in all_tasks if not task.completed])
    completed_count = len(all_tasks) - pending_count

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        render_metric_card("Pets", len(current_owner.pets))
    with m_col2:
        render_metric_card("Pending tasks", pending_count)
    with m_col3:
        render_metric_card("Completed tasks", completed_count)
    with m_col4:
        render_metric_card("Daily time budget", f"{current_owner.available_time} min")


inject_styles()
render_hero()
render_metrics(owner)

tab_setup, tab_tasks, tab_schedule = st.tabs(["Owner & Pets", "Tasks", "Schedule"])

with tab_setup:
    st.subheader("Owner Profile")
    with st.container(border=True):
        col_name, col_time = st.columns(2)
        with col_name:
            owner.name = st.text_input("Your name", value=owner.name, placeholder="Alex")
        with col_time:
            owner.available_time = st.number_input(
                "Available time (minutes/day)",
                min_value=1,
                max_value=480,
                value=owner.available_time,
            )

        owner.preferences = st.multiselect(
            "Preferred task categories (these receive a scheduling boost)",
            options=["walk", "feeding", "meds", "enrichment", "grooming"],
            default=owner.preferences,
        )

    st.subheader("Pets")
    with st.container(border=True):
        with st.form("add_pet_form", clear_on_submit=True):
            st.markdown('<div class="pp-inline-heading">Add a new pet</div>', unsafe_allow_html=True)
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                pet_name = st.text_input("Pet name")
            with p_col2:
                pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
            with p_col3:
                pet_breed = st.text_input("Breed (optional)")
            pet_age = st.number_input("Age", min_value=0, max_value=30, value=1)
            add_pet = st.form_submit_button("Add Pet")

        if add_pet and pet_name.strip():
            owner.add_pet(
                Pet(
                    name=pet_name.strip(),
                    species=pet_species,
                    breed=pet_breed.strip(),
                    age=pet_age,
                )
            )
            st.success(f"Added {pet_name.strip()}!")
            st.rerun()
        elif add_pet:
            st.error("Please enter a pet name before submitting.")

        if owner.pets:
            st.markdown('<div class="pp-inline-heading">Current pets</div>', unsafe_allow_html=True)
            st.dataframe(
                pet_rows(owner.pets),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No pets yet. Add your first pet above.")

with tab_tasks:
    if owner.pets:
        st.subheader("Task Explorer")
        with st.container(border=True):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                filter_pet = st.selectbox("By pet", ["All"] + [pet.name for pet in owner.pets])
            with f_col2:
                filter_status = st.selectbox("By status", ["All", "Pending", "Completed"])
            with f_col3:
                filter_time = st.selectbox("By time slot", ["all", "morning", "midday", "evening", "anytime"])

            pet_filter = None if filter_pet == "All" else filter_pet
            status_filter = None if filter_status == "All" else filter_status.lower()

            filtered_tasks = owner.filter_tasks(
                pet_name=pet_filter,
                status=status_filter,
                time_slot=filter_time,
            )
            filtered_sorted = sort_by_time_slot(filtered_tasks)

            st.caption(f"Showing {len(filtered_sorted)} task(s) with current filters.")
            if filtered_sorted:
                st.dataframe(
                    task_rows(filtered_sorted),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No tasks match the current filters.")

        st.subheader("Add a Task")
        with st.container(border=True):
            with st.form("add_task_form", clear_on_submit=True):
                target_pet_name = st.selectbox("Assign to pet", [pet.name for pet in owner.pets])

                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    task_name = st.text_input("Task name")
                    task_category = st.selectbox(
                        "Category",
                        ["walk", "feeding", "meds", "enrichment", "grooming"],
                    )
                    task_time_slot = st.selectbox(
                        "Time of day",
                        ["anytime", "morning", "midday", "evening"],
                    )
                with t_col2:
                    task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=15)
                    task_priority = st.slider("Priority", min_value=1, max_value=5, value=3)
                    task_recurrence = st.selectbox(
                        "Recurrence",
                        ["none", "daily", "weekly", "monthly"],
                    )

                task_desc = st.text_input("Description (optional)")
                add_task = st.form_submit_button("Add Task")

            if add_task and task_name.strip():
                target_pet = next(pet for pet in owner.pets if pet.name == target_pet_name)
                target_pet.add_task(
                    Task(
                        name=task_name.strip(),
                        category=task_category,
                        duration=int(task_duration),
                        priority=int(task_priority),
                        description=task_desc.strip(),
                        time_slot=task_time_slot,
                        recurrence=task_recurrence,
                    )
                )
                st.success(f"Added \"{task_name.strip()}\" to {target_pet_name}!")
                st.rerun()
            elif add_task:
                st.error("Please enter a task name before submitting.")
    else:
        st.info("Add at least one pet in the Owner & Pets tab before managing tasks.")

with tab_schedule:
    st.subheader("Build Schedule")
    with st.container(border=True):
        should_generate = st.button("Generate Schedule", use_container_width=True)

        if should_generate:
            owner.expand_recurring_tasks()
            all_tasks = owner.get_all_tasks()

            if not all_tasks:
                st.warning("No pending tasks found. Add tasks to your pets first.")
            else:
                schedule = Schedule(date=str(date.today()))
                schedule.generate_schedule(
                    tasks=all_tasks,
                    available_time=owner.available_time,
                    preferences=owner.preferences,
                )

                st.markdown(f"### Schedule for {schedule.date}")
                utilization = int((schedule.total_duration / owner.available_time) * 100)
                usage_ratio = min(schedule.total_duration / owner.available_time, 1.0)

                s_col1, s_col2, s_col3 = st.columns(3)
                with s_col1:
                    render_metric_card("Accepted tasks", len(schedule.tasks))
                with s_col2:
                    render_metric_card("Skipped tasks", len(schedule.get_skipped_tasks()))
                with s_col3:
                    render_metric_card("Time used", f"{schedule.total_duration} / {owner.available_time} min")

                st.progress(usage_ratio)
                st.caption(f"{utilization}% of your daily time budget is allocated.")

                remaining = schedule.get_remaining_time(owner.available_time)
                if remaining > 0:
                    st.info(f"{remaining} min of free time remaining.")
                else:
                    st.success("Great! Your full available time is allocated.")

                conflicts = schedule.get_conflicts()
                st.markdown("#### Conflict Warnings")
                if conflicts:
                    for warning in conflicts:
                        st.warning(warning)
                    st.caption(
                        "Tip: Move one of the conflicting tasks to another slot or reduce overlap between pets."
                    )
                else:
                    st.success("No schedule conflicts detected.")

                st.markdown("#### Scheduled Tasks (Sorted Chronologically)")
                st.dataframe(
                    task_rows(schedule.tasks),
                    use_container_width=True,
                    hide_index=True,
                )

                skipped_tasks = schedule.get_skipped_tasks()
                if skipped_tasks:
                    st.markdown("#### Skipped (not enough time)")
                    st.dataframe(
                        task_rows(skipped_tasks),
                        use_container_width=True,
                        hide_index=True,
                    )

                    fillers = schedule.suggest_fillers(owner.available_time)
                    if fillers:
                        st.markdown("#### Could still fit")
                        st.dataframe(
                            task_rows(fillers),
                            use_container_width=True,
                            hide_index=True,
                        )

                with st.expander("Full scheduling reasoning"):
                    st.text(schedule.explain_reasoning())
        else:
            st.caption("Generate a schedule to see conflicts, utilization, and recommendations.")
