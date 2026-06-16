def calculate_score(attempts):
    """
    Calculate CAT score based on attempts.
    attempts: list of dicts with 'is_correct' (1, 0, or None if skipped)
    """
    correct = 0
    incorrect = 0
    skipped = 0
    
    for attempt in attempts:
        if attempt.get('is_correct') == 1:
            correct += 1
        elif attempt.get('is_correct') == 0:
            incorrect += 1
        else:
            skipped += 1
            
    score = (correct * 3) - incorrect
    accuracy = (correct / (correct + incorrect)) * 100 if (correct + incorrect) > 0 else 0
    
    return {
        "score": score,
        "correct": correct,
        "incorrect": incorrect,
        "skipped": skipped,
        "total_attempted": correct + incorrect,
        "accuracy": accuracy
    }
