from qdrant_client import QdrantClient, models
import os
from dotenv import load_dotenv
import numpy as np
load_dotenv()

# Load Qdrant URL & API key from environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API", None)

# Initialize client
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
vector_size=1024
COLLECTION_NAME="video_title_desc"
video_id = 1
vector = np.random.rand(vector_size).tolist()
metadata = {"video_id": video_id, "published_date": "2025-08-16"}

# Insert point
try:
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=video_id,
                vector=vector,
                payload=metadata
            )
        ]
    )
    print("Embedding inserted successfully!")
except Exception as e:
    print("Error inserting embedding:", e)
