from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API", None)

# Initialize client
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Collection names
TITLE_DESC_COLLECTION = "video_title_desc"
SUMMARY_COLLECTION = "video_summary"


def test_qdrant_connection():
    """
    Test if Qdrant is reachable and print a success message.
    """
    try:
        # Fetch list of collections as a lightweight check
        collections = client.get_collections()
        print(f"Connected to Qdrant successfully! Collections available: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")


# Example usage
if __name__ == "__main__":
    test_qdrant_connection()
