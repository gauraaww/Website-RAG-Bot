import numpy as np
import faiss
import pickle
from google import genai
from google.genai import types
from constants import API_KEY, INDEX_PATH, CHUNKS_PATH


class Embedder:
    def __init__(self, model_name):
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name

    def embed_texts(self, texts, batch_size=50):
        all_embeddings = []

        # Process the list in chunks of batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            config = types.EmbedContentConfig(
                output_dimensionality=768,
                task_type="RETRIEVAL_DOCUMENT",  # Recommended for RAG storage
            )

            result = self.client.models.embed_content(
                model=self.model_name, contents=batch, config=config
            )

            # Extract numerical values from the response
            for embedding in result.embeddings:
                all_embeddings.append(embedding.values)

        return np.array(all_embeddings, dtype=np.float32)


class FaissStore:
    def __init__(self, dim):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.texts = []
        self.index_path = INDEX_PATH
        self.chunk_path = CHUNKS_PATH

    def add(self, embeddings, texts):
        # normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.texts.extend(texts)

    def search(self, query_emb, k=5):
        faiss.normalize_L2(query_emb)
        data, Index = self.index.search(query_emb, k)
        results = []
        for idx_list, score_list in zip(Index, data):
            for idx, score in zip(idx_list, score_list):
                if idx < len(self.texts):
                    results.append((self.texts[idx], float(score)))
        return results

    def save(self):
        if not self.index_path:
            raise ValueError("index path required to save")
        faiss.write_index(self.index, self.index_path + ".index")
        with open(self.chunk_path + ".texts.pkl", "wb") as f:
            pickle.dump(self.texts, f)

    def load(self):
        self.index = faiss.read_index(self.index_path + ".index")
        with open(self.chunk_path + ".texts.pkl", "rb") as f:
            self.texts = pickle.load(f)
        return self.index, self.texts
