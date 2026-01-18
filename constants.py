import os
import streamlit as st

CUR_PATH = os.path.dirname(os.path.abspath(__file__))


# Chunker
MIN_PARA_LENGTH = 200
MAX_PARA_LENGTH = 3000

# embedding
EMBEDDNG_DIM = 768
API_KEY = st.secrets["GEMINI_KEY"]
TOP_K = 5
INDEX_PATH = f"{CUR_PATH}/data/faiss_index"
CHUNKS_PATH = f"{CUR_PATH}/data/chunks.pkl"
EMBEDDING_MODEL = "text-embedding-004"

# QA
SYSTEM_PROMPT = """
    You are an intelligent assistant tasked with answering questions based on the provided context and previous conversations.
        Follow these rules strictly:
        1. If there is relevant context, use it to answer the question. But do not mention that you are using the context.
        2. If there is a previous conversation, incorporate it to provide a coherent and context-aware response. User might be asking follow-up questions.
"""
FAILED_CONTEXT_RETRIEVAL = "The answer is not available on the provided website."
GEMINI_MODEL = "gemini-2.5-flash"
