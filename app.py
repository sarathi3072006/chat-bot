import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai

# --- Configuration ---
API_KEY = "your_api_key_here"
MODEL_NAME = "gemini-2.5-flash"
# ---------------------

app = Flask(__name__)
CORS(app)

# Load SRNM data
try:
    with open("srnm_data.txt", "r", encoding="utf-8") as f:
        SRNM_DATA = f.read()
except FileNotFoundError:
    SRNM_DATA = "SRNM data file not found! Add srnm_data.txt."


# Restriction prompt
SYSTEM_PROMPT = f"""
You are an AI chatbot dedicated ONLY to SRNM College, Sattur.

RULES:
1. You must answer only questions related to SRNM College.
2. If the question is not related to SRNM, reply:
   "Sorry, I can answer only questions about SRNM College, Sattur."
3. Use ONLY the information provided in the database below.
4. If the answer is not in the database, reply:
   "I don’t have this information in my database."

SRNM COLLEGE DATABASE:
{SRNM_DATA}

Now answer the user's question accurately.
"""


# Initialize Gemini Client
try:
    client = genai.Client(api_key=API_KEY)
    print(f"--- SRNM Chatbot Backend Initialized with model: {MODEL_NAME} ---")
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    exit()


@app.route('/')
def serve_index():
    """Serve the frontend HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Handles user messages and returns SRNM-restricted AI response."""
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Build SRNM-restricted prompt
    final_prompt = SYSTEM_PROMPT + "\nUser: " + user_message + "\nAI:"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=final_prompt
        )

        ai_reply = response.text
        return jsonify({"response": ai_reply})

    except Exception as e:
        print("API error:", e)
        return jsonify({"error": "AI service failed"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

