import streamlit as st
from dotenv import load_dotenv

load_dotenv()  ##load all the nevironment variables
import os
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi,TranscriptsDisabled, NoTranscriptFound

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are Yotube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """


## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]

        # Specify language codes to search for
        language_codes = ['en', 'hi']  # English and Hindi

        # Attempt to retrieve the transcript
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=language_codes)

        transcript = " ".join([item["text"] for item in transcript_data])
        return transcript

    except NoTranscriptFound as e:
        return "No transcript found for the specified languages."
    except TranscriptsDisabled as e:
        return "Transcripts are disabled for this video."
    except Exception as e:
        return f"An error occurred: {str(e)}"


## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text


st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    print(video_id)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text.startswith("No transcript found") or transcript_text.startswith("Transcripts are disabled"):
        st.error(transcript_text)
    else:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)





