import streamlit as st
import requests
import os
from dotenv import load_dotenv
from ocr import extract_text_from_image
from pdf_reader import extract_text_from_pdf

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Campus Copilot", layout="centered")

# Custom Styling
st.markdown("""
    <style>
        .main {
            padding-top: 1rem;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 900px;
        }

        h1, h2, h3 {
            letter-spacing: -0.5px;
        }

        .stTextArea textarea {
            border-radius: 14px;
            font-size: 16px;
        }

        .stButton button {
            border-radius: 12px;
            padding: 0.6rem 1.4rem;
            font-weight: 600;
            font-size: 16px;
        }

        .stFileUploader {
            border-radius: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.title("🎓 Campus Copilot")
st.markdown("### Turn college notices into actions")
st.markdown(
    """
    <div style="font-size:18px; color:#B8C0CC; margin-bottom:20px;">
        Upload a poster, PDF notice, or paste text — get deadlines, urgency, action steps, and a ready-to-send message instantly.
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# User Profile
st.markdown("## 👤 Student Profile")
department = st.selectbox(
    "Select your Department",
    ["CSE", "AIML", "ECE", "EEE", "ISE", "Mechanical", "Civil", "Other"]
)

year = st.selectbox(
    "Select your Year",
    ["1st Year", "2nd Year", "3rd Year", "4th Year"]
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload Poster / Notice Image or PDF",
    type=["png", "jpg", "jpeg", "pdf"]
)

manual_text = st.text_area("Or paste notice text here")


def analyze_text(text, department, year):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    prompt = f"""
You are Campus Copilot, an AI assistant for students.

The user is from:
Department: {department}
Year: {year}

Analyze the following college notice/poster text and return STRICTLY in this format:

Summary:
Event:
Deadline:
Priority:
Urgency:
Relevance:
Category:
Reason:
Why this matters for YOU:
Actions:
- 
- 
- 
WhatsApp Message:

Text:
{text}
"""

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "candidates" not in data:
        return f"Error: {data}"

    return data["candidates"][0]["content"]["parts"][0]["text"]


if st.button("Analyze Notice"):
    extracted_text = ""

    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".pdf"):
            with open("temp_notice.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())

            extracted_text = extract_text_from_pdf("temp_notice.pdf")
            st.text_area("Extracted Text from PDF", extracted_text, height=200)

        else:
            with open("temp_poster.png", "wb") as f:
                f.write(uploaded_file.getbuffer())

            extracted_text = extract_text_from_image("temp_poster.png")
            st.text_area("Extracted Text from Image", extracted_text, height=200)

    elif manual_text.strip():
        extracted_text = manual_text

    else:
        st.warning("Please upload an image / PDF or paste notice text.")
        st.stop()

    with st.spinner("Analyzing with AI..."):
        result = analyze_text(extracted_text, department, year)

    st.success("Analysis Complete")
    st.divider()

    # Parse output into sections
    lines = result.split("\n")

    summary = ""
    event = ""
    deadline = ""
    priority = ""
    urgency = ""
    relevance = ""
    category = ""
    reason = ""
    personal_reason = ""
    actions = []
    whatsapp = ""

    mode = ""

    for line in lines:
        line = line.strip()

        if line.lower().startswith("summary"):
            summary = line
        elif line.lower().startswith("event"):
            event = line
        elif line.lower().startswith("deadline"):
            deadline = line
        elif line.lower().startswith("priority"):
            priority = line
        elif line.lower().startswith("urgency"):
            urgency = line
        elif line.lower().startswith("relevance"):
            relevance = line
        elif line.lower().startswith("category"):
            category = line
        elif line.lower().startswith("reason"):
            reason = line
        elif line.lower().startswith("why this matters for you"):
            personal_reason = line
        elif line.lower().startswith("actions"):
            mode = "actions"
        elif line.lower().startswith("whatsapp"):
            mode = "whatsapp"
        else:
            if mode == "actions" and line.startswith("-"):
                actions.append(line)
            elif mode == "whatsapp":
                whatsapp += line + " "

    # Display nicely
    st.markdown("## ⚡ Quick Summary")
    st.success(summary)

    st.markdown("## 📌 Event Details")
    st.markdown(f"**{event}**")
    st.markdown(f"**{deadline}**")

    st.markdown("## 🧠 Smart Insights")
    st.info(urgency)
    st.info(relevance)
    st.info(category)

    if "high" in priority.lower():
        st.error(priority)
    elif "medium" in priority.lower():
        st.warning(priority)
    else:
        st.success(priority)

    st.markdown("### 🤔 Why it matters")
    st.write(reason)

    st.markdown("### 🎯 Why this matters for YOU")
    st.write(personal_reason)

    st.markdown("### ✅ Action Steps")
    for i, act in enumerate(actions, start=1):
        st.markdown(f"**{i}.** {act[1:].strip()}")

    st.markdown("### 💬 WhatsApp Message")
    st.code(whatsapp.strip())

    st.caption("Tip: You can copy this WhatsApp message and send it directly.")