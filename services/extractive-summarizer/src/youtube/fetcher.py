from googleapiclient.discovery import build
import os
import isodate
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

def iso8601_duration_to_seconds(duration: str) -> int:
    """
    Convert ISO 8601 duration string to seconds.
    """
    return int(isodate.parse_duration(duration).total_seconds())

def fetch_videos_for_subdomain(subdomain: str, max_results: int = 10) -> list[dict]:
    """
    Fetch videos for a given subdomain (keyword/topic).
    Filters out Shorts (duration < 60 sec).
    Returns list of video metadata dicts
    """
    print(f"[Fetcher] Fetching videos for subdomain: {subdomain}")

    videos = []

    # Search videos by keyword
    request = youtube.search().list(
        q=subdomain,
        type="video",
        part="id,snippet",
        maxResults=max_results
    )
    response = request.execute()
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        published_date = item["snippet"]["publishedAt"]
        channel_id=item["snippet"]["channelId"]
        thumbnail_url=item["snippet"]["thumbnails"]['default']['url']


        # Fetch video details for duration and views
        details_request = youtube.videos().list(
            part="contentDetails,statistics",
            id=video_id
        )
        details_response = details_request.execute()
        details = details_response["items"][0]

        # Skip Shorts (<60 sec)
        duration = details["contentDetails"]["duration"]
        if iso8601_duration_to_seconds(duration) < 60:
            continue

        if details["contentDetails"].get("caption", "false") != "true":
            continue

        # views
        views = int(details["statistics"].get("viewCount", 0))
        # tags
        tags=[subdomain]

        # Append video metadata dict
        videos.append({
            "video_id": video_id,
            "title": title,
            "description": description,
            "published_date": published_date,
            "channel_id": channel_id,
            "tags": tags,
            "thumbnail_url": thumbnail_url
        })



    print(f"[Fetcher] Total videos fetched for {subdomain}: {len(videos)}")
    return videos
