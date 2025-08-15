from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os 
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URL") 
DB_NAME = "videosummary"

try:
    client = MongoClient(MONGO_URI)
    # Test connection
    client.admin.command("ping")
    print("Connected to MongoDB successfully")
except ConnectionFailure as e:
    print(f"MongoDB connection failed: {e}")
    raise

# Get the database
db = client[DB_NAME]

# Collections
metadata_collection = db["metadata"]
summaries_collection = db["summaries"]

# Ensure indexes
metadata_collection.create_index("video_id", unique=True)
summaries_collection.create_index("video_id", unique=True)

def insert_metadata(video_id: str, published_date: str, title: str, views: int, description: str):
    """Insert or update video metadata."""
    metadata_collection.update_one(
        {"video_id": video_id},
        {"$set": {
            "published_date": published_date,
            "title": title,
            "views": views,
            "description": description
        }},
        upsert=True
    )

def insert_summaries(video_id: str, transcript: str, abstractive_summary: str, extractive_summary: str):
    """Insert or update video summaries."""
    summaries_collection.update_one(
        {"video_id": video_id},
        {"$set": {
            "transcript": transcript,
            "abstractive_summary": abstractive_summary,
            "extractive_summary": extractive_summary
        }},
        upsert=True
    )

def get_metadata(video_id: str):
    return metadata_collection.find_one({"video_id": video_id})

def get_summaries(video_id: str):
    return summaries_collection.find_one({"video_id": video_id})