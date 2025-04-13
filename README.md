# 🌲 Forest Haven - Mental Health Chatbot

**Forest Haven** is a real-time, web-based mental wellness chatbot that offers emotional support through natural conversations. Built with NLP, emotion detection, and Hugging Face Transformers, it understands your feelings and responds in a comforting, therapist-like way — just like a peaceful forest for your thoughts. 🌿

---

## 🧠 About the Project

- A real-time chatbot that detects emotional context in user inputs  
- Tailored replies to help users navigate stress, anxiety, and mood swings  
- Designed to support mental well-being in a non-judgmental, private environment  
- Great for students, professionals, or anyone needing a safe digital space to talk
- Offers helpful video links and supportive suggestions based on emotional needs
- Responds with empathy while also sharing insightful mental health facts — for example, India accounts for nearly 15% of global mental health conditions like depression and anxiety
- Combines AI understanding with kindness to create a virtual space that listens and comforts

---

## Dataset

 - Refer the intents.json file.

---

## 🔧 Tech Stack

### 💻 Backend
- **Python 3**
- **Flask** – Web framework for serving chatbot and handling API routes
- **Flask-Session** – User session management

### 🤖 Machine Learning
- **PyTorch** – Neural network model training and inference
- **NLTK** – Tokenization and stemming
- **TextBlob** – Sentiment analysis

### 🗃️ Database
- **MongoDB** – Stores conversation history, mood entries, and sentiment analysis

### 🌐 Frontend
- **HTML (Jinja2 template)** – Simple UI with `base.html`

### 📦 Other Tools
- **TorchScript** – Saves trained model (`data.pth`)
- **JSON** – Used for defining intents and patterns (`intents.json`)
---

## 🚀 Workflow
The complete lifecycle of the Forest Therapy chatbot consists of the following stages:

### 🏗️ 1. Data Preparation
- Define conversation intents in `intents.json`
- Each intent contains:
  - `tag`: intent label
  - `patterns`: sample user messages
  - `responses`: possible bot replies

### 🧠 2. Model Training (`train.py`)
- Tokenize and stem all patterns using NLTK
- Convert text to bag-of-words vectors
- Train a neural network using PyTorch
- Save model as `data.pth` for later inference

### 🧪 3. Chatbot Inference (`chat.py`)
- Load the trained model and `intents.json`
- For each user message:
  - Tokenize and convert to bag-of-words
  - Predict intent and choose a random response
  - If confidence < 0.75, return fallback message

### 🌐 4. Web Integration (`app.py`)
- Set up Flask server with session-based user ID
- Routes:
  - `/predict`: Accepts user message and returns bot response
  - `/mood`: Accepts user mood (1–10) and stores it
  - `/analysis`: Returns mood and sentiment trends
- Stores all data in MongoDB (`conversations`, `mood_scores`, `analysis`)

### 📊 5. Mood & Sentiment Analysis
- Every 5th query, calculate:
  - Average mood from user submissions
  - Sentiment score using TextBlob polarity
- Store the computed metrics in MongoDB

### 🧾 6. Frontend (HTML Template)
- Renders basic UI for chatting with the bot
- Displays real-time responses and mood input option

![Forest Haven Chatbot Preview](https://github.com/us107/Mental-health-chatbot--Forest-Haven/blob/main/image.png?raw=true)

---

## 🎥 Demo

Watch the chatbot in action!  
[▶️ Click to view demo video](https://github.com/us107/Mental-health-chatbot--Forest-Haven/blob/main/demo%20-%20Made%20with%20Clipchamp.mp4?raw=true)

---

## 🛠️ How to Run This Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/forest-haven.git
   cd forest-haven
2. Create a virtual env
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install dependencies
    ```bash
     pip install -r requirements.txt

4. Run train.py and then chat.py
    ```bash
    python train.py
    python chat.py 

6. Run the Flask app
   ```bash
      python app.py

## Contributing 
   Contributions are welcome! Feel free to open issues or pull requests. Let's grow Forest Haven together and support more minds! 💚

   

