import random
from logic_planner.resources import resources

def calculate_weights(records):
    """
    Calculates weights based on the accuracy of each topic.
    Lower accuracy -> higher weight (needs more focus)
    """
    weights = []
    for record in records:
        topic = record.get("topic")
        accuracy = record.get("result", {}).get("accuracy", 0)  # get accuracy safely
        weight = max(100 - accuracy, 0)  # higher weight for lower accuracy
        weights.append({"topic": topic, "weight": weight})
    return weights


def generate_plan(records):
    """
    Generates a 7-day study plan.
    Pattern: Weak → Medium → Good → Weak → Medium → Good → ...
    """
    weights = calculate_weights(records)
    
    # Sort topics by weight descending
    sorted_topics = sorted(weights, key=lambda x: x["weight"], reverse=True)
    
    # Divide into categories
    weak = [t["topic"] for t in sorted_topics if t["weight"] > 50]
    medium = [t["topic"] for t in sorted_topics if 25 < t["weight"] <= 50]
    good = [t["topic"] for t in sorted_topics if t["weight"] <= 25]

    # Helper to pick next topic from a list (cycle if needed)
    def pick_next(category_list, index):
        if not category_list:
            return None
        return category_list[index % len(category_list)]

    plan = []
    for i in range(7):
        pattern = i % 3  # 0=weak, 1=medium, 2=good
        if pattern == 0:
            topic_for_day = pick_next(weak, i//3)
        elif pattern == 1:
            topic_for_day = pick_next(medium, i//3)
        else:
            topic_for_day = pick_next(good, i//3)

        # If category is empty, fallback to weak → medium → good
        if not topic_for_day:
            for fallback in [weak, medium, good]:
                topic_for_day = pick_next(fallback, i//3)
                if topic_for_day:
                    break

        plan.append({"Day": i + 1, "Topic": topic_for_day})

    return plan
