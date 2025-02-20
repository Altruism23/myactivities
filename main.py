import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import data_handler as dh
import utils

# Page Configuration
st.set_page_config(
    page_title="Daily Activity Tracker",
    page_icon="📝",
    layout="wide"
)

# Initialize Session State
if 'tasks' not in st.session_state:
    st.session_state.tasks = dh.load_tasks()
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

# Main Title
st.title("📝 Daily Activity Tracker")

# Calendar View
st.subheader("📅 Calendar View")
cal_col1, cal_col2 = st.columns([1, 3])

with cal_col1:
    # Date Picker and Navigation
    selected_date = st.date_input("Select Date", value=st.session_state.selected_date, key="calendar_date")
    st.session_state.selected_date = selected_date

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
    # Display Daily Tasks
    daily_tasks = st.session_state.tasks[
        pd.to_datetime(st.session_state.tasks['scheduled_start']).dt.date == selected_date
    ]

    if not daily_tasks.empty:
        st.write(f"Tasks scheduled for {selected_date.strftime('%B %d, %Y')}:")
        for _, task in daily_tasks.iterrows():
            scheduled_time = pd.to_datetime(task['scheduled_start']).strftime('%H:%M')
            status_icon = {
                'Completed': '🟢',
                'In Progress': '🟡',
                'Pending': '⚪'
            }.get(task['status'], '⚪')

            st.markdown(f"""
                {status_icon} **{scheduled_time}** - {task['name']}  
                Priority: {task['priority']} | Category: {task['category']}  
            """)
    else:
        st.info(f"No tasks scheduled for {selected_date.strftime('%B %d, %Y')}")

# Sidebar for Task Creation
with st.sidebar:
    st.header("Add New Task")

    task_name = st.text_input("Task Name")
    category = st.selectbox("Category", ["Work", "Personal", "Shopping", "Health", "Other"])
    priority = st.selectbox("Priority", ["Urgent", "High", "Normal", "Low"])
    due_date = st.date_input("Due Date")

    # Time Selection
    st.write("Scheduled Start Time")
    hour = st.number_input("Hour (24-hour)", min_value=0, max_value=23, value=datetime.now().hour)
    minute = st.number_input("Minute", min_value=0, max_value=59, value=datetime.now().minute)
    scheduled_time = time(hour=int(hour), minute=int(minute))
    st.write(f"Selected time: {scheduled_time.strftime('%H:%M')}")

    description = st.text_area("Description")

    if st.button("Add Task"):
        if task_name:
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

# Task Overview and Filtering
st.subheader("Tasks Overview")

# Filters
filter_category = st.multiselect("Filter by Category", options=["All"] + list(st.session_state.tasks['category'].unique()), default="All")
filter_priority = st.multiselect("Filter by Priority", options=["All"] + list(st.session_state.tasks['priority'].unique()), default="All")
filter_status = st.multiselect("Filter by Status", options=["All", "Pending", "In Progress", "Completed"], default="All")

filtered_tasks = utils.filter_tasks(
    st.session_state.tasks,
    filter_category,
    filter_priority,
    filter_status
)

# Pagination Settings
items_per_page = 5
total_tasks = len(filtered_tasks)
total_pages = (total_tasks // items_per_page) + (1 if total_tasks % items_per_page > 0 else 0)

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

# Display Tasks for Current Page
start_idx = (st.session_state.current_page - 1) * items_per_page
end_idx = start_idx + items_per_page

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
                <strong>Scheduled Start:</strong> {scheduled_start_time}</p>
                <p>{task['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_time:
            if task['status'] == "Completed":
                st.write(f"✅ Completed at: {pd.to_datetime(task['completed_at']).strftime('%Y-%m-%d %H:%M')}")
                st.write(f"⏱️ Time spent: {task['time_spent']:.1f} min")

        st.markdown("---")
