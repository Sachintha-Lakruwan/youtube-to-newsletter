from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from db.mongo_client import summaries_collection
from typing import Dict
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

def summarize_video(extractive_summary: str) -> str:
    prompt = f"""
You are an AI assistant. Write a concise, reader-friendly abstractive summary suitable for a newsletter.
Please make it more descriptive enough to engage users.
Extractive summary:
{extractive_summary}

Respond with only the abstractive summary text.
"""
    result = llm.invoke([HumanMessage(content=prompt)])
    return result.content.strip()

def summarization_agent(state: Dict) -> Dict:
    processed_videos = []

    for vid in state["video_ids"]:
        doc = summaries_collection.find_one({"video_id": vid})
        extractive = doc.get("extractive_summary", "") if doc else ""
        abstractive = summarize_video(extractive) if extractive else ""
        processed_videos.append({
            "video_id": vid,
            "extractive_summary": extractive,
            "abstractive_summary": abstractive
        })

    return {**state, "videos": processed_videos}