# RAG Chatbot (site-specific)

This is a small Retrieval-Augmented Generation (RAG) prototype that lets you
ingest a website and ask questions restricted to the site's content.

Core features

- Accepts a website URL and crawls same-domain pages (configurable depth / pages).
- Extracts cleaned textual content (removes headers, footers, nav, scripts, ads).
- Creates embeddings (sentence-transformers or configurable embedder) and indexes them with FAISS.
- Provides an interactive Streamlit UI for ingesting sites and asking questions.

Design notes

- The system retrieves top passages from the indexed site and generates answers based on that context.
- The project includes both programmatic components (crawler, cleaner, embeddings, FAISS store, QA engine)
  and a Streamlit app at `rag_chatbot/app.py`.

Quick start (Streamlit UI)

1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r rag_chatbot/requirements.txt
```

2. Run the Streamlit app:

```bash
streamlit run rag_chatbot/app.py
```

3. In the browser UI:
- Enter a website URL (http/https) and set `Max pages` for crawling.
- Click "Ingest / Index Site" to crawl and build the FAISS index.
- Once indexing completes, ask questions in the "Ask a question" box and click "Ask".

Programmatic usage

If you prefer to use the library programmatically (for automation or tests), you can use the
`QAEngine` in `rag_chatbot/qa.py`:

```python
from rag_chatbot.qa import QAEngine

engine = QAEngine()
# Ingest a site (returns number of chunks indexed)
engine.ingest('https://example.com', max_pages=5)
# Generate an answer to a question based on the indexed site
answer = engine.generate_response('What does this website say about X?')
print(answer)
```

Notes & troubleshooting

- The project currently has two embedding paths in different places:
  - The notebook examples use `sentence-transformers` (local model) which produces 384-dimensional vectors.
  - Some modules may still reference an external embedding/LLM provider (check `rag_chatbot/contants.py` and `rag_chatbot/qa.py`).

- If the code uses an external API (Google GenAI) you will need to set the API key. The repository's
  `rag_chatbot/contants.py` currently sets `API_KEY` as a module constant. For security, replace the
  hard-coded key there with reading from an environment variable or your secret manager before running the app.

- If you want an entirely local stack (no external LLM):
  - Use `sentence-transformers` for embeddings (already present in `requirements.txt`).
  - For generation, you can either:
    - Return the retrieved context verbatim as the "answer" (deterministic, safe), or
    - Plug in a local LLM backend (e.g., a small LLM with a compatible API) and modify `qa.py`.

Files of interest

- `rag_chatbot/crawler.py`  — crawler and link-extraction logic
- `rag_chatbot/cleaner.py`  — HTML cleaning and text extraction
- `rag_chatbot/embeddings.py` — embedder and `FaissStore`
- `rag_chatbot/qa.py`       — ingestion, retrieval, and LLM invocation
- `rag_chatbot/app.py`      — Streamlit UI (ingest + ask)

Next steps / suggestions

- Run the Streamlit app and ingest a small site (e.g., a documentation page) to validate everything.
- If you want me to: replace any external-API embedding/LLM calls with local-only components and add
  a small test harness to automatically validate ingest -> query paths.

If anything in the README is out of sync with the code you see, tell me and I will update it to match the
exact runtime behaviour (for example: switching the default embedder to local-only, or documenting env vars).
