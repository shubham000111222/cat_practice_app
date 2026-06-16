import streamlit as st
import plotly.express as px
from utils.analytics import get_basic_stats, get_topic_accuracy, get_recent_activity

st.set_page_config(page_title="Dashboard | CAT Practice", layout="wide")
st.title("📊 Performance Dashboard")

# Load stats
stats = get_basic_stats()

# Top row metrics
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Questions", stats["total_questions"])
col2.metric("Attempted", stats["attempted"])
col3.metric("Remaining", stats["total_questions"] - stats["attempted"])
col4.metric("Accuracy", f"{stats['accuracy']:.1f}%")
col5.metric("Bookmarks", stats["bookmarks"])

st.markdown("---")

topic_acc = get_topic_accuracy()

col_charts, col_recent = st.columns([2, 1])

with col_charts:
    st.subheader("Topic Accuracy")
    if not topic_acc.empty:
        fig = px.bar(
            topic_acc, x="topic", y="accuracy", color="section",
            title="Accuracy by Topic (%)",
            labels={"accuracy": "Accuracy (%)", "topic": "Topic"},
            hover_data=["correct_attempts", "total_attempts"]
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Strong & Weak
        st.subheader("Strengths & Weaknesses")
        # Filter out topics with very few attempts to avoid noise
        reliable_topics = topic_acc[topic_acc['total_attempts'] >= 5]
        if not reliable_topics.empty:
            strongest = reliable_topics.sort_values(by="accuracy", ascending=False).head(3)
            weakest = reliable_topics.sort_values(by="accuracy", ascending=True).head(3)
            
            s1, s2 = st.columns(2)
            with s1:
                st.write("**Strongest Topics**")
                for _, row in strongest.iterrows():
                    st.success(f"{row['topic']} ({row['accuracy']:.1f}%)")
            with s2:
                st.write("**Weakest Topics**")
                for _, row in weakest.iterrows():
                    st.error(f"{row['topic']} ({row['accuracy']:.1f}%)")
        else:
            st.info("Attempt more questions (at least 5 per topic) to see strengths and weaknesses.")
    else:
        st.info("No attempts recorded yet. Start practicing!")

with col_recent:
    st.subheader("Recent Activity")
    recent = get_recent_activity(limit=10)
    if not recent.empty:
        for _, row in recent.iterrows():
            icon = "✅" if row['is_correct'] else "❌"
            date_str = row['attempt_timestamp'][:16].replace("T", " ")
            st.markdown(f"{icon} **{row['section']}** - {row['topic']}  \n*{date_str}*")
    else:
        st.write("No recent activity.")
