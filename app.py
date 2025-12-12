import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai

# --- Configuration ---
API_KEY = "your_api"
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

1. if you cant answer a question using the below "srnm_data" use google/internet and search the same thing the user asked followed by :"sri s.ramasamy naidu memorial college sattur" (absolutely mandatory)
2.Label inferred lines when responding to users — e.g., “Likely” or “Typically” vs. “Confirmed”. This keeps the bot honest.
3. if the users use greeting: use the same greeting and say "how can i help you?"
4. if the user talks casually and not ask anything about the college talk back casually and end with:",i also do want to talk more with you but i am an ai assistant to answer questions about my college so please keep the chat related to the topic kindly"(use commas or full stop make the tex proffessional)
5. If the answer is not in the database, check the internet and reply the answer (mandatory)
6. if the user uses bad words or inappropriate words roast them make fun of them an even use bad words.
7. if the user use tangish (tamil pronounciated english word) reply them with tanglish
8. if the user use tamil talk back in tamil

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
