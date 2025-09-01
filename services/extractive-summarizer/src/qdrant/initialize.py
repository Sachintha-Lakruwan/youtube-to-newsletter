from qdrant_client import QdrantClient, models
import os
from dotenv import load_dotenv

load_dotenv()

# Load Qdrant URL & API key from environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API", None)

# Initialize client
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def create_collections():
    # 1. Title + Description collection
    client.recreate_collection(
        collection_name="video_title_desc",
        vectors_config=models.VectorParams(
            size=768,  
            distance=models.Distance.COSINE
        )
    )

    # 2. Extractive Summary collection
    client.recreate_collection(
        collection_name="video_summary",
        vectors_config=models.VectorParams(
            size=768,
            distance=models.Distance.COSINE
        )
    )

if __name__ == "__main__":
    create_collections()
    print("✅ Qdrant collections created successfully!")
