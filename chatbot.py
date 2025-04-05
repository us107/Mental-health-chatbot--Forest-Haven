from flask import Flask, render_template, request
from flask_socketio import SocketIO
import pandas as pd
from transformers import pipeline
import os
import re

app = Flask(__name__)
socketio = SocketIO(app)

# Load Spark stats
stats_df = pd.read_csv("mental_health_stats.csv")

# Initialize a more nuanced emotion detection model, forcing CPU usage
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", device=-1)  # -1 ensures CPU

# Country-specific helpline numbers (expandable)
helplines = {
    "United States": "1-800-273-8255 (National Suicide Prevention Lifeline)",
    "Canada": "1-833-456-4566 (Canada Suicide Prevention Service)",
    "United Kingdom": "116 123 (Samaritans)",
    "Australia": "13 11 14 (Lifeline Australia)",
    "Poland": "22 484 88 01 (Helpline Poland)",
    "India": "91-9820466726 (Vandrevala Foundation)",
}

# User session data
user_data = {}

# Check HF_TOKEN
hf_token = os.environ.get("HUGGINGFACE_TOKEN")
if hf_token:
    print("Hugging Face token found!")
else:
    print("No HF token found, using public model.")

# Check if input is gibberish
def is_gibberish(text):
    return bool(re.match(r'^[^a-zA-Z0-9\s]+$', text)) or len(text.split()) == 0 or all(len(word) < 3 and not word.isdigit() for word in text.split())

# Therapist-like responses based on detected emotion
def handle_emotion(message, user, emotion):
    if "anxiety" in message or "anxious" in message or emotion == "fear":
        return (f"{user['name'] or 'Friend'}, I’m so sorry you’re feeling anxious. Let’s try this together: breathe in for 4 seconds, hold for 4, exhale for 4. "
                "Here’s a calming video: <a href='https://www.youtube.com/watch?v=Dx112W4i5I0' target='_blank'>Relaxation Video</a>.")
    elif "frustrated" in message or "frustration" in message or emotion == "anger":
        return (f"{user['name'] or 'Friend'}, I can understand how frustrating that must feel. Let’s take a moment—try stepping away for a bit and doing something calming, like listening to music. "
                "Here’s a video that might help: <a href='https://www.youtube.com/watch?v=wLj3FSd79i4' target='_blank'>Dealing with Frustration</a>. "
                "Here's a music video that might help too: <a href='https://youtu.be/_BtXPQimVhg?si=K1TunupLIMEWNSf-' target='_blank'>Music</a>.")
    elif "sad" in message or "depressed" in message or emotion == "sadness":
        if "kill" in message or "suicide" in message or "hopeless" in message:
            helpline = helplines.get(user["country"], "a local helpline")
            return (f"{user['name'] or 'Friend'}, I’m really worried about you—it sounds incredibly tough right now. You don’t have to go through this alone. "
                    f"Please reach out to someone who can help immediately. Here’s a helpline for {user['country']}: {helpline}. "
                    "For now, try focusing on something small—maybe step outside and feel the air. Can you tell me one thing you see?")
        else:
            return (f"{user['name'] or 'Friend'}, I’m here for you—it’s okay to feel sad. How about writing down three things you’re grateful for today? "
                    "Here’s a helpful video: <a href='https://www.youtube.com/watch?v=x42THvq0gqM' target='_blank'>Coping with Sadness</a>.")
    elif emotion == "joy":
        return f"{user['name'] or 'Friend'}, I’m so glad you’re feeling good! What’s making your day brighter?"
    else:
        # Fallback for unrecognized emotions
        return f"Hey {user['name'] or 'Friend'}, I can sense you’re feeling something strongly. Can you tell me more about what’s going on?"

# Response logic
def get_response(message, sid):
    message = message.lower().strip()
    user = user_data.get(sid, {"name": None, "age": None, "country": None, "stage": "greeting"})

    # Detect emotion using the new model
    emotion_result = emotion_classifier(message)[0]
    emotion = emotion_result["label"]  # e.g., "anger", "sadness", "joy"
    confidence = emotion_result["score"]

    # Check for emotional content even in greeting stage
    if user["stage"] == "greeting":
        if "frustrated" in message or "anxiety" in message or "anxious" in message or "sad" in message or "depressed" in message or emotion in ["anger", "fear", "sadness", "joy"]:
            user["stage"] = "asking_info"
            user_data[sid] = user
            return f"{handle_emotion(message, user, emotion)} By the way, I’d love to get to know you better. What’s your name? And where are you from?"
        elif message in ["hi", "hello", "hey"]:
            user["stage"] = "asking_info"
            user_data[sid] = user
            return "Hey there! I’m glad you’re here to chat. What’s your name? And where are you from?"
        else:
            user["stage"] = "asking_info"
            user_data[sid] = user
            return "I’m here for you! What’s your name? And where are you from?"

    # Collecting user info
    elif user["stage"] == "asking_info":
        words = message.split()
        if len(words) >= 2:
            user["name"] = words[0].capitalize()
            potential_country = " ".join(words[1:]).title()
            if potential_country in stats_df["Country"].values or potential_country in helplines:
                user["country"] = potential_country
                user["stage"] = "asking_age"
                user_data[sid] = user
                return f"Nice to meet you, {user['name']}! How old are you?"
            else:
                user["stage"] = "asking_country"
                user_data[sid] = user
                return f"Hi {user['name']}! I didn’t catch your country—where are you from?"
        else:
            return "I’d love to get to know you! What’s your name and where are you from?"

    # Collecting country
    elif user["stage"] == "asking_country":
        potential_country = message.title()
        if potential_country in stats_df["Country"].values or potential_country in helplines:
            user["country"] = potential_country
            user["stage"] = "asking_age"
            user_data[sid] = user
            return f"Great, {user['name']}! How old are you?"
        return "Hmm, I’m not sure about that country. Could you tell me again where you’re from?"

    # Collecting age
    elif user["stage"] == "asking_age":
        try:
            age = int(re.search(r'\d+', message).group())
            user["age"] = age
            user["stage"] = "conversation"
            user_data[sid] = user
            return f"Thanks, {user['name']}! It’s nice to chat with someone {age} from {user['country']}. How are you feeling today?"
        except (AttributeError, ValueError):
            return f"Hey {user['name']}, I didn’t catch your age. How old are you?"

    # Conversation phase
    elif user["stage"] == "conversation":
        # Handle gibberish
        if is_gibberish(message):
            return f"{user['name']}, I’m not quite sure what you mean! Could you tell me more about how you’re feeling?"

        # Data-related questions
        if "depression" in message or "stress" in message or "common" in message:
            country = user["country"] or next((c for c in stats_df["Country"] if c.lower() in message), None)
            if country:
                country_stats = stats_df[stats_df["Country"] == country].iloc[0]
                stress_percent = country_stats["stress_percent"]
                mood_percent = country_stats["mood_percent"]
                if "depression" in message:
                    if mood_percent > 50:
                        return f"{user['name']}, yes, depression-related issues like mood swings are common in {country}, with {mood_percent}% reporting medium to high mood swings."
                    elif mood_percent > 20:
                        return f"{user['name']}, depression is somewhat common in {country}, with {mood_percent}% reporting medium to high mood swings."
                    else:
                        return f"{user['name']}, depression isn’t very common in {country}, with only {mood_percent}% reporting medium to high mood swings."
                elif "stress" in message:
                    if stress_percent > 50:
                        return f"{user['name']}, yes, stress is common in {country}, with {stress_percent}% reporting growing stress."
                    elif stress_percent > 20:
                        return f"{user['name']}, stress is somewhat common in {country}, with {stress_percent}% reporting growing stress."
                    else:
                        return f"{user['name']}, stress isn’t very common in {country}, with only {stress_percent}% reporting growing stress."
            return f"{user['name']}, I can tell you about stress or depression trends if you mention a country!"

        # Therapist-like responses based on detected emotion
        return handle_emotion(message, user, emotion)

    return f"{user['name'] or 'Friend'}, I’m here for you. How can I help you today?"

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    sid = request.sid
    msg = data.get("message", "")
    response = get_response(msg, sid)
    socketio.emit('response', {"text": response}, room=sid)

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    user_data[sid] = {"name": None, "age": None, "country": None, "stage": "greeting"}
    print(f"User {sid} connected")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    user_data.pop(sid, None)
    print(f"User {sid} disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)