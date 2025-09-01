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
summaries_collection = db["summaries"]