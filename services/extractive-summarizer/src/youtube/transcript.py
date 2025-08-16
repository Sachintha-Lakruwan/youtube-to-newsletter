from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript(video_id: str) -> str:
    """
    Return transcript text as a single string for a YouTube video id.

    """
    try:
            ytt = YouTubeTranscriptApi()
            transcript = ytt.fetch(video_id)

            texts = []
            for item in transcript:
                if isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
                else:

                    texts.append(getattr(item, "text", str(item)))
            return " ".join(texts)
    except Exception as e2:
            raise RuntimeError(f"Failed to fetch transcript")
