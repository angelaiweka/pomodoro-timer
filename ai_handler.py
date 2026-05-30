from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def get_break_suggestion(topic):
    try:
        prompt = f"I just finished a 25-minute study session on '{topic}'. Give me a short, fun, and creative break activity suggestion in 2-3 sentences. Keep it light and encouraging!"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Take a short walk and stretch! (Error: {e})"

def get_weekly_summary(sessions):
    try:
        if not sessions:
            return "No study sessions found yet!"
        session_text = "\n".join([
            f"- {s['date']}: {s['topic']} ({s['duration']} min, {s['type']})"
            for s in sessions
        ])
        prompt = f"Here are my recent study sessions:\n{session_text}\n\nGive me a brief, encouraging weekly summary with insights on my study patterns, most studied topics, and one actionable tip. Keep it under 150 words."
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Could not generate summary. (Error: {e})"