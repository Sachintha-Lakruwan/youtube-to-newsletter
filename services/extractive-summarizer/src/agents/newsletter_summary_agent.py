from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from db.mongo_client import summaries_collection
from db.mongo_client import store_abstractive
from typing import Dict
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

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

def editor_agent(state: Dict) -> Dict:
    for video in state.get("videos", []):
        video_id = video["video_id"]
        extractive = video.get("extractive_summary", "")
        abstractive = summarize_video(extractive) if extractive else ""

        # Save in MongoDB
        store_abstractive(video_id=video_id, abstractive_summary=abstractive)

        

    return state

