# agents/performance_tracker_agent.py

def track_performance(user_answers, correct_answers, topics):
    """
    Compare user answers with correct answers and return score + analysis.
    """
    score = 0
    total = len(correct_answers)
    mistakes = []

    for i, ans in enumerate(user_answers):
        if ans == correct_answers[i]:
            score += 1
        else:
            mistakes.append(topics[i])  # log weak topic
    
    accuracy = round((score / total) * 100, 2)
    
    return {
        "score": score,
        "total": total,
        "accuracy": accuracy,
        "mistakes": mistakes
    }


def get_feedback(performance_data):
    """
    Generate adaptive feedback for Planner.
    """
    if performance_data["accuracy"] >= 80:
        return "✅ Great job! Move to advanced topics."
    elif performance_data["accuracy"] >= 50:
        return "👍 Good work. Revise weak areas: " + ", ".join(performance_data["mistakes"])
    else:
        return "⚠️ Focus more on basics. Revise topics: " + ", ".join(performance_data["mistakes"])


if __name__ == "__main__":
    user_answers = ["A", "B", "C", "D", "A"]
    correct_answers = ["A", "C", "C", "D", "B"]
    topics = ["Math", "Physics", "Math", "Chemistry", "Biology"]

    performance = track_performance(user_answers, correct_answers, topics)
    feedback = get_feedback(performance)

    # Example usage - results can be used by other modules
