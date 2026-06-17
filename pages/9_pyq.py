import streamlit as st
import time
import sqlite3
import pandas as pd
from utils.database import get_connection, get_distinct_values, record_attempt, toggle_bookmark
from utils.calculator import render_calculator

st.set_page_config(page_title="PYQ | CAT Practice", layout="wide")

# Initialize session state variables
if 'pyq_q_idx' not in st.session_state:
    st.session_state.pyq_q_idx = 0
if 'pyq_questions' not in st.session_state:
    st.session_state.pyq_questions = []
if 'pyq_show_explanation' not in st.session_state:
    st.session_state.pyq_show_explanation = False
if 'pyq_selected_answer' not in st.session_state:
    st.session_state.pyq_selected_answer = None
if 'pyq_start_time' not in st.session_state:
    st.session_state.pyq_start_time = time.time()

def load_pyq_questions(filters):
    conn = get_connection()
    query = "SELECT * FROM questions WHERE 1=1"
    params = []
    
    if filters.get("source") and filters["source"] != "All":
        query += " AND source = ?"
        params.append(filters["source"])
    else:
        # If "All" is selected, still only show PYQs (where source starts with CAT or PYQ)
        query += " AND (source LIKE 'CAT %' OR source = 'PYQ')"
        
    if filters.get("section") and filters["section"] != "All":
        query += " AND section = ?"
        params.append(filters["section"])
        
    if filters.get("topic") and filters["topic"] != "All":
        query += " AND topic = ?"
        params.append(filters["topic"])

    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(filters.get("limit", 10))
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    st.session_state.pyq_questions = df.to_dict('records')
    st.session_state.pyq_q_idx = 0
    reset_q_state()

def reset_q_state():
    st.session_state.pyq_show_explanation = False
    st.session_state.pyq_selected_answer = None
    st.session_state.pyq_start_time = time.time()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter PYQs")

# Only fetch sources that look like PYQs
conn = get_connection()
sources_df = pd.read_sql_query("SELECT DISTINCT source FROM questions WHERE source LIKE 'CAT %' OR source = 'PYQ' ORDER BY source DESC", conn)
conn.close()
sources = ["All"] + sources_df['source'].tolist()

selected_source = st.sidebar.selectbox("Year / Source", sources)

sections = ["All"] + get_distinct_values("section")
selected_sec = st.sidebar.selectbox("Section", sections)

topics = ["All"] + get_distinct_values("topic", {"section": selected_sec} if selected_sec != "All" else None)
selected_top = st.sidebar.selectbox("Topic", topics)

num_qs = st.sidebar.slider("Number of Questions", 5, 50, 10)

if st.sidebar.button("Start PYQ Practice", use_container_width=True):
    filters = {
        "source": selected_source,
        "section": selected_sec,
        "topic": selected_top,
        "limit": num_qs
    }
    load_pyq_questions(filters)

st.sidebar.markdown("---")
st.sidebar.subheader("🧮 Calculator")
with st.sidebar:
    render_calculator()

# --- MAIN CONTENT ---
st.title("📚 Previous Year Questions (PYQ)")
st.write("Practice questions exclusively from past CAT exams.")

questions = st.session_state.pyq_questions

if not questions:
    st.info("👈 Select your PYQ filters from the sidebar and click 'Start PYQ Practice'.")
else:
    idx = st.session_state.pyq_q_idx
    total = len(questions)
    
    if idx >= total:
        st.success(f"You have completed all {total} questions in this PYQ set!")
        if st.button("Start New Set"):
            st.session_state.pyq_questions = []
            st.rerun()
    else:
        q = questions[idx]
        
        # Header
        source_display = q.get('tags', q.get('source', 'PYQ'))
        st.markdown(f"**Question {idx + 1} of {total}** | {q['section']} > {q['topic']} | 📌 **{source_display}**")
        st.markdown("---")
        
        # Question Text
        q_text = q['question'].replace('\\n', '\n')
        st.markdown(f"### {q_text}")
        st.write("")
        
        # Options or TITA
        opts = [
            ("A", q.get('option_a')),
            ("B", q.get('option_b')),
            ("C", q.get('option_c')),
            ("D", q.get('option_d'))
        ]
        valid_opts = [opt for opt in opts if opt[1]]
        
        if q['question_type'] == 'MCQ' and valid_opts:
            st.session_state.pyq_selected_answer = st.radio(
                "Select your answer:",
                options=[opt[0] for opt in valid_opts],
                format_func=lambda x: f"{x}) {[opt[1] for opt in valid_opts if opt[0] == x][0]}",
                index=None if not st.session_state.pyq_show_explanation else ([opt[0] for opt in valid_opts].index(st.session_state.pyq_selected_answer) if st.session_state.pyq_selected_answer in [opt[0] for opt in valid_opts] else None)
            )
        else:
            st.session_state.pyq_selected_answer = st.text_input("Type your answer (TITA):")

        st.write("")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if not st.session_state.pyq_show_explanation:
                if st.button("Submit Answer", type="primary"):
                    if st.session_state.pyq_selected_answer:
                        st.session_state.pyq_show_explanation = True
                        time_taken = int(time.time() - st.session_state.pyq_start_time)
                        record_attempt(q['id'], st.session_state.pyq_selected_answer, q['correct_answer'], time_taken)
                        st.rerun()
                    else:
                        st.warning("Please select or type an answer.")
        
        with col_btn2:
            if st.button("🔖 Bookmark"):
                is_b = toggle_bookmark(q['id'])
                if is_b:
                    st.toast("Question bookmarked!")
                else:
                    st.toast("Bookmark removed!")
                    
        with col_btn3:
            if st.session_state.pyq_show_explanation:
                if st.button("Next Question ⏭️", use_container_width=True):
                    st.session_state.pyq_q_idx += 1
                    reset_q_state()
                    st.rerun()

        # Explanation logic
        if st.session_state.pyq_show_explanation:
            st.markdown("---")
            is_correct = str(st.session_state.pyq_selected_answer).strip().upper() == str(q['correct_answer']).strip().upper()
            
            if is_correct:
                st.success(f"✅ Correct! The answer is {q['correct_answer']}")
            else:
                st.error(f"❌ Incorrect. You answered {st.session_state.pyq_selected_answer}, but the correct answer is {q['correct_answer']}")
                
            with st.expander("Show Explanation", expanded=True):
                st.write(q['explanation'])
