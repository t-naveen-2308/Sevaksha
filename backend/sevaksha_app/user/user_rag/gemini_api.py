import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

_chat_session = None
_chat_history = []

def query_gemini(prompt):
    try:
        return _extracted_from_query_gemini_7(prompt)
    except Exception as e:
        _chat_session = None
        _chat_history = []
        return f"❌ API Error: {e}"

def _extracted_from_query_gemini_7(prompt):
    global _chat_session, _chat_history
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    safety_settings = {
        "HARASSMENT": "block_none",
        "HATE_SPEECH": "block_none",
        "SEXUALLY_EXPLICIT": "block_none",
        "DANGEROUS_CONTENT": "block_none",
    }

    if _chat_session is None:
        system_prompt = """You're a friendly and helpful chatbot that assists users in finding Indian government welfare schemes. You can chat naturally, answer questions, and guide users based on their needs. Your responses are always based only on your internal database of officially curated welfare schemes.

When a user gives a keyword or asks a question, you use that to identify relevant welfare schemes. Then, you suggest matching schemes by name, each on a new line with a bullet point.

Don't make up any schemes or details. If nothing matches, just say:
"I'm sorry, I couldn't find any scheme that matches your query."

You can also ask follow-up questions or chat casually, as long as you stay helpful and focused on guiding users to the right schemes.
"""

        _chat_session = model.start_chat(history=[])
        _chat_history = []
        _chat_session.send_message(system_prompt)

    _chat_history.append({"role": "user", "content": prompt})

    response = _chat_session.send_message(prompt)

    _chat_history.append({"role": "assistant", "content": response.text})

    return response.text

def reset_chat():
    global _chat_session, _chat_history
    _chat_session = None
    _chat_history = []
    return {"message": "Chat history cleared", "history": []}

def get_chat_history():
    global _chat_history
    return _chat_history
