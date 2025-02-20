import pandas as pd
from datetime import datetime
import os

TASKS_FILE = "tasks.csv"

def load_tasks():
    """Load tasks from CSV file or create empty DataFrame if file doesn't exist"""
    if os.path.exists(TASKS_FILE):
        return pd.read_csv(TASKS_FILE, parse_dates=['due_date', 'created_at'])
    return pd.DataFrame(columns=[
        'name', 'category', 'priority', 'due_date', 'description',
        'status', 'created_at'
    ])

def save_tasks(tasks_df):
    """Save tasks to CSV file"""
    tasks_df.to_csv(TASKS_FILE, index=False)
    return tasks_df

def add_task(task):
    """Add a new task to the DataFrame"""
    tasks_df = load_tasks()
    tasks_df = pd.concat([tasks_df, pd.DataFrame([task])], ignore_index=True)
    return save_tasks(tasks_df)

def update_task_status(task_idx, status):
    """Update task status"""
    tasks_df = load_tasks()
    tasks_df.loc[task_idx, 'status'] = status
    return save_tasks(tasks_df)
