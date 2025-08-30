import os
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
from youtube.channel import insert_channel_if_missing
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Deterministic embedding ID generator
def video_id_to_uuid(video_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, video_id))

def insert_video(video: dict):
    """
    Insert a video record into the 'videos' table, generating a deterministic embedding_id.
    :param video: dictionary containing video metadata
    """
    insert_channel_if_missing(video["channel_id"])
    embedding_id = video_id_to_uuid(video['video_id'])

    record = {
        'video_id': video['video_id'],  
        'title': video['title'],
        'description': video['description'],
        'tags': video['tags'],  
        'published_at': video['published_date'],
        'thumbnail_url': video['thumbnail_url'],
        'channel_id': video['channel_id'],
        'embedding_id': embedding_id
    }
    supabase.table('videos').upsert([record]).execute()
    print("Upsert Successful")
    

