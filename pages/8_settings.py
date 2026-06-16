import streamlit as st
import pandas as pd
import io
from utils.database import get_connection, set_setting, get_setting
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.set_page_config(page_title="Settings | CAT Practice", layout="wide")

st.title("⚙️ Settings & Exports")

# Theme Selection
st.subheader("Preferences")
theme = get_setting('theme', 'light')
new_theme = st.radio("Theme Mode (Note: Streamlit's native theme engine mostly controls this, but we can store preference)", 
                     options=['light', 'dark'], 
                     index=0 if theme == 'light' else 1)
                     
if new_theme != theme:
    set_setting('theme', new_theme)
    st.session_state.theme = new_theme
    st.success("Theme preference saved!")

st.markdown("---")
st.subheader("Data Exports")
st.write("Download your performance data and bookmarks.")

conn = get_connection()

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Export Attempts (CSV)")
    attempts_df = pd.read_sql_query("SELECT * FROM attempts", conn)
    if not attempts_df.empty:
        csv_att = attempts_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Attempts CSV",
            data=csv_att,
            file_name="cat_attempts.csv",
            mime="text/csv"
        )
    else:
        st.info("No attempts to export.")

    st.markdown("#### Export Bookmarks (CSV)")
    bm_df = pd.read_sql_query("""
        SELECT q.section, q.topic, q.question, b.created_at
        FROM bookmarks b JOIN questions q ON b.question_id = q.id
    """, conn)
    
    if not bm_df.empty:
        csv_bm = bm_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Bookmarks CSV",
            data=csv_bm,
            file_name="cat_bookmarks.csv",
            mime="text/csv"
        )
    else:
        st.info("No bookmarks to export.")

with col2:
    st.markdown("#### Performance Report (PDF)")
    
    def generate_pdf():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, "CAT Practice Performance Report")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, 720, f"Total Attempts: {len(attempts_df)}")
        
        correct = len(attempts_df[attempts_df['is_correct'] == 1]) if not attempts_df.empty else 0
        acc = (correct / len(attempts_df)) * 100 if len(attempts_df) > 0 else 0
        
        p.drawString(50, 700, f"Overall Accuracy: {acc:.1f}%")
        p.drawString(50, 680, f"Total Bookmarks: {len(bm_df)}")
        
        p.drawString(50, 650, "Generated locally by CAT Practice Platform.")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer
        
    if not attempts_df.empty:
        pdf_bytes = generate_pdf()
        st.download_button(
            label="Download Performance Report PDF",
            data=pdf_bytes,
            file_name="cat_performance_report.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Attempt some questions to generate a PDF report.")

conn.close()
