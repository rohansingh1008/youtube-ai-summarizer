import re
import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi

# Page Configuration
st.set_page_config(page_title="AI Video Insights", page_icon="⚡", layout="wide")

st.title("⚡ AI Video Insights Generator")
st.write("Convert any YouTube video into structured study notes using YouTube Captions & Llama 3.3 LLM via Groq.")

# Retrieve Groq key from secrets or sidebar
groq_key = st.secrets.get("GROQ_API_KEY", "")

with st.sidebar:
    st.header("🔑 Configuration")
    if groq_key:
        st.success("✅ Groq API Key loaded automatically!")
    else:
        groq_key = st.text_input("Enter Groq API Key:", type="password")
        st.markdown("[Get a free Groq API Key](https://console.groq.com)")

video_url = st.text_input("Enter YouTube Video URL:")

def extract_video_id(url: str) -> str:
    """Extracts the YouTube Video ID from standard, short, or embedded URLs."""
    pattern = r"(?:v=|\/|be\/|embed\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(url: str) -> str:
    """Fetches video transcript using official/auto-generated YouTube subtitles."""
    video_id = extract_video_id(url)
    if not video_id:
        return "Pipeline Error: Invalid YouTube URL format."
        
    try:
        # Fetch transcript (supports English or auto-generated captions)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
        full_text = " ".join([item['text'] for item in transcript_list])
        return full_text
    except Exception as e:
        return f"Pipeline Error: Could not retrieve transcript. Make sure captions/subtitles are available on this video. ({str(e)})"

def summarize_text(text: str, api_key: str) -> str:
    """Summarizes transcribed text using Groq Llama 3.3-70B model."""
    try:
        client = Groq(api_key=api_key)
        
        prompt = (
            "You are an expert technical note-taker. Provide detailed, structured study notes "
            "with an Executive Summary, Key Concepts/Takeaways, and a Detailed Breakdown "
            f"for the following transcript:\n\n{text}"
        )
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1500
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"LLM Error: {str(e)}"

# Execution Trigger
if st.button("Generate Summary"):
    if not groq_key:
        st.error("Please configure your Groq API Key!")
    elif not video_url:
        st.warning("Please enter a YouTube video URL.")
    else:
        with st.spinner("Fetching transcript from YouTube..."):
            transcript = get_transcript(video_url)
            
        if transcript.startswith("Pipeline Error"):
            st.error(transcript)
        else:
            with st.spinner("Generating AI study notes with Llama 3.3..."):
                summary = summarize_text(transcript, groq_key)
                st.subheader("📝 Generated Insights")
                st.markdown(summary)