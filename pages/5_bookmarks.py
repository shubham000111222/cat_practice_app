import streamlit as st
import pandas as pd
from utils.database import get_bookmarked_questions, toggle_bookmark

st.set_page_config(page_title="Bookmarks | CAT Practice", layout="wide")

st.title("🔖 Bookmarks")
st.write("Review and practice the questions you've saved.")

df = get_bookmarked_questions()

if df.empty:
    st.info("You haven't bookmarked any questions yet. Go to Practice mode to add some!")
else:
    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        sections = ["All"] + list(df['section'].unique())
        sec_filter = st.selectbox("Filter by Section", sections)
    with col2:
        if sec_filter != "All":
            topics = ["All"] + list(df[df['section'] == sec_filter]['topic'].unique())
        else:
            topics = ["All"] + list(df['topic'].unique())
        top_filter = st.selectbox("Filter by Topic", topics)
        
    filtered_df = df
    if sec_filter != "All":
        filtered_df = filtered_df[filtered_df['section'] == sec_filter]
    if top_filter != "All":
        filtered_df = filtered_df[filtered_df['topic'] == top_filter]
        
    st.write(f"Showing {len(filtered_df)} bookmarked questions.")
    
    # State for practice mode within bookmarks
    if 'bm_practice_idx' not in st.session_state:
        st.session_state.bm_practice_idx = None
        
    if st.button("Practice Bookmarked List"):
        st.session_state.bm_practice_idx = 0
        
    if st.session_state.bm_practice_idx is not None:
        idx = st.session_state.bm_practice_idx
        if idx >= len(filtered_df):
            st.success("Finished practicing bookmarked questions!")
            if st.button("Close Practice"):
                st.session_state.bm_practice_idx = None
                st.rerun()
        else:
            q = filtered_df.iloc[idx].to_dict()
            st.markdown("---")
            st.markdown(f"**Section:** {q['section']} | **Topic:** {q['topic']}")
            st.markdown(f"### {q['question'].replace('\\n', '\n')}")
            
            with st.expander("View Answer & Explanation"):
                st.write(f"**Correct Answer:** {q['correct_answer']}")
                st.write(f"**Explanation:** {q['explanation']}")
                
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Next Question"):
                    st.session_state.bm_practice_idx += 1
                    st.rerun()
            with col_b2:
                if st.button("Remove Bookmark"):
                    toggle_bookmark(q['id'])
                    # If we remove, we should just rerun
                    st.rerun()
            st.markdown("---")
            
    else:
        # Just list them
        for _, row in filtered_df.iterrows():
            with st.expander(f"{row['section']} - {row['topic']} (Saved: {row['bookmarked_at'][:10]})"):
                st.write(row['question'].replace('\\n', '\n'))
                if st.button("Remove Bookmark", key=f"rm_{row['id']}"):
                    toggle_bookmark(row['id'])
                    st.rerun()
