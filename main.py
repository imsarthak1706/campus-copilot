import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_text(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    prompt = f"""
You are Campus Copilot, an AI assistant for students.

Analyze the following college notice/poster text and return clearly:

1. Event name
2. Deadline
3. Priority (high / medium / low)
4. Why it matters for a student
5. What actions the student should take

Text:
{text}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    print("FULL RESPONSE:")
    print(data)

    if "candidates" not in data:
        return "Gemini API error. Check FULL RESPONSE above."

    return data["candidates"][0]["content"]["parts"][0]["text"]


sample_text = """
Hyperthon Hackathon
Register before April 5
Open for CSE students
Team size 2-4
Venue: AI Brewery
"""

print(analyze_text(sample_text))