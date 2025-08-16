# src/qdrant/qdrant_cli.py
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API", None)


client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Collection names
TITLE_DESC_COLLECTION = "video_title_desc"

SUMMARY_COLLECTION = "video_summary"



def video_id_to_uuid(video_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, video_id))

def insert_title_desc(video_id: str, vector: list[float], metadata: dict):
    """
    Insert embedding for title + description
    metadata: {video_id, published_date}
    """
    client.upsert(
        collection_name=TITLE_DESC_COLLECTION,
        points=[
            PointStruct(
                id=video_id_to_uuid(video_id),
                vector=vector,
                payload=metadata
            )
        ]
    )

def insert_summary(video_id: str, vector: list[float], metadata: dict):
    """
    Insert embedding for extractive summary
    metadata: additional info(e.g.:video_id)
    """
    client.upsert(
        collection_name=SUMMARY_COLLECTION,
        points=[
            PointStruct(
                id=video_id_to_uuid(video_id),
                vector=vector,
                payload=metadata
            )
        ]
    )
def get_title_desc_embedding(video_id: str):
    """
    Retrieve the embedding and payload for a specific video_id from title+description collection.
    """
    results = client.retrieve(
        collection_name=TITLE_DESC_COLLECTION,
        ids=[video_id]  
    )
    if results and len(results) > 0:
        return results[0]  # returns PointStruct with vector + payload
    return None

def get_summary_embedding(video_id: str):
    """
    Retrieve the embedding and payload for a specific video_id from summary collection.
    """
    results = client.retrieve(
        collection_name=SUMMARY_COLLECTION,
        ids=[video_id]  
    )
    if results and len(results) > 0:
        return results[0]  # returns PointStruct with vector + payload
    return None

def search_title_desc(query_vector: list[float], top_k: int = 5):
    return client.search(
        collection_name=TITLE_DESC_COLLECTION,
        query_vector=query_vector,
        limit=top_k
    )

def search_summary(query_vector: list[float], top_k: int = 5):
    return client.search(
        collection_name=SUMMARY_COLLECTION,
        query_vector=query_vector,
        limit=top_k
    )
