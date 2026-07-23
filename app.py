import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from huggingface_hub import InferenceClient

# Page setup
st.set_page_config(
    page_title="AI Video Insights & Notes Generator",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ AI Video Insights Generator")
st.caption("Transform long video lectures into structured, actionable study summaries using Hugging Face LLMs.")

# Sidebar - Configuration
st.sidebar.header("Settings")
hf_token = st.sidebar.text_input("Hugging Face API Token", type="password")
st.sidebar.markdown("Need a key? [Get API Token](https://huggingface.co/settings/tokens)")

# Core Functions
def extract_video_id(url: str) -> str:
    """Extracts 11-character video ID from common YouTube URL formats."""
    pattern = r"(?:v=|\/|be\/|embed\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id: str) -> str:
    """Fetches and concatenates subtitle text for a given YouTube video ID."""
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        return " ".join([item.text for item in fetched])
    except TranscriptsDisabled:
        return "Error: Subtitles/transcripts are disabled for this video."
    except NoTranscriptFound:
        return "Error: No English transcript found for this video."
    except Exception as e:
        return f"Error extracting transcript: {str(e)}"

def generate_study_notes(transcript_text: str, token: str) -> str:
    """Processes transcript text through Hugging Face Inference API to generate structured notes."""
    client = InferenceClient(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        token=token
    )
    
    trimmed_transcript = transcript_text[:12000]
    
    messages = [
        {
            "role": "system", 
            "content": "You are an expert AI documentation tutor. Generate precise, high-quality Markdown technical notes from the provided text."
        },
        {
            "role": "user", 
            "content": f"""
Analyze the following lecture transcript and synthesize structured, concise study notes.

Use the following output structure:
1. 📌 **Executive Overview**: High-level summary of the core topic.
2. 🔑 **Core Takeaways**: Key concepts and primary findings.
3. 📝 **Technical Breakdown**: In-depth conceptual analysis.
4. ❓ **Retention Assessment**: 3 self-check questions based on the content.

Transcript:
{trimmed_transcript}
"""
        }
    ]
    
    response = client.chat.completions.create(
        messages=messages,
        max_tokens=1500,
        temperature=0.4
    )
    
    return response.choices[0].message.content

# Main UI
youtube_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Generate Insights", type="primary", use_container_width=True):
    if not hf_token:
        st.error("Please provide a valid Hugging Face API token in the sidebar.")
    elif not youtube_url:
        st.warning("Please provide a YouTube video URL.")
    else:
        video_id = extract_video_id(youtube_url)
        
        if not video_id:
            st.error("Invalid YouTube URL format. Please check the link.")
        else:
            with st.spinner("Extracting transcript data..."):
                transcript = get_transcript(video_id)
            
            if transcript.startswith("Error"):
                st.error(transcript)
            else:
                with st.spinner("Generating structured notes via LLM..."):
                    try:
                        notes = generate_study_notes(transcript, hf_token)
                        
                        st.success("Summary generated!")
                        st.divider()
                        st.markdown(notes)
                        
                        st.download_button(
                            label="📥 Export Notes (.md)",
                            data=notes,
                            file_name=f"notes_{video_id}.md",
                            mime="text/markdown"
                        )
                        
                    except Exception as e:
                        st.error(f"Generation failed: {str(e)}")