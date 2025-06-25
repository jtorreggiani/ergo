from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embedding(text: str) -> list[float]:
    return model.encode(text, convert_to_numpy=True).tolist()