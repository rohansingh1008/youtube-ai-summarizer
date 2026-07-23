import os
import yt_dlp
import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="AI Video Insights", page_icon="⚡", layout="wide")

st.title("⚡ AI Video Insights Generator")
st.write("Convert any YouTube video into structured study notes using OpenAI Whisper ASR & Llama 3.3 LLM via Groq.")

# Retrieve key from secrets if available, otherwise ask in sidebar
groq_key = st.secrets.get("GROQ_API_KEY", "")

with st.sidebar:
    st.header("🔑 Configuration")
    if groq_key:
        st.success("✅ Groq API Key loaded automatically!")
    else:
        groq_key = st.text_input("Enter Groq API Key:", type="password")
        st.markdown("[Get a free Groq API Key](https://console.groq.com)")

video_url = st.text_input("Enter YouTube Video URL:")

def extract_audio_and_transcribe(url: str, api_key: str) -> str:
    """Downloads audio stream flexibly and transcribes using Groq Whisper API."""
    cookie_file = "youtube_cookies.txt"
    output_template = "temp_audio.%(ext)s"
    
    # Write cookies from secrets to a temporary file if present
    cookies_content = st.secrets.get("YOUTUBE_COOKIES", "")
    if cookies_content:
        with open(cookie_file, "w", encoding="utf-8") as f:
            f.write(cookies_content)

    ydl_opts = {
        'format': 'ba/b',  # Fallback to best available audio stream
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookie_file if os.path.exists(cookie_file) else None,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
        }
    }
    
    downloaded_file = None
    
    try:
        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)

        client = Groq(api_key=api_key)
        
        # Transcribe using Groq Whisper
        with open(downloaded_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(downloaded_file, file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
            
        # Clean up downloaded files
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
            
        return str(transcription)

    except Exception as e:
        # Clean up on error
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
        return f"Pipeline Error: {str(e)}"

def summarize_text(text: str, api_key: str) -> str:
    """Summarizes transcribed text using Groq Llama 3.3-70B model."""
    try:
        client = Groq(api_key=api_key)
        
        prompt = (
            "You are an expert technical note-taker. Provide structured study notes "
            "with an Executive Summary, Key Takeaways, and a Technical Breakdown "
            f"for the following transcript:\n\n{text}"
        )
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000
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
        with st.spinner("Extracting audio & transcribing with Groq Whisper..."):
            transcript = extract_audio_and_transcribe(video_url, groq_key)
            
        if transcript.startswith("Pipeline Error"):
            st.error(transcript)
        else:
            with st.spinner("Generating AI study notes with Llama 3.3..."):
                summary = summarize_text(transcript, groq_key)
                st.subheader("📝 Generated Insights")
                st.markdown(summary)