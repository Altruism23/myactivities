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
            options=["All", "Pending", "Completed"],
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
            col_check, col_content = st.columns([0.1, 0.9])
            with col_check:
                if st.checkbox("", task['status'] == "Completed", key=f"check_{idx}"):
                    st.session_state.tasks = dh.update_task_status(idx, "Completed")
                else:
                    st.session_state.tasks = dh.update_task_status(idx, "Pending")
            
            with col_content:
                task_color = utils.get_priority_color(task['priority'])
                st.markdown(
                    f"""
                    <div style="border-left: 5px solid {task_color}; padding-left: 10px;">
                    <h4>{task['name']}</h4>
                    <p><strong>Category:</strong> {task['category']} | 
                    <strong>Priority:</strong> <span style="color: {task_color}">{task['priority']}</span> | 
                    <strong>Due:</strong> {task['due_date']}</p>
                    <p>{task['description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown("---")

with col2:
    st.subheader("Statistics")
    
    # Display statistics and charts
    viz.display_category_distribution(filtered_tasks)
    viz.display_priority_distribution(filtered_tasks)
    viz.display_completion_rate(filtered_tasks)
