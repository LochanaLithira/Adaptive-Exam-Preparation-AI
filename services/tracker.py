from flask import Flask, request, jsonify
from collections import OrderedDict

app = Flask(__name__)

@app.route("/track_performance", methods=["POST"])
def track_performance():
    data = request.get_json()

    if not data or "results" not in data:
        return jsonify({"error": "No quiz results received"}), 400

    results = data["results"]
    # Sort by question ID to keep numbering consistent
    results_sorted = sorted(results, key=lambda x: x["id"])
    num_digits = len(str(len(results_sorted)))

    received_responses  = OrderedDict()
    for q in results_sorted:
        key = f"Q{str(q['id']).zfill(num_digits)} : {q.get('question')}"
        received_responses[key] = {
            "category": q.get("category"),
            "correct_answer": q.get("correct_answer"),
            "user_answer": q.get("user_answer"),
        }

    response_summary = {
        "message": "✅ Data received successfully",
        "received_quiz_count": len(results_sorted),
        "received_responses": received_responses
    }

    return jsonify(response_summary)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
