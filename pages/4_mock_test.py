import streamlit as st
import time
from utils.mock_generator import generate_mock, save_mock_result
from utils.calculator import render_calculator

st.set_page_config(page_title="Mock Test | CAT Practice", layout="wide")

if 'mock_active' not in st.session_state:
    st.session_state.mock_active = False
if 'mock_q_idx' not in st.session_state:
    st.session_state.mock_q_idx = 0
if 'mock_questions' not in st.session_state:
    st.session_state.mock_questions = []
if 'mock_answers' not in st.session_state:
    st.session_state.mock_answers = {}
if 'mock_end_time' not in st.session_state:
    st.session_state.mock_end_time = 0
if 'mock_type' not in st.session_state:
    st.session_state.mock_type = ""
if 'mock_submitted' not in st.session_state:
    st.session_state.mock_submitted = False

def start_mock(m_type):
    st.session_state.mock_questions = generate_mock(m_type)
    st.session_state.mock_q_idx = 0
    st.session_state.mock_answers = {}
    st.session_state.mock_type = m_type
    st.session_state.mock_active = True
    st.session_state.mock_submitted = False
    
    # Time limits: Mini 40 mins, Full 120 mins
    limit = 40 if m_type == "Mini Mock" else 120
    st.session_state.mock_end_time = time.time() + (limit * 60)

def submit_mock():
    st.session_state.mock_active = False
    st.session_state.mock_submitted = True
    
    qs = st.session_state.mock_questions
    ans = st.session_state.mock_answers
    
    attempts = []
    for i, q in enumerate(qs):
        s_ans = ans.get(i)
        is_corr = None
        if s_ans:
            is_corr = 1 if str(s_ans).strip().upper() == str(q['correct_answer']).strip().upper() else 0
        attempts.append({
            'question_id': q['id'],
            'section': q['section'],
            'selected_answer': s_ans,
            'correct_answer': q['correct_answer'],
            'is_correct': is_corr,
            'time_taken': 0 # Basic estimation or 0
        })
        
    save_mock_result(st.session_state.mock_type, attempts)
    st.session_state.mock_attempts = attempts # Cache for review

st.title("🏆 CAT Mock Tests")

if not st.session_state.mock_active and not st.session_state.mock_submitted:
    st.write("Simulate the real CAT experience with carefully balanced question sets.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Mini Mock")
        st.write("25 Questions | 40 Minutes")
        st.write("- QA: 10 Questions")
        st.write("- VARC: 10 Questions")
        st.write("- DILR: 5 Questions")
        if st.button("Start Mini Mock", type="primary"):
            start_mock("Mini Mock")
            st.rerun()
            
    with col2:
        st.markdown("### Full Mock")
        st.write("66 Questions | 120 Minutes")
        st.write("- VARC: 24 Questions")
        st.write("- DILR: 20 Questions")
        st.write("- QA: 22 Questions")
        if st.button("Start Full Mock", type="primary"):
            start_mock("Full Mock")
            st.rerun()

elif st.session_state.mock_active:
    time_left = int(st.session_state.mock_end_time - time.time())
    
    if time_left <= 0:
        st.warning("Time's up! Submitting mock automatically...")
        submit_mock()
        st.rerun()
        
    mins, secs = divmod(time_left, 60)
    
    st.error(f"⏳ Time Remaining: {mins:02d}:{secs:02d}")
    st.markdown("---")
    
    # Section navigation sidebar
    qs = st.session_state.mock_questions
    idx = st.session_state.mock_q_idx
    
    st.sidebar.markdown("### Mock Navigation")
    sections = []
    for i, q in enumerate(qs):
        if q['section'] not in sections:
            sections.append(q['section'])
            
    selected_nav_section = st.sidebar.radio("Jump to Section:", sections, index=sections.index(qs[idx]['section']))
    
    # If user changed section via sidebar, jump to first question of that section
    if qs[idx]['section'] != selected_nav_section:
        for i, q in enumerate(qs):
            if q['section'] == selected_nav_section:
                st.session_state.mock_q_idx = i
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧮 Calculator")
    with st.sidebar:
        render_calculator()
        
    # Question view
    q = qs[idx]
    
    st.markdown(f"**Section: {q['section']}** | Question {idx + 1} of {len(qs)}")
    st.markdown("---")
    
    # Handle DILR/RC Passages
    if q['section'] in ['DILR', 'VARC'] and q['topic'] in ['RC', 'Caselets', 'Tables', 'Bar Graphs', 'Pie Charts', 'Linear Arrangement', 'Circular Arrangement', 'Selection', 'Scheduling', 'Grouping']:
        st.info("Passage/Data Set Context: Read carefully to answer related questions.")
        # If the DB has 'passage' or similar field, we'd render it. 
        # For our DB, the context is often integrated into the question or linked via source.
        # We will render the question text directly which contains the data.
        
    st.markdown(f"### {q['question'].replace('\\n', '\n')}")
    
    opts = [("A", q.get('option_a')), ("B", q.get('option_b')), ("C", q.get('option_c')), ("D", q.get('option_d'))]
    valid_opts = [opt for opt in opts if opt[1]]
    
    current_ans = st.session_state.mock_answers.get(idx, None)
    
    if q['question_type'] == 'MCQ' and valid_opts:
        ans_idx = [o[0] for o in valid_opts].index(current_ans) if current_ans in [o[0] for o in valid_opts] else None
        selected = st.radio(
            "Select your answer:",
            options=[opt[0] for opt in valid_opts],
            format_func=lambda x: f"{x}) {[opt[1] for opt in valid_opts if opt[0] == x][0]}",
            index=ans_idx,
            key=f"mq_{idx}"
        )
    else:
        selected = st.text_input("Type your answer (TITA):", value=current_ans if current_ans else "", key=f"mq_{idx}")
        
    st.session_state.mock_answers[idx] = selected
    
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if idx > 0:
            if st.button("⬅️ Previous"):
                st.session_state.mock_q_idx -= 1
                st.rerun()
    with c2:
        if idx < len(qs) - 1:
            if st.button("Next ➡️"):
                st.session_state.mock_q_idx += 1
                st.rerun()
        else:
            if st.button("✅ Submit Mock", type="primary"):
                submit_mock()
                st.rerun()

elif st.session_state.mock_submitted:
    st.success(f"{st.session_state.mock_type} Completed!")
    
    from utils.scoring import calculate_score
    attempts = st.session_state.mock_attempts
    qs = st.session_state.mock_questions
    ans = st.session_state.mock_answers
    
    overall = calculate_score(attempts)
    qa = calculate_score([a for a in attempts if a['section'] == 'QA'])
    varc = calculate_score([a for a in attempts if a['section'] == 'VARC'])
    dilr = calculate_score([a for a in attempts if a['section'] == 'DILR'])
    
    st.markdown("### Score Card")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Score", overall['score'])
    c2.metric("QA Score", qa['score'])
    c3.metric("VARC Score", varc['score'])
    c4.metric("DILR Score", dilr['score'])
    
    st.markdown("### Question Review")
    for i, a in enumerate(attempts):
        q = qs[i]
        icon = "✅" if a['is_correct'] == 1 else ("⚪" if a['is_correct'] is None else "❌")
        with st.expander(f"{icon} Q{i+1} [{q['section']}]"):
            st.write(q['question'].replace('\\n', '\n'))
            st.write(f"**Your Answer:** {a['selected_answer'] or 'Skipped'}")
            st.write(f"**Correct Answer:** {a['correct_answer']}")
            st.write(f"**Explanation:** {q['explanation']}")
            
    if st.button("Return to Mock Menu"):
        st.session_state.mock_submitted = False
        st.session_state.mock_active = False
        st.rerun()
