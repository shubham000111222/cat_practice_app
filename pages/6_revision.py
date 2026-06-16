import streamlit as st
import time
from utils.database import get_revision_queue, record_attempt

st.set_page_config(page_title="Revision | CAT Practice", layout="wide")

st.title("🔄 Revision Mode")
st.write("Spaced repetition queue. Questions you answered incorrectly or struggled with will appear here for review.")

df = get_revision_queue(limit=10)

if df.empty:
    st.success("Your revision queue is empty! Great job. Go practice more questions to fill it up.")
else:
    if 'rev_idx' not in st.session_state:
        st.session_state.rev_idx = 0
    if 'rev_show_ans' not in st.session_state:
        st.session_state.rev_show_ans = False
    if 'rev_selected' not in st.session_state:
        st.session_state.rev_selected = None
        
    idx = st.session_state.rev_idx
    if idx >= len(df):
        st.success("You've completed your revision queue for now!")
        if st.button("Refresh Queue"):
            st.session_state.rev_idx = 0
            st.rerun()
    else:
        q = df.iloc[idx].to_dict()
        
        st.markdown(f"**Question {idx + 1} of {len(df)}** | Priority Score: {q['priority_score']:.2f} (Higher = Needs review)")
        st.markdown("---")
        
        st.markdown(f"### {q['question'].replace('\\n', '\n')}")
        
        opts = [("A", q.get('option_a')), ("B", q.get('option_b')), ("C", q.get('option_c')), ("D", q.get('option_d'))]
        valid_opts = [opt for opt in opts if opt[1]]
        
        if q['question_type'] == 'MCQ' and valid_opts:
            st.session_state.rev_selected = st.radio(
                "Select your answer:",
                options=[opt[0] for opt in valid_opts],
                format_func=lambda x: f"{x}) {[opt[1] for opt in valid_opts if opt[0] == x][0]}",
                index=None if not st.session_state.rev_show_ans else ([o[0] for o in valid_opts].index(st.session_state.rev_selected) if st.session_state.rev_selected in [o[0] for o in valid_opts] else None)
            )
        else:
            st.session_state.rev_selected = st.text_input("Type your answer:")
            
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.rev_show_ans:
                if st.button("Submit Answer", type="primary"):
                    if st.session_state.rev_selected:
                        # Record attempt updates the revision queue score automatically
                        record_attempt(q['id'], st.session_state.rev_selected, q['correct_answer'], 0)
                        st.session_state.rev_show_ans = True
                        st.rerun()
                    else:
                        st.warning("Please provide an answer.")
                        
        with col2:
            if st.session_state.rev_show_ans:
                if st.button("Next Question ➡️"):
                    st.session_state.rev_idx += 1
                    st.session_state.rev_show_ans = False
                    st.session_state.rev_selected = None
                    st.rerun()
                    
        if st.session_state.rev_show_ans:
            st.markdown("---")
            if str(st.session_state.rev_selected).strip().upper() == str(q['correct_answer']).strip().upper():
                st.success(f"✅ Correct! Priority score decreased.")
            else:
                st.error(f"❌ Incorrect. Priority score increased.")
                
            st.write(f"**Correct Answer:** {q['correct_answer']}")
            st.write(f"**Explanation:** {q['explanation']}")
