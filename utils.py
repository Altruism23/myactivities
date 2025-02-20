def get_priority_color(priority):
    """Return color code for priority level"""
    colors = {
        'Urgent': '#ff4b4b',
        'High': '#ffa07a',
        'Normal': '#90ee90',
        'Low': '#add8e6'
    }
    return colors.get(priority, '#000000')

def filter_tasks(df, categories, priorities, statuses):
    """Filter tasks based on selected criteria"""
    filtered_df = df.copy()
    
    if "All" not in categories:
        filtered_df = filtered_df[filtered_df['category'].isin(categories)]
    
    if "All" not in priorities:
        filtered_df = filtered_df[filtered_df['priority'].isin(priorities)]
    
    if "All" not in statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(statuses)]
    
    return filtered_df
