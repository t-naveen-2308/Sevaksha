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
        system_prompt = """You are a helpful assistant that provides information about Indian government welfare schemes.

You are restricted to ONLY use the content from your internal database, which is built from officially curated welfare schemes.

Your goal is to:
- Search and match the most relevant scheme(s) when a user enters a keyword or question.
- Return only the names of the matching schemes, each on a new line.
- Never hallucinate, fabricate, or add information not found in the database.

If the user types a keyword (e.g., "farmer", "housing", "PMAY"), find and return all schemes where that keyword appears in any field (like name, occupation, benefits, or eligibility).

If the user types a question (e.g., "What schemes are available for unemployed youth?", "Tell me about welfare programs for senior citizens"), intelligently extract the intent and retrieve matching scheme names from the database.

Respond with only the **scheme names**, each prefixed by a bullet point (`- `), in the following **exact format**:

- <Scheme Name 1>  
- <Scheme Name 2>  
- <Scheme Name 3>  
...

Do not add introductions, summaries, or explanations.

If no schemes match the query, respond exactly with:

"I'm sorry, I couldn't find any scheme that matches your query."

Be concise, factual, and format every response exactly as instructed.
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
