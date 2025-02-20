import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def display_category_distribution(df):
    """Display category distribution chart"""
    category_counts = df['category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Tasks by Category",
        hole=0.3
    )
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

def display_priority_distribution(df):
    """Display priority distribution chart"""
    priority_counts = df['priority'].value_counts()
    
    fig = px.bar(
        x=priority_counts.index,
        y=priority_counts.values,
        title="Tasks by Priority",
        color=priority_counts.index,
        color_discrete_map={
            'Urgent': '#ff4b4b',
            'High': '#ffa07a',
            'Normal': '#90ee90',
            'Low': '#add8e6'
        }
    )
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

def display_completion_rate(df):
    """Display completion rate gauge chart"""
    if len(df) > 0:
        completion_rate = (df['status'] == 'Completed').mean() * 100
    else:
        completion_rate = 0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=completion_rate,
        title={'text': "Completion Rate"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#FF4B4B"},
            'steps': [
                {'range': [0, 50], 'color': "#ffeded"},
                {'range': [50, 75], 'color': "#ffcdcd"},
                {'range': [75, 100], 'color': "#ffacac"}
            ]
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
