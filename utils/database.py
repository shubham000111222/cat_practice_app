import sqlite3
import pandas as pd
import os
from datetime import datetime

# We expect this file to be run from the root of cat_practice_app
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'cat_question_bank.db')

def get_connection():
    # Provide a dictionary-like cursor
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def run_migrations():
    """Create new tables required for the application if they don't exist."""
    conn = get_connection()
    c = conn.cursor()
    
    # Enable WAL mode for better concurrency performance if not already
    c.execute("PRAGMA journal_mode=WAL")
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            selected_answer TEXT,
            correct_answer TEXT,
            is_correct INTEGER,
            time_taken INTEGER,
            attempt_timestamp TEXT,
            FOREIGN KEY(question_id) REFERENCES questions(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER UNIQUE,
            created_at TEXT,
            FOREIGN KEY(question_id) REFERENCES questions(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS revision_queue (
            question_id INTEGER PRIMARY KEY,
            priority_score REAL DEFAULT 1.0,
            next_review_date TEXT,
            last_review_date TEXT,
            FOREIGN KEY(question_id) REFERENCES questions(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS mock_history (
            mock_id INTEGER PRIMARY KEY AUTOINCREMENT,
            mock_type TEXT,
            score REAL,
            qa_score REAL,
            varc_score REAL,
            dilr_score REAL,
            time_taken INTEGER,
            timestamp TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_filtered_questions(section=None, topic=None, subtopic=None, difficulty=None, source=None, limit=10, offset=0):
    conn = get_connection()
    query = "SELECT * FROM questions WHERE 1=1"
    params = []
    
    if section and section != "All":
        query += " AND section = ?"
        params.append(section)
    if topic and topic != "All":
        query += " AND topic = ?"
        params.append(topic)
    if subtopic and subtopic != "All":
        query += " AND subtopic = ?"
        params.append(subtopic)
    if difficulty and difficulty != "All":
        query += " AND difficulty = ?"
        params.append(difficulty)
    if source and source != "All":
        query += " AND source = ?"
        params.append(source)
        
    # We want random questions for practice, but SQLite RANDOM() is slow on large tables.
    # Since we have pagination, we order by random but within a subquery if needed. 
    # For simplicity, we just order by RANDOM(). The DB is small enough (4.4k rows).
    query += f" ORDER BY RANDOM() LIMIT {limit} OFFSET {offset}"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_question_by_id(qid):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM questions WHERE id = ?", conn, params=(qid,))
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else None

def record_attempt(question_id, selected_answer, correct_answer, time_taken):
    conn = get_connection()
    c = conn.cursor()
    
    is_correct = 1 if selected_answer == correct_answer else 0
    now = datetime.now().isoformat()
    
    c.execute('''
        INSERT INTO attempts (question_id, selected_answer, correct_answer, is_correct, time_taken, attempt_timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (question_id, selected_answer, correct_answer, is_correct, time_taken, now))
    
    # Update revision queue logic
    c.execute("SELECT priority_score FROM revision_queue WHERE question_id=?", (question_id,))
    row = c.fetchone()
    
    if row:
        new_score = max(0.1, row[0] - 0.5) if is_correct else min(5.0, row[0] + 1.0)
        c.execute('''
            UPDATE revision_queue 
            SET priority_score=?, last_review_date=? 
            WHERE question_id=?
        ''', (new_score, now, question_id))
    else:
        # If wrong, add to revision queue immediately
        if not is_correct:
            c.execute('''
                INSERT INTO revision_queue (question_id, priority_score, last_review_date)
                VALUES (?, ?, ?)
            ''', (question_id, 2.0, now))
            
    conn.commit()
    conn.close()

def toggle_bookmark(question_id):
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT bookmark_id FROM bookmarks WHERE question_id = ?", (question_id,))
    row = c.fetchone()
    
    is_bookmarked = False
    if row:
        c.execute("DELETE FROM bookmarks WHERE question_id = ?", (question_id,))
    else:
        c.execute("INSERT INTO bookmarks (question_id, created_at) VALUES (?, ?)", 
                  (question_id, datetime.now().isoformat()))
        is_bookmarked = True
        
    conn.commit()
    conn.close()
    return is_bookmarked

def get_bookmarked_questions():
    conn = get_connection()
    query = """
        SELECT q.*, b.created_at as bookmarked_at 
        FROM questions q
        JOIN bookmarks b ON q.id = b.question_id
        ORDER BY b.created_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_revision_queue(limit=20):
    conn = get_connection()
    query = """
        SELECT q.*, r.priority_score
        FROM questions q
        JOIN revision_queue r ON q.id = r.question_id
        ORDER BY r.priority_score DESC, r.last_review_date ASC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_setting(key, default=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT setting_value FROM user_settings WHERE setting_key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_settings (setting_key, setting_value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_distinct_values(column, filters=None):
    conn = get_connection()
    
    where_clause = ""
    params = []
    if filters:
        clauses = []
        for k, v in filters.items():
            if v and v != "All":
                clauses.append(f"{k} = ?")
                params.append(v)
        if clauses:
            where_clause = "WHERE " + " AND ".join(clauses)
            
    query = f"SELECT DISTINCT {column} FROM questions {where_clause} ORDER BY {column}"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df[column].dropna().tolist()
