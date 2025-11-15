import streamlit as st
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("MEDICAL_DIAGNOSTIC_API_KEY"))

# Create Gemini model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "temperature": 1,
        "top_p": 0.5,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",   # FIXED
    },
)

# ---- System Prompt ----
system_prompt = """
(Your system prompt here — unchanged)
"""

# UI
st.set_page_config(page_title="Medical Diagnostic Analytics", page_icon="🩺")

st.title("🩺 Medical Diagnostic Image Analyzer")

upload_file = st.file_uploader(
    "Please upload a medical image (JPG or PNG):",
    type=["jpg", "jpeg", "png"]
)

submit_button = st.button("Generate Image Analysis")

if submit_button:
    if upload_file is None:
        st.error("Please upload an image first.")
    else:
        # Read image bytes
        image_bytes = upload_file.read()

        # Show uploaded image
        st.image(image_bytes, caption="Uploaded Image", use_container_width=True)  # FIXED

        # Prepare input for Gemini Vision
        prompt_parts = [
            {"mime_type": upload_file.type, "data": image_bytes},  # FIXED: correct mime_type
            system_prompt
        ]

        # Generate response
        response = model.generate_content(prompt_parts)

        # Show result
        st.markdown("### 🧠 Analysis Result")
        st.write(response.text)
