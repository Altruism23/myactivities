import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def display_category_distribution(df):
    """Display category distribution chart"""
    if len(df) == 0:
        st.info("No tasks available to display statistics")
        return

    category_counts = df['category'].value_counts()

    fig = px.bar(
        x=category_counts.index,
        y=category_counts.values,
        title="Tasks by Category",
        labels={'x': 'Category', 'y': 'Number of Tasks'},
        color=category_counts.index,
        text=category_counts.values
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        showlegend=False,
        height=250,
        margin=dict(t=30, b=0, l=0, r=0),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

def display_priority_distribution(df):
    """Display priority distribution chart"""
    if len(df) == 0:
        return

    priority_order = ['Urgent', 'High', 'Normal', 'Low']
    priority_counts = df['priority'].value_counts().reindex(priority_order).fillna(0)

    colors = {
        'Urgent': '#ff4b4b',
        'High': '#ffa07a',
        'Normal': '#90ee90',
        'Low': '#add8e6'
    }

    fig = go.Figure(data=[
        go.Bar(
            x=priority_counts.index,
            y=priority_counts.values,
            marker_color=[colors[p] for p in priority_counts.index],
            text=priority_counts.values,
            textposition='outside'
        )
    ])

    fig.update_layout(
        title="Tasks by Priority",
        height=250,
        margin=dict(t=30, b=0, l=0, r=0),
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

def display_completion_rate(df):
    """Display completion rate gauge chart"""
    if len(df) == 0:
        return

    completion_rate = (df['status'] == 'Completed').mean() * 100
    pending_rate = (df['status'] == 'Pending').mean() * 100
    in_progress_rate = (df['status'] == 'In Progress').mean() * 100

    # Create a more compact layout for status distribution
    fig = go.Figure()

    # Add status distribution bar
    fig.add_trace(go.Bar(
        x=['Completed', 'In Progress', 'Pending'],
        y=[completion_rate, in_progress_rate, pending_rate],
        marker_color=['#90ee90', '#ffd700', '#ff4b4b'],
        text=[f'{v:.1f}%' for v in [completion_rate, in_progress_rate, pending_rate]],
        textposition='outside'
    ))

    fig.update_layout(
        title="Task Status Distribution",
        height=250,
        margin=dict(t=30, b=0, l=0, r=0),
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        yaxis_range=[0, 100],
        yaxis_title="Percentage"
    )

    st.plotly_chart(fig, use_container_width=True)