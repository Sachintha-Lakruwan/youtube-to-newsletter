from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "BAAI/bge-base-en"
model = SentenceTransformer(MODEL_NAME)

def embed_text(text: str) -> np.ndarray:
    """
    Generate embedding for a single text input.
    Returns a 768-dim vector.
    """
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding


def embed_extractive_summary(summary: str) -> np.ndarray:
    """
    Generate embedding for extractive summary.
    """
    return embed_text(summary)

def embed_title_desc(title: str, desc: str) -> np.ndarray:
    """
    Generate embedding for title+description of the video.
    """
    combined_text = f"{title}. {desc}"
    return embed_text(combined_text)
    
