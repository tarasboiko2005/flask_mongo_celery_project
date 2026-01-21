import os
from langchain_ollama import OllamaEmbeddings, OllamaLLM

def get_embeddings():
    model = os.getenv("OLLAMA_EMBED_MODEL")
    return OllamaEmbeddings(model=model)

def get_llm():
    model = os.getenv("OLLAMA_LLM_MODEL")
    return OllamaLLM(model=model)