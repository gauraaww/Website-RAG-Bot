from embeddings import Embedder, FaissStore
from cleaner import Cleaner
from crawler import Crawler
from constants import (
    API_KEY,
    EMBEDDNG_DIM,
    SYSTEM_PROMPT,
    GEMINI_MODEL,
    EMBEDDING_MODEL,
    TOP_K,
    FAILED_CONTEXT_RETRIEVAL,
)
from google import genai
from google.genai import types


class QAEngine:
    def __init__(self):
        self.crawler = Crawler()
        self.cleaner = Cleaner()
        self.embedder = Embedder(model_name=EMBEDDING_MODEL)
        self.faiss_store = FaissStore(EMBEDDNG_DIM)
        self.client = genai.Client(api_key=API_KEY)

    def indexing(self, url, max_pages=10):
        # crawler raw html content
        pages = self.crawler.crawl(url, max_pages=max_pages)
        texts = []
        urls = []
        # clean html content
        for u, html in pages:
            parsed_text = self.cleaner.clean_html(html)
            if parsed_text and len(parsed_text) > 30:
                texts.append(parsed_text)
                urls.append(u)

        if not texts:
            raise ValueError("No usable content extracted from site")

        # chunk by simple paragraph chunks
        chunks = []
        for text in texts:
            paras = text.split("\n")
            for para in paras:
                if len(para) > 50:
                    # further split long paragraphs
                    if len(para) > 2000:
                        for i in range(0, len(para), 1500):
                            chunks.append(para[i : i + 1500])
                    else:
                        chunks.append(para)

        # create embedding
        embeddings = self.embedder.embed_texts(texts=chunks)

        # index and store in index_path
        self.faiss_store.add(embeddings=embeddings, texts=chunks)
        self.faiss_store.save()
        return len(chunks)

    def fetch_context(self, question, k=TOP_K):
        self.faiss_store.load()
        if not self.faiss_store.texts:
            raise ValueError("No index loaded. Run ingest first.")
        q_emb = self.embedder.embed_texts(texts=[question])
        results = self.faiss_store.search(query_emb=q_emb, k=k)
        # assemble answer: return top passages with scores
        answer = ""
        for paragraph, score in results:
            answer += f"[score={score:.3f}] {paragraph} \n\n"
        return answer

    def get_recent_conversation(self, previous_conversation, max_turns=5):
        recent_conversation = []
        for chat in previous_conversation[-max_turns:]:
            q = chat["question"]
            a = chat["answer"]
            recent_conversation.append({"question": q, "answer": a})
        return recent_conversation

    def ask_gemini(self, context, question, previous_conversation=[]):
        prompt = f"""
            Context:
            {context if context else "No relevant context provided."}

            Previous Conversation:
            {str(previous_conversation) if previous_conversation else "No previous conversation available."}

            Question:
            {question}
        """
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            contents=prompt,
        )
        return response.text.strip()

    def generate_response(self, question, previous_conversation=[]):
        retrieved = self.fetch_context(question)
        recent_conversation = self.get_recent_conversation(previous_conversation)
        print("recent conversation:", recent_conversation)

        if not retrieved and not recent_conversation:
            print("failed to retrieve context and no recent conversation")
            return FAILED_CONTEXT_RETRIEVAL

        context = "\n\n".join(retrieved)
        return self.ask_gemini(context, question, recent_conversation)
