import pandas as pd
from utils.database import get_connection

def generate_mock(mock_type):
    """
    Generate a mock test question set based on mock type.
    Returns a list of dicts (the questions).
    """
    if mock_type == "Mini Mock":
        config = {"QA": 10, "VARC": 10, "DILR": 5}
    elif mock_type == "Full Mock":
        config = {"QA": 22, "VARC": 24, "DILR": 20}
    else:
        raise ValueError(f"Unknown mock type: {mock_type}")
        
    conn = get_connection()
    questions = []
    
    for section, count in config.items():
        # Using ORDER BY RANDOM() since we only need a few questions
        # and limit is small.
        query = f"""
            SELECT * FROM questions 
            WHERE section = ? 
            ORDER BY RANDOM() 
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(section, count))
        questions.extend(df.to_dict('records'))
        
    conn.close()
    return questions

def save_mock_result(mock_type, attempts):
    from utils.scoring import calculate_score
    from datetime import datetime
    
    # Calculate overall
    overall = calculate_score(attempts)
    
    # Sectional scores
    qa_attempts = [a for a in attempts if a.get('section') == 'QA']
    varc_attempts = [a for a in attempts if a.get('section') == 'VARC']
    dilr_attempts = [a for a in attempts if a.get('section') == 'DILR']
    
    qa_score = calculate_score(qa_attempts)['score']
    varc_score = calculate_score(varc_attempts)['score']
    dilr_score = calculate_score(dilr_attempts)['score']
    
    total_time = sum([a.get('time_taken', 0) for a in attempts])
    
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO mock_history (mock_type, score, qa_score, varc_score, dilr_score, time_taken, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (mock_type, overall['score'], qa_score, varc_score, dilr_score, total_time, datetime.now().isoformat()))
    
    # Also log individual attempts so they show in analytics and revision queue
    for a in attempts:
        if 'selected_answer' in a and a['selected_answer'] is not None:
            # We use an inline import to avoid circular dependency
            from utils.database import record_attempt
            record_attempt(
                question_id=a['question_id'],
                selected_answer=a['selected_answer'],
                correct_answer=a['correct_answer'],
                time_taken=a.get('time_taken', 0)
            )
            
    conn.commit()
    conn.close()
