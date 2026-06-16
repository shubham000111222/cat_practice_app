import streamlit as st
import os
from utils.database import run_migrations, get_setting

# Set up page configuration
st.set_page_config(
    page_title="CAT Practice Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Run database migrations on startup
@st.cache_resource
def init_db():
    run_migrations()

init_db()

# Load user settings
if 'theme' not in st.session_state:
    st.session_state.theme = get_setting('theme', 'light')

st.title("🎓 Offline CAT Practice Platform")
st.markdown("---")

st.markdown("""
### Welcome to your personal CAT preparation hub!

Use the sidebar to navigate through the platform:

*   📊 **Dashboard**: View your high-level statistics and performance.
*   📝 **Practice**: Practice questions by section, topic, and difficulty at your own pace.
*   ⏱️ **Quiz**: Take timed quizzes on specific topics.
*   🏆 **Mock Test**: Simulate full or mini CAT-style tests.
*   🔖 **Bookmarks**: Review questions you've saved for later.
*   🔄 **Revision**: Spaced repetition and weak topic focused practice.
*   📈 **Analytics**: Deep dive into your accuracy and trends.
*   ⚙️ **Settings**: Export data and customize your experience.

Ready to start? Select a module from the left sidebar.
""")

# Simple keyboard shortcut injection (JavaScript)
# This will globally listen for keys and set a dummy element value or use Streamlit's 
# experimental get_query_params/set_query_params, but pure JS execution in ST is tricky.
# We will rely on standard Streamlit buttons for this app to ensure stability,
# but add some helper instructions.

st.info("💡 **Pro Tip**: In Practice mode, you can use the on-screen buttons to quickly navigate and bookmark questions.")
