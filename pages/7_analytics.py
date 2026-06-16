import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.analytics import get_topic_accuracy, get_attempts_over_time
from utils.database import get_connection
import pandas as pd

st.set_page_config(page_title="Analytics | CAT Practice", layout="wide")

st.title("📈 Detailed Analytics")

# --- Accuracy by Section ---
conn = get_connection()
section_df = pd.read_sql_query("""
    SELECT q.section, a.is_correct
    FROM attempts a
    JOIN questions q ON a.question_id = q.id
""", conn)

if len(section_df) > 0:
    sec_grouped = section_df.groupby('section').agg(
        attempts=('is_correct', 'count'),
        correct=('is_correct', 'sum')
    ).reset_index()
    sec_grouped['accuracy'] = (sec_grouped['correct'] / sec_grouped['attempts']) * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Accuracy by Section")
        fig1 = px.bar(sec_grouped, x='section', y='accuracy', color='section', text='accuracy')
        fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.subheader("Attempts Distribution")
        fig2 = px.pie(sec_grouped, names='section', values='attempts', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No attempts recorded yet.")
    
st.markdown("---")

# --- Progress Over Time ---
st.subheader("Improvement Trend (Attempts & Accuracy Over Time)")
time_df = get_attempts_over_time()

if not time_df.empty:
    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(x=time_df['date'], y=time_df['attempts'], name='Attempts', marker_color='lightblue'))
    fig_time.add_trace(go.Scatter(x=time_df['date'], y=time_df['accuracy'], name='Accuracy %', yaxis='y2', line=dict(color='green', width=3)))
    
    fig_time.update_layout(
        yaxis=dict(title='Number of Attempts'),
        yaxis2=dict(title='Accuracy %', overlaying='y', side='right', range=[0, 100]),
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.write("Not enough data to show trends.")

st.markdown("---")

# --- Deep Dive Topics ---
st.subheader("Topic Deep Dive")
topic_df = get_topic_accuracy()
if not topic_df.empty:
    fig_scatter = px.scatter(
        topic_df, x="total_attempts", y="accuracy", color="section", hover_name="topic",
        size="total_attempts", size_max=40,
        title="Topic Mastery Matrix (Size = Attempts)",
        labels={"total_attempts": "Total Attempts", "accuracy": "Accuracy (%)"}
    )
    # Add horizontal line for 70% target
    fig_scatter.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Target 70%")
    st.plotly_chart(fig_scatter, use_container_width=True)

# Mock history
mock_df = pd.read_sql_query("SELECT * FROM mock_history ORDER BY timestamp DESC", conn)
if not mock_df.empty:
    st.markdown("---")
    st.subheader("Mock Test History")
    
    mock_df['timestamp'] = pd.to_datetime(mock_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
    st.dataframe(mock_df[['mock_type', 'score', 'qa_score', 'varc_score', 'dilr_score', 'timestamp']], use_container_width=True)

conn.close()
