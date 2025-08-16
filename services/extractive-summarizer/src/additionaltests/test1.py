from embeddings.embedder import embed_title_desc
from qdrant.qdrant_cli import insert_title_desc
vector = embed_title_desc("Computer Vision Explained in 5 Minutes | AI Explained", "Get a look at our course on data science and AI here: http://bit.ly/3K7Ak2c ...")

# Insert embedding in Qdrant
insert_title_desc(
            video_id="puB-4LuRNys",
            vector=vector.tolist() if hasattr(vector, "tolist") else vector,
            metadata={
                "video_id": "puB-4LuRNys" ,
                "published_date": "2025-08-16"
            }
)