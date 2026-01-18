from constants import MIN_PARA_LENGTH, MAX_PARA_LENGTH


class Chunker:
    def chunk_text(self, texts: list):
        chunks = []
        for text in texts:
            paras = text.split("\n")
            for para in paras:
                if len(para) > MIN_PARA_LENGTH:
                    # further split long paragraphs
                    if len(para) > MAX_PARA_LENGTH:
                        for i in range(0, len(para), 1500):
                            chunks.append(para[i : i + 1500])
                    else:
                        chunks.append(para)
        return chunks
