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

 - https://www.kaggle.com/datasets/bhavikjikadara/mental-health-dataset

---

## 🔧 Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **NLP & ML**: Hugging Face Transformers (model="bhadresh-savani/distilbert-base-uncased-emotion"), Pytorch
- **Emotion Detection**: Pretrained transformer models
- **Environment**: Python 3.8+
- **Data Analysis**: PySpark  
- **Deployment**: GitHub Pages / Streamlit / Flask server  

---

## 🚀 Workflow

1. User inputs a message.  
2. Message processed using emotion detection model.  
3. Bot generates a response based on detected emotion.  
4. Frontend displays the calming and supportive reply.

![Forest Haven Chatbot Preview](https://github.com/us107/Mental-health-chatbot--Forest-Haven/blob/main/image.png?raw=true)

---

## 🎥 Demo

Watch the chatbot in action!  
[▶️ Click to view demo video](https://github.com/us107/Mental-health-chatbot--Forest-Haven/blob/main/demo%20-%20Made%20with%20Clipchamp.mp4?raw=true)

---

## 📊 Data Preprocessing with PySpark

Before the chatbot generates emotionally intelligent responses, a PySpark-based script is used to analyze the dataset and extract mental health insights based on:

- **Stress Levels** (`Growing_Stress = Yes`)  
- **Mood Swings** (`Mood_Swings = High or Medium`)  
- **Country-wise Statistics**

This script:
- Aggregates total entries per country
- Calculate percentages of users experiencing stress/mood swings
- Saves results to `mental_health_stats.csv` for chatbot usage

----

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

4. Run the spark script
    ```bash
    pip install pyspark
    python spark.py 

6. Run the app
   ```bash
      python chatbot.py

## Contributing 
   Contributions are welcome! Feel free to open issues or pull requests. Let's grow Forest Haven together and support more minds! 💚

   

