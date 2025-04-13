from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import pymongo
from datetime import datetime
from textblob import TextBlob

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# MongoDB connection with explicit database creation
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    # Test connection
    client.admin.command('ping')
    db = client["chatbot"]
    # Ensure collections exist
    db.conversations.create_index([("user_id", 1), ("timestamp", -1)])
    db.mood_scores.create_index([("user_id", 1), ("timestamp", -1)])
    db.analysis.create_index([("user_id", 1), ("timestamp", -1)])
    print("Connected to MongoDB and initialized chatbot database.")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    raise

conversations = db["conversations"]
mood_scores = db["mood_scores"]
analysis = db["analysis"]

@app.before_request
def initialize_session():
    # Set a default user_id if not present (runs before every request)
    if "user_id" not in session:
        session["user_id"] = str(datetime.now().timestamp())

@app.route("/")
def home():
    return render_template("base.html")

@app.post("/predict")
def predict():
    message = request.json.get("message")
    if not message:
        return jsonify({"answer": "Please provide a message.", "query_count": 0})

    # Get response from chat.py
    from chat import get_response
    response = get_response(message)
    query_count = conversations.count_documents({"user_id": session["user_id"]}) + 1

    # Store conversation
    conversation = {
        "user_id": session["user_id"],
        "message": message,
        "response": response,
        "query_count": query_count,
        "timestamp": datetime.now()
    }
    try:
        result = conversations.insert_one(conversation)
        print(f"Conversation stored with ID: {result.inserted_id}, Data: {conversation}")  # Debug
    except Exception as e:
        print(f"Error storing conversation: {e}")
        return jsonify({"answer": response, "query_count": query_count}), 500

    # Compute and store analysis every 5 queries
    if query_count % 5 == 0:
        print(f"Computing analysis for query_count {query_count}")
        # Fetch mood data
        mood_data = list(mood_scores.find({"user_id": session["user_id"]}))
        print(f"Found mood data: {mood_data}")  # Debug
        if mood_data:
            avg_mood = sum(d["mood"] for d in mood_data) / len(mood_data)
        else:
            avg_mood = 0

        # Basic sentiment analysis from recent conversations
        recent_convos = list(conversations.find({"user_id": session["user_id"]}).sort("timestamp", -1).limit(5))
        sentiment_score = 0
        if recent_convos:
            total_sentiment = sum(TextBlob(conv["message"]).sentiment.polarity for conv in recent_convos if conv["message"])
            sentiment_score = (total_sentiment / len(recent_convos) + 1) * 2.5  # Scale -1 to 1 to 0 to 10
            sentiment_score = max(1, min(10, sentiment_score))  # Clamp to 1-10

        # Store analysis
        analysis_entry = {
            "user_id": session["user_id"],
            "avg_mood": round(avg_mood, 1),
            "sentiment_mood": round(sentiment_score, 1),
            "mood_entries": len(mood_data),
            "timestamp": datetime.now()
        }
        try:
            result = analysis.insert_one(analysis_entry)
            print(f"Analysis inserted with ID: {result.inserted_id}, Data: {analysis_entry}")  # Debug
        except Exception as e:
            print(f"Error storing analysis: {e}")
            return jsonify({"answer": response, "query_count": query_count}), 500

    return jsonify({"answer": response, "query_count": query_count})

@app.post("/mood")
def submit_mood():
    mood = request.json.get("mood")
    if not mood or not isinstance(mood, (int, float)) or mood < 1 or mood > 10:
        return jsonify({"error": "Mood must be a number between 1 and 10."}), 400

    mood_score = {
        "user_id": session["user_id"],
        "mood": float(mood),
        "timestamp": datetime.now()
    }
    try:
        result = mood_scores.insert_one(mood_score)
        print(f"Mood score inserted with ID: {result.inserted_id}, Data: {mood_score}")  # Debug
    except Exception as e:
        print(f"Error storing mood score: {e}")
        return jsonify({"message": "Error recording mood."}), 500
    return jsonify({"message": "Mood recorded successfully."})

@app.get("/analysis")
def get_analysis():
    try:
        results = db.analysis.find({"user_id": session["user_id"]}).sort("timestamp", -1).limit(5)
        analysis = [
            {
                "avg_mood": round(float(r.get("avg_mood", 0)), 1),
                "sentiment_mood": round(float(r.get("sentiment_mood", 0)), 1),
                "mood_entries": int(r.get("mood_entries", 0)),
                "timestamp": r.get("timestamp", datetime.now()).isoformat()
            }
            for r in results
        ]
        print(f"Analysis data fetched: {analysis}")  # Debug log
        if not analysis:
            print("No analysis data found for user.")
        return jsonify(analysis)
    except Exception as e:
        print(f"Error fetching analysis: {e}")
        return jsonify([]), 500

if __name__ == "__main__":
    app.run(debug=True)