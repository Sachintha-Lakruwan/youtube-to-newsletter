from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env vars
load_dotenv()

# YouTube setup
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def insert_channel_if_missing(channel_id: str):
    """Fetch channel details from YouTube API and insert into Supabase if missing."""

    response = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    ).execute()

    if not response["items"]:
        print(f"Channel {channel_id} not found")
        return

    details = response["items"][0]

    record = {
        "id": channel_id,
        "title": details["snippet"]["title"],
        "description": details["snippet"].get("description", ""),
        "published_at": details["snippet"]["publishedAt"],
        "subscriber_count": int(details["statistics"].get("subscriberCount", 0)),
        "video_count": int(details["statistics"].get("videoCount", 0)),
        "view_count": int(details["statistics"].get("viewCount", 0)),
        "thumbnail_url": details["snippet"]["thumbnails"]["default"]["url"]
                        if "thumbnails" in details["snippet"] else None,
    }

    supabase.table("channels").upsert(record).execute()
    print(f"Channel {channel_id} inserted/updated")

