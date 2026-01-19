from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def get_llm(model: str = "models/gemini-flash-latest", temperature: float = 0):
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=temperature
    )

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )