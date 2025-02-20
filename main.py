import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import data_handler as dh
import visualizations as viz
import utils

# Page config
st.set_page_config(
    page_title="Daily Activity Tracker",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = dh.load_tasks()
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

# Main title
st.title("📝 Daily Activity Tracker")

# Calendar View
st.subheader("📅 Calendar View")
cal_col1, cal_col2 = st.columns([1, 3])

with cal_col1:
    # Calendar date picker
    selected_date = st.date_input(
        "Select Date",
        value=st.session_state.selected_date,
        key="calendar_date"
    )
    st.session_state.selected_date = selected_date

    # Quick date navigation
    if st.button("⬅️ Previous Day"):
        st.session_state.selected_date -= timedelta(days=1)
        st.rerun()
    if st.button("➡️ Next Day"):
        st.session_state.selected_date += timedelta(days=1)
        st.rerun()
    if st.button("📍 Today"):
        st.session_state.selected_date = datetime.now().date()
        st.rerun()

with cal_col2:
    # Filter tasks for selected date
    daily_tasks = st.session_state.tasks[
        pd.to_datetime(st.session_state.tasks['scheduled_start']).dt.date == selected_date
    ]

    if len(daily_tasks) > 0:
        st.write(f"Tasks scheduled for {selected_date.strftime('%B %d, %Y')}:")
        for _, task in daily_tasks.iterrows():
            scheduled_time = pd.to_datetime(task['scheduled_start']).strftime('%H:%M')
            status_color = {
                'Completed': '🟢',
                'In Progress': '🟡',
                'Pending': '⚪'
            }.get(task['status'], '⚪')

            st.markdown(f"""
            {status_color} **{scheduled_time}** - {task['name']}  
            Priority: {task['priority']} | Category: {task['category']}  
            """)
    else:
        st.info(f"No tasks scheduled for {selected_date.strftime('%B %d, %Y')}")

# Sidebar for task creation
with st.sidebar:
    st.header("Add New Task")

    task_name = st.text_input("Task Name")
    category = st.selectbox(
        "Category",
        ["Work", "Personal", "Shopping", "Health", "Other"]
    )
    priority = st.selectbox(
        "Priority",
        ["Urgent", "High", "Normal", "Low"]
    )

    # Add date and time inputs
    due_date = st.date_input("Due Date")

    # Custom time selection
    st.write("Scheduled Start Time")
    time_col1, time_col2 = st.columns(2)
    with time_col1:
        hour = st.number_input("Hour (24-hour)", min_value=0, max_value=23, value=datetime.now().hour)
    with time_col2:
        minute = st.number_input("Minute", min_value=0, max_value=59, value=datetime.now().minute)

    # Show selected time
    scheduled_time = time(hour=int(hour), minute=int(minute))
    st.write(f"Selected time: {scheduled_time.strftime('%H:%M')}")

    description = st.text_area("Description")

    if st.button("Add Task"):
        if task_name:
            # Combine date and time for scheduled start
            scheduled_datetime = datetime.combine(due_date, scheduled_time)

            new_task = {
                'name': task_name,
                'category': category,
                'priority': priority,
                'due_date': due_date,
                'description': description,
                'status': 'Pending',
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'scheduled_start': scheduled_datetime.strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.tasks = dh.add_task(new_task)
            st.success("Task added successfully!")
        else:
            st.error("Task name is required!")

# Main content area
st.subheader("Tasks Overview")

# Filters
filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    filter_category = st.multiselect(
        "Filter by Category",
        options=["All"] + list(st.session_state.tasks['category'].unique()),
        default="All"
    )
with filter_col2:
    filter_priority = st.multiselect(
        "Filter by Priority",
        options=["All"] + list(st.session_state.tasks['priority'].unique()),
        default="All"
    )
with filter_col3:
    filter_status = st.multiselect(
        "Filter by Status",
        options=["All", "Pending", "In Progress", "Completed"],
        default="All"
    )

# Apply filters
filtered_tasks = utils.filter_tasks(
    st.session_state.tasks,
    filter_category,
    filter_priority,
    filter_status
)

# Display tasks
for idx, task in filtered_tasks.iterrows():
    with st.container():
        col_status, col_content, col_time = st.columns([0.2, 0.6, 0.2])

        with col_status:
            status = st.selectbox(
                "Status",
                options=["Pending", "In Progress", "Completed"],
                index=["Pending", "In Progress", "Completed"].index(task['status']),
                key=f"status_{idx}",
                label_visibility="collapsed"
            )
            if status != task['status']:
                st.session_state.tasks = dh.update_task_status(idx, status)

        with col_content:
            task_color = utils.get_priority_color(task['priority'])
            scheduled_start_time = pd.to_datetime(task['scheduled_start']).strftime('%Y-%m-%d %H:%M') if pd.notnull(task.get('scheduled_start')) else 'N/A'

            st.markdown(
                f"""
                <div style="border-left: 5px solid {task_color}; padding-left: 10px;">
                <h4>{task['name']}</h4>
                <p><strong>Category:</strong> {task['category']} | 
                <strong>Priority:</strong> <span style="color: {task_color}">{task['priority']}</span></p>
                <p><strong>Due:</strong> {task['due_date']} |
                <strong>Created:</strong> {pd.to_datetime(task['created_at']).strftime('%Y-%m-%d %H:%M')} |
                <strong>Scheduled Start:</strong> {scheduled_start_time}</p>
                <p>{task['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_time:
            if task['status'] == "Completed":
                time_spent = task['time_spent']
                completed_at = pd.to_datetime(task['completed_at']).strftime('%Y-%m-%d %H:%M') if pd.notnull(task['completed_at']) else 'N/A'
                st.write(f"✅ Completed at: {completed_at}")
                st.write(f"⏱️ Time spent: {time_spent:.1f} min")
            elif task['status'] == "In Progress":
                if not pd.isna(task['started_at']):
                    current_time = datetime.now()
                    started_time = pd.to_datetime(task['started_at'])
                    started_at = started_time.strftime('%Y-%m-%d %H:%M')
                    elapsed_time = (current_time - started_time).total_seconds() / 60
                    st.write(f"🚀 Started at: {started_at}")
                    st.write(f"⏱️ Time elapsed: {elapsed_time:.1f} min")

        st.markdown("---")

# Summary section at the bottom
st.markdown("### 📊 Task Summary")
if len(filtered_tasks) > 0:
    total_tasks = len(filtered_tasks)
    completed_tasks = len(filtered_tasks[filtered_tasks['status'] == 'Completed'])
    in_progress_tasks = len(filtered_tasks[filtered_tasks['status'] == 'In Progress'])
    pending_tasks = len(filtered_tasks[filtered_tasks['status'] == 'Pending'])

    # Create three columns for the summary
    sum_col1, sum_col2, sum_col3 = st.columns(3)

    with sum_col1:
        st.metric("🎯 Total Tasks", total_tasks)
    with sum_col2:
        st.metric("✅ Completed", f"{completed_tasks} ({(completed_tasks/total_tasks*100):.1f}%)")
    with sum_col3:
        st.metric("⏳ In Progress", f"{in_progress_tasks} ({(in_progress_tasks/total_tasks*100):.1f}%)")

    # Progress bar
    st.progress(completed_tasks/total_tasks)

    # Task distribution
    st.markdown(f"""
    ### Task Distribution
    - 🟢 **Completed Tasks:** {completed_tasks} ({(completed_tasks/total_tasks*100):.1f}%)
    - 🟡 **In Progress:** {in_progress_tasks} ({(in_progress_tasks/total_tasks*100):.1f}%)
    - ⚪ **Pending:** {pending_tasks} ({(pending_tasks/total_tasks*100):.1f}%)
    """)
else:
    st.info("No tasks available to display statistics")

# Pagination Settings
items_per_page = 5
total_tasks = len(filtered_tasks)
total_pages = (total_tasks // items_per_page) + (1 if total_tasks % items_per_page > 0 else 0)

# Initialize session state for pagination
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Page Navigation
col_prev, col_page, col_next = st.columns([1, 2, 1])

with col_prev:
    if st.button("⬅️ Previous", disabled=(st.session_state.current_page <= 1)):
        st.session_state.current_page -= 1

with col_page:
    st.markdown(f"**Page {st.session_state.current_page} of {total_pages}**")

with col_next:
    if st.button("➡️ Next", disabled=(st.session_state.current_page >= total_pages)):
        st.session_state.current_page += 1

# Determine Start and End Index for Pagination
start_idx = (st.session_state.current_page - 1) * items_per_page
end_idx = start_idx + items_per_page

# Display Tasks for Current Page
for idx, task in filtered_tasks.iloc[start_idx:end_idx].iterrows():
    with st.container():
        col_status, col_content, col_time = st.columns([0.2, 0.6, 0.2])

        with col_status:
            status = st.selectbox(
                "Status",
                options=["Pending", "In Progress", "Completed"],
                index=["Pending", "In Progress", "Completed"].index(task['status']),
                key=f"status_{st.session_state.current_page}_{idx}",
                label_visibility="collapsed"
            )
            if status != task['status']:
                st.session_state.tasks = dh.update_task_status(idx, status)

        with col_content:
            task_color = utils.get_priority_color(task['priority'])
            scheduled_start_time = pd.to_datetime(task['scheduled_start']).strftime('%Y-%m-%d %H:%M') if pd.notnull(task.get('scheduled_start')) else 'N/A'

            st.markdown(
                f"""
                <div style="border-left: 5px solid {task_color}; padding-left: 10px;">
                <h4>{task['name']}</h4>
                <p><strong>Category:</strong> {task['category']} | 
                <strong>Priority:</strong> <span style="color: {task_color}">{task['priority']}</span></p>
                <p><strong>Due:</strong> {task['due_date']} |
                <strong>Created:</strong> {pd.to_datetime(task['created_at']).strftime('%Y-%m-%d %H:%M')} |
                <strong>Scheduled Start:</strong> {scheduled_start_time}</p>
                <p>{task['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_time:
            if task['status'] == "Completed":
                time_spent = task['time_spent']
                completed_at = pd.to_datetime(task['completed_at']).strftime('%Y-%m-%d %H:%M') if pd.notnull(task['completed_at']) else 'N/A'
                st.write(f"✅ Completed at: {completed_at}")
                st.write(f"⏱️ Time spent: {time_spent:.1f} min")
            elif task['status'] == "In Progress":
                if not pd.isna(task['started_at']):
                    current_time = datetime.now()
                    started_time = pd.to_datetime(task['started_at'])
                    started_at = started_time.strftime('%Y-%m-%d %H:%M')
                    elapsed_time = (current_time - started_time).total_seconds() / 60
                    st.write(f"🚀 Started at: {started_at}")
                    st.write(f"⏱️ Time elapsed: {elapsed_time:.1f} min")

        st.markdown("---")