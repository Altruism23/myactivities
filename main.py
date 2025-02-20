import streamlit as st
import pandas as pd
from datetime import datetime
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

# Main title
st.title("📝 Daily Activity Tracker")

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
    due_date = st.date_input("Due Date")
    description = st.text_area("Description")

    if st.button("Add Task"):
        if task_name:
            new_task = {
                'name': task_name,
                'category': category,
                'priority': priority,
                'due_date': due_date,
                'description': description,
                'status': 'Pending',
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.tasks = dh.add_task(new_task)
            st.success("Task added successfully!")
        else:
            st.error("Task name is required!")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
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
                st.markdown(
                    f"""
                    <div style="border-left: 5px solid {task_color}; padding-left: 10px;">
                    <h4>{task['name']}</h4>
                    <p><strong>Category:</strong> {task['category']} | 
                    <strong>Priority:</strong> <span style="color: {task_color}">{task['priority']}</span></p>
                    <p><strong>Due:</strong> {task['due_date']} |
                    <strong>Created:</strong> {pd.to_datetime(task['created_at']).strftime('%Y-%m-%d %H:%M')}</p>
                    <p>{task['description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_time:
                if task['status'] == "Completed":
                    time_spent = task['time_spent']
                    completed_at = pd.to_datetime(task['completed_at']).strftime('%Y-%m-%d %H:%M')
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

with col2:
    st.subheader("Statistics")

    # Display statistics and charts
    viz.display_category_distribution(filtered_tasks)
    viz.display_priority_distribution(filtered_tasks)
    viz.display_completion_rate(filtered_tasks)