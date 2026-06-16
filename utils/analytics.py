import pandas as pd
from utils.database import get_connection

def get_basic_stats():
    conn = get_connection()
    
    # Total questions
    total_q = pd.read_sql_query("SELECT COUNT(*) as c FROM questions", conn)['c'][0]
    
    # Total attempts
    attempts_df = pd.read_sql_query("SELECT * FROM attempts", conn)
    
    if len(attempts_df) == 0:
        conn.close()
        return {
            "total_questions": total_q,
            "attempted": 0,
            "correct": 0,
            "accuracy": 0,
            "bookmarks": 0
        }
        
    attempted = len(attempts_df)
    correct = len(attempts_df[attempts_df['is_correct'] == 1])
    accuracy = (correct / attempted) * 100 if attempted > 0 else 0
    
    # Total bookmarks
    bookmarks = pd.read_sql_query("SELECT COUNT(*) as c FROM bookmarks", conn)['c'][0]
    
    conn.close()
    
    return {
        "total_questions": total_q,
        "attempted": attempted,
        "correct": correct,
        "accuracy": accuracy,
        "bookmarks": bookmarks
    }

def get_topic_accuracy():
    conn = get_connection()
    query = """
        SELECT q.section, q.topic, a.is_correct 
        FROM attempts a
        JOIN questions q ON a.question_id = q.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) == 0:
        return pd.DataFrame()
        
    grouped = df.groupby(['section', 'topic']).agg(
        total_attempts=('is_correct', 'count'),
        correct_attempts=('is_correct', 'sum')
    ).reset_index()
    
    grouped['accuracy'] = (grouped['correct_attempts'] / grouped['total_attempts']) * 100
    return grouped

def get_recent_activity(limit=5):
    conn = get_connection()
    query = """
        SELECT a.attempt_timestamp, q.section, q.topic, a.is_correct
        FROM attempts a
        JOIN questions q ON a.question_id = q.id
        ORDER BY a.attempt_timestamp DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_attempts_over_time():
    conn = get_connection()
    query = "SELECT attempt_timestamp, is_correct FROM attempts"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) == 0:
        return pd.DataFrame()
        
    df['date'] = pd.to_datetime(df['attempt_timestamp']).dt.date
    grouped = df.groupby('date').agg(
        attempts=('is_correct', 'count'),
        correct=('is_correct', 'sum')
    ).reset_index()
    
    grouped['accuracy'] = (grouped['correct'] / grouped['attempts']) * 100
    return grouped
