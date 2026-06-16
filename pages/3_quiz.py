import streamlit as st
import time
from utils.database import get_distinct_values, get_filtered_questions, record_attempt
from utils.calculator import render_calculator

st.set_page_config(page_title="Quiz Mode | CAT Practice", layout="wide")

# Initialize state
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False
if 'quiz_q_idx' not in st.session_state:
    st.session_state.quiz_q_idx = 0
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {} # q_idx -> answer
if 'quiz_end_time' not in st.session_state:
    st.session_state.quiz_end_time = 0
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False

def start_quiz(filters, time_limit_mins):
    df = get_filtered_questions(**filters)
    st.session_state.quiz_questions = df.to_dict('records')
    st.session_state.quiz_q_idx = 0
    st.session_state.quiz_answers = {}
    st.session_state.quiz_active = True
    st.session_state.quiz_submitted = False
    st.session_state.quiz_end_time = time.time() + (time_limit_mins * 60)

def submit_quiz():
    st.session_state.quiz_active = False
    st.session_state.quiz_submitted = True
    # Record all attempts
    qs = st.session_state.quiz_questions
    ans = st.session_state.quiz_answers
    
    # We assume equal time distribution for simplicity, or just 0
    for idx, q in enumerate(qs):
        selected = ans.get(idx, None)
        if selected:
            record_attempt(q['id'], selected, q['correct_answer'], 0)

# --- SIDEBAR FILTERS ---
if not st.session_state.quiz_active and not st.session_state.quiz_submitted:
    st.sidebar.header("Quiz Setup")
    
    selected_sec = st.sidebar.selectbox("Section", ["All"] + get_distinct_values("section"))
    selected_top = st.sidebar.selectbox("Topic", ["All"] + get_distinct_values("topic", {"section": selected_sec} if selected_sec != "All" else None))
    selected_diff = st.sidebar.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
    
    num_qs = st.sidebar.slider("Number of Questions", 5, 30, 10)
    time_limit = st.sidebar.slider("Time Limit (Minutes)", 5, 60, 15)
    
    if st.sidebar.button("Start Timed Quiz", use_container_width=True):
        filters = {
            "section": selected_sec,
            "topic": selected_top,
            "difficulty": selected_diff,
            "limit": num_qs
        }
        start_quiz(filters, time_limit)
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🧮 Calculator")
with st.sidebar:
    render_calculator()

# --- MAIN CONTENT ---
st.title("⏱️ Timed Quiz Mode")

if not st.session_state.quiz_active and not st.session_state.quiz_submitted:
    st.info("👈 Set up your quiz parameters in the sidebar and click 'Start Timed Quiz'.")

elif st.session_state.quiz_active:
    time_left = int(st.session_state.quiz_end_time - time.time())
    
    if time_left <= 0:
        st.warning("Time's up! Submitting quiz automatically...")
        submit_quiz()
        st.rerun()
        
    # Header & Timer
    mins, secs = divmod(time_left, 60)
    
    col_prog, col_time = st.columns([3, 1])
    with col_prog:
        total = len(st.session_state.quiz_questions)
        idx = st.session_state.quiz_q_idx
        st.progress((idx) / total)
        st.write(f"Question {idx + 1} of {total}")
    with col_time:
        st.error(f"⏳ Time Remaining: {mins:02d}:{secs:02d}")
        
    st.markdown("---")
    
    q = st.session_state.quiz_questions[idx]
    q_text = q['question'].replace('\\n', '\n')
    st.markdown(f"### {q_text}")
    
    opts = [("A", q.get('option_a')), ("B", q.get('option_b')), ("C", q.get('option_c')), ("D", q.get('option_d'))]
    valid_opts = [opt for opt in opts if opt[1]]
    
    current_ans = st.session_state.quiz_answers.get(idx, None)
    
    if q['question_type'] == 'MCQ' and valid_opts:
        ans_idx = [o[0] for o in valid_opts].index(current_ans) if current_ans in [o[0] for o in valid_opts] else None
        selected = st.radio(
            "Select your answer:",
            options=[opt[0] for opt in valid_opts],
            format_func=lambda x: f"{x}) {[opt[1] for opt in valid_opts if opt[0] == x][0]}",
            index=ans_idx,
            key=f"q_{idx}"
        )
    else:
        selected = st.text_input("Type your answer (TITA):", value=current_ans if current_ans else "", key=f"q_{idx}")
        
    st.session_state.quiz_answers[idx] = selected
    
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if idx > 0:
            if st.button("⬅️ Previous"):
                st.session_state.quiz_q_idx -= 1
                st.rerun()
    with c2:
        if idx < total - 1:
            if st.button("Next ➡️"):
                st.session_state.quiz_q_idx += 1
                st.rerun()
        else:
            if st.button("✅ Finish & Submit", type="primary"):
                submit_quiz()
                st.rerun()

elif st.session_state.quiz_submitted:
    st.success("Quiz Completed!")
    
    from utils.scoring import calculate_score
    qs = st.session_state.quiz_questions
    ans = st.session_state.quiz_answers
    
    attempts_for_scoring = []
    for i, q in enumerate(qs):
        s_ans = ans.get(i)
        is_corr = None
        if s_ans:
            is_corr = 1 if str(s_ans).strip().upper() == str(q['correct_answer']).strip().upper() else 0
        attempts_for_scoring.append({'is_correct': is_corr})
        
    results = calculate_score(attempts_for_scoring)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", results['score'])
    c2.metric("Accuracy", f"{results['accuracy']:.1f}%")
    c3.metric("Correct", results['correct'])
    c4.metric("Incorrect / Skipped", f"{results['incorrect']} / {results['skipped']}")
    
    st.markdown("### Review Answers")
    for i, q in enumerate(qs):
        s_ans = ans.get(i, "Skipped")
        c_ans = q['correct_answer']
        icon = "✅" if str(s_ans).strip().upper() == str(c_ans).strip().upper() else ("⚪" if s_ans == "Skipped" else "❌")
        
        with st.expander(f"{icon} Q{i+1}: {q['topic']}"):
            st.write(q['question'].replace('\\n', '\n'))
            st.write(f"**Your Answer:** {s_ans}")
            st.write(f"**Correct Answer:** {c_ans}")
            st.write(f"**Explanation:** {q['explanation']}")
            
    if st.button("Start New Quiz"):
        st.session_state.quiz_submitted = False
        st.session_state.quiz_active = False
        st.rerun()
