import pandas as pd
from datetime import datetime
import os

TASKS_FILE = "tasks.csv"

def load_tasks():
    """Load tasks from CSV file or create empty DataFrame if file doesn't exist"""
    if os.path.exists(TASKS_FILE):
        try:
            # Try to read with all columns
            return pd.read_csv(TASKS_FILE, parse_dates=['due_date', 'created_at', 'started_at', 'completed_at'])
        except ValueError:
            # If timing columns don't exist, read basic columns and add timing columns
            df = pd.read_csv(TASKS_FILE, parse_dates=['due_date', 'created_at'])
            df['started_at'] = None
            df['completed_at'] = None
            df['time_spent'] = 0
            return df
    return pd.DataFrame(columns=[
        'name', 'category', 'priority', 'due_date', 'description',
        'status', 'created_at', 'started_at', 'completed_at', 'time_spent'
    ])

def save_tasks(tasks_df):
    """Save tasks to CSV file"""
    tasks_df.to_csv(TASKS_FILE, index=False)
    return tasks_df

def add_task(task):
    """Add a new task to the DataFrame"""
    task['started_at'] = None
    task['completed_at'] = None
    task['time_spent'] = 0
    tasks_df = load_tasks()
    tasks_df = pd.concat([tasks_df, pd.DataFrame([task])], ignore_index=True)
    return save_tasks(tasks_df)

def update_task_status(task_idx, status):
    """Update task status and timing"""
    tasks_df = load_tasks()
    tasks_df.loc[task_idx, 'status'] = status

    if status == "In Progress" and pd.isna(tasks_df.loc[task_idx, 'started_at']):
        tasks_df.loc[task_idx, 'started_at'] = datetime.now()
    elif status == "Completed" and pd.isna(tasks_df.loc[task_idx, 'completed_at']):
        tasks_df.loc[task_idx, 'completed_at'] = datetime.now()
        if not pd.isna(tasks_df.loc[task_idx, 'started_at']):
            time_spent = (datetime.now() - pd.to_datetime(tasks_df.loc[task_idx, 'started_at'])).total_seconds() / 60
            tasks_df.loc[task_idx, 'time_spent'] = time_spent

    return save_tasks(tasks_df)