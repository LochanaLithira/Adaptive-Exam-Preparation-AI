# logic/performance_loader.py
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERFORMANCE_FILE = os.path.join(BASE_DIR, "data", "performance.json")

def load_performance():
    """Load performance records from JSON file."""
    with open(PERFORMANCE_FILE, "r") as f:
        records = json.load(f)
    return records

def summarize_by_topic(records):
    """
    Summarize performance by topic.
    Returns dict {topic: average accuracy}.
    """
    topic_stats = {}
    for r in records:
        topic = r["topic"]
        acc = r["result"]["accuracy"]
        if topic not in topic_stats:
            topic_stats[topic] = []
        topic_stats[topic].append(acc)

    summary = {t: sum(vals)/len(vals) for t, vals in topic_stats.items()}
    return summary
