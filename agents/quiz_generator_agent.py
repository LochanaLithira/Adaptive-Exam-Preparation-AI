from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/track_performance", methods=["POST"])
def track_performance():
    data = request.get_json()

    if not data or "results" not in data:
        return jsonify({"error": "No quiz results received"}), 400

    results = data["results"]

    # Example: Evaluate correctness
    performance = []
    score = 0
    for q in results:
        is_correct = q["user_answer"] == q["correct_answer"]
        if is_correct:
            score += 1
        performance.append({
            "id": q["id"],
            "question": q["question"],
            "category": q["category"],
            "correct_answer": q["correct_answer"],
            "user_answer": q["user_answer"],
            "is_correct": is_correct
        })

    return jsonify({
        "total_questions": len(results),
        "score": score,
        "details": performance
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
