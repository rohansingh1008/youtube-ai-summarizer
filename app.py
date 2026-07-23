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
    """Downloads m4a audio and transcribes instantly using Groq Whisper API."""
    audio_file = "temp_audio.m4a"
    
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        client = Groq(api_key=api_key)
        
        with open(audio_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file, file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
            
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        return str(transcription)

    except Exception as e:
        if os.path.exists(audio_file):
            os.remove(audio_file)
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