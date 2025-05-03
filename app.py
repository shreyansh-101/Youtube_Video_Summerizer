import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import datetime
import pyperclip
import requests
from streamlit_lottie import st_lottie

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found. Please set up your API key in the .env file.")
else:
    genai.configure(api_key=api_key)

# Function to load Lottie animations
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Initialize session state
if "summary_history" not in st.session_state:
    st.session_state.summary_history = []
if "current_summary" not in st.session_state:
    st.session_state.current_summary = ""
if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

# Title with animation
st.set_page_config(page_title="YouTube Summarizer", layout="wide")
st.markdown("<h1 style='text-align: center;'>🎥 YouTube Video Summarizer</h1>", unsafe_allow_html=True)
lottie_video = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_j1adxtyb.json")
st_lottie(lottie_video, height=200, key="video")

# Sidebar - History
def delete_history():
    st.session_state.summary_history.clear()

st.sidebar.header("🕘 Summary History")
for entry in st.session_state.summary_history:
    st.sidebar.write(entry)
st.sidebar.button("🗑️ Clear History", on_click=delete_history)

# User input for YouTube URL
youtube_link = st.text_input("🔗 Enter full YouTube Video URL:")

# Options
col1, col2 = st.columns(2)
with col1:
    summary_length = st.radio("📏 Summary Length", ["100 words", "400 words", "600 words"])
with col2:
    summary_language = st.radio("🈹 Summary Language", ["English", "Hindi", "Marathi"])

# Display thumbnail if URL is provided
def extract_video_id(link):
    if "v=" in link:
        return link.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in link:
        return link.split("youtu.be/")[-1].split("?")[0]
    return ""

video_id = extract_video_id(youtube_link)
if video_id:
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

# List models
def list_available_models():
    try:
        models = genai.list_models()
        st.sidebar.write("### 🔹 Available Models:")
        for model in models:
            st.sidebar.write(f"- {model.name}")
    except Exception as e:
        st.sidebar.error(f"❌ Error fetching models: {str(e)}")

st.sidebar.button("🔍 Check Available Models", on_click=list_available_models)

# Extract transcript
def extract_transcript(video_id):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        return " ".join([item["text"] for item in transcript_data])
    except NoTranscriptFound:
        return "No transcript found."
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except Exception as e:
        return f"Error: {str(e)}"

# Generate summary
def generate_summary(transcript, length, language):
    word_limit = int(length.split(" ")[0])
    prompt = f"You are a YouTube video summarizer. Summarize the transcript in key points within {word_limit} words in {language} language:\n\n"

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt + transcript)
        return response.text
    except Exception as e:
        return f"❌ Error generating summary: {str(e)}"

# Generate Summary Button
if st.button("📝 Get Summary"):
    if not video_id:
        st.error("Please enter a valid YouTube URL.")
    else:
        transcript = extract_transcript(video_id)
        if "No transcript found" in transcript or "Transcripts are disabled" in transcript:
            st.error(transcript)
        else:
            summary = generate_summary(transcript, summary_length, summary_language)
            if summary.startswith("❌ Error"):
                st.error(summary)
            else:
                st.session_state.current_summary = summary
                st.session_state.show_summary = True

                # Add to history
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.summary_history.append(f"{timestamp} - {youtube_link}")

# Display Summary
if st.session_state.show_summary:
    st.markdown("## 📄 Summary:")
    st.write(st.session_state.current_summary)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download Summary",
            st.session_state.current_summary,
            file_name="summary.txt",
            key="download"
        )

    with col2:
        if st.button("📋 Copy Summary", key="copy"):
            try:
                pyperclip.copy(st.session_state.current_summary)
                st.success("✅ Summary copied to clipboard!")
            except Exception as e:
                st.error(f"❌ Failed to copy to clipboard: {str(e)}")
