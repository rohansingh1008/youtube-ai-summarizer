# ⚡ AI Video Insights Generator

An interactive web application built with Python and Streamlit that converts YouTube lecture videos into structured, actionable study notes using open-source Large Language Models (LLMs) via the Hugging Face Inference API.

## 🚀 Features

* **Instant Transcript Extraction**: Automatically pulls video subtitles and transcripts directly via YouTube's API.
* **LLM-Powered Summarization**: Generates high-quality Markdown study notes including:
  * Executive Overview
  * Core Takeaways
  * Technical Breakdown
  * Retention Check Questions
* **Export Functionality**: Download formatted summaries locally as Markdown (`.md`) files.
* **Custom API Integration**: Input your own free Hugging Face API token for secure execution.

## 🛠️ Tech Stack

* **Frontend / Web Framework**: [Streamlit](https://streamlit.io/)
* **AI / NLP Model**: [Hugging Face Serverless Inference API](https://huggingface.co/docs/api-inference/index) (Qwen 2.5)
* **Data Extraction**: `youtube-transcript-api`
* **Language**: Python 3.10+

## ⚙️ Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/rohan1008/youtube-ai-summarizer.git](https://github.com/rohan1008/youtube-ai-summarizer.git)
   cd youtube-ai-summarizer