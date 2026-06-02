import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_break_suggestion(topic):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": f"I just finished a 25-minute study session on '{topic}'. Give me a short, fun, and creative break activity suggestion in 2-3 sentences. Keep it light and encouraging!"
            }]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Take a short walk and stretch! (Error: {e})"

def get_weekly_summary(sessions):
    try:
        if not sessions:
            return "No study sessions found yet!"
        session_text = "\n".join([
            f"- {s['date']}: {s['topic']} ({s['duration']} min, {s['type']})"
            + (f" | notes: {s['notes']}" if s.get('notes') and s['notes'] != 'how did it go?' else "")
            + (f" | completed: {', '.join(s['completed_tasks'])}" if s.get('completed_tasks') else "")
            + (f" | incomplete: {', '.join(s['incomplete_tasks'])}" if s.get('incomplete_tasks') else "")
            for s in sessions
        ])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": f"Here are my recent study sessions:\n{session_text}\n\nGive me a brief, encouraging weekly summary with insights on my study patterns, most studied topics, task completion rate, and one actionable tip. Keep it under 150 words."
            }]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate summary. (Error: {e})"