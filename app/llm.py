import os
from langchain_google_genai import ChatGoogleGenerativeAI

def make_llm():
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest").strip()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    # allow both "models/..." and plain
    if model.startswith("models/"):
        model = model.replace("models/", "", 1)

    return ChatGoogleGenerativeAI(model=model, temperature=0.2, api_key=api_key)