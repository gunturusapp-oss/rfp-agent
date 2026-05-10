import google.generativeai as genai
import streamlit as st

# Use your actual API key from secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

print("\n🔍 AVAILABLE GEMINI MODELS:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Description: {model.display_name}")
        print()
