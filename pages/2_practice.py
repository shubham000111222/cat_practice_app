import streamlit as st
import time
from utils.database import get_distinct_values, get_filtered_questions, record_attempt, toggle_bookmark

st.set_page_config(page_title="Practice | CAT Practice", layout="wide")

# Initialize session state variables
if 'practice_q_idx' not in st.session_state:
    st.session_state.practice_q_idx = 0
if 'practice_questions' not in st.session_state:
    st.session_state.practice_questions = []
if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = False
if 'selected_answer' not in st.session_state:
    st.session_state.selected_answer = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

def load_questions(filters):
    df = get_filtered_questions(**filters)
    st.session_state.practice_questions = df.to_dict('records')
    st.session_state.practice_q_idx = 0
    reset_q_state()

def reset_q_state():
    st.session_state.show_explanation = False
    st.session_state.selected_answer = None
    st.session_state.start_time = time.time()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Questions")

sections = ["All"] + get_distinct_values("section")
selected_sec = st.sidebar.selectbox("Section", sections)

topics = ["All"] + get_distinct_values("topic", {"section": selected_sec} if selected_sec != "All" else None)
selected_top = st.sidebar.selectbox("Topic", topics)

subtopics = ["All"] + get_distinct_values("subtopic", {"topic": selected_top} if selected_top != "All" else None)
selected_sub = st.sidebar.selectbox("Subtopic", subtopics)

diffs = ["All", "Easy", "Medium", "Hard"]
selected_diff = st.sidebar.selectbox("Difficulty", diffs)

num_qs = st.sidebar.slider("Number of Questions", 5, 50, 10)

if st.sidebar.button("Start Practice", use_container_width=True):
    filters = {
        "section": selected_sec,
        "topic": selected_top,
        "subtopic": selected_sub,
        "difficulty": selected_diff,
        "limit": num_qs
    }
    load_questions(filters)

# --- MAIN CONTENT ---
st.title("📝 Practice Mode")

questions = st.session_state.practice_questions

if not questions:
    st.info("👈 Use the sidebar to select your filters and click 'Start Practice'.")
else:
    idx = st.session_state.practice_q_idx
    total = len(questions)
    
    if idx >= total:
        st.success(f"You have completed all {total} questions in this set!")
        if st.button("Start New Set"):
            st.session_state.practice_questions = []
            st.rerun()
    else:
        q = questions[idx]
        
        # Header
        st.markdown(f"**Question {idx + 1} of {total}** | {q['section']} > {q['topic']} | 🎯 {q['difficulty']}")
        st.markdown("---")
        
        # Question Text
        # Replace explicit literal \n with actual newlines to render properly
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
            # We use radio buttons
            st.session_state.selected_answer = st.radio(
                "Select your answer:",
                options=[opt[0] for opt in valid_opts],
                format_func=lambda x: f"{x}) {[opt[1] for opt in valid_opts if opt[0] == x][0]}",
                index=None if not st.session_state.show_explanation else ([opt[0] for opt in valid_opts].index(st.session_state.selected_answer) if st.session_state.selected_answer in [opt[0] for opt in valid_opts] else None)
            )
        else:
            # TITA
            st.session_state.selected_answer = st.text_input("Type your answer (TITA):")

        st.write("")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if not st.session_state.show_explanation:
                if st.button("Submit Answer", type="primary"):
                    if st.session_state.selected_answer:
                        st.session_state.show_explanation = True
                        time_taken = int(time.time() - st.session_state.start_time)
                        record_attempt(q['id'], st.session_state.selected_answer, q['correct_answer'], time_taken)
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
            if st.session_state.show_explanation:
                if st.button("Next Question ⏭️", use_container_width=True):
                    st.session_state.practice_q_idx += 1
                    reset_q_state()
                    st.rerun()

        # Explanation logic
        if st.session_state.show_explanation:
            st.markdown("---")
            is_correct = str(st.session_state.selected_answer).strip().upper() == str(q['correct_answer']).strip().upper()
            
            if is_correct:
                st.success(f"✅ Correct! The answer is {q['correct_answer']}")
            else:
                st.error(f"❌ Incorrect. You answered {st.session_state.selected_answer}, but the correct answer is {q['correct_answer']}")
                
            with st.expander("Show Explanation", expanded=True):
                st.write(q['explanation'])
