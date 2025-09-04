import nltk
nltk.download('punkt_tab')
from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize
from embeddings.embedder import embed_extractive_summary
from db.mongo_client import store_extractive
from qdrant.qdrant_cli import insert_summary
import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from sklearn.cluster import KMeans

# BART setup (abstractive)
bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

sbert_model_name = "sentence-transformers/all-mpnet-base-v2"
sbert = SentenceTransformer(sbert_model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sbert.to(device)

# ---------------------------
# Hierarchical embeddings
# ---------------------------
def get_hierarchical_embeddings(text, segment_size=8):
    sentences = sent_tokenize(text)
    if not sentences:
        return [], torch.empty(0)
    sentence_embs = sbert.encode(sentences, convert_to_tensor=True).to(device)

    # Segment embeddings
    segment_embs = []
    for i in range(0, len(sentences), segment_size):
        chunk_emb = sentence_embs[i:i+segment_size].mean(dim=0)
        segment_embs.extend([chunk_emb] * min(segment_size, len(sentences)-i))
    segment_embs = torch.stack(segment_embs)

    # Weighted fusion
    enriched_embs = 0.7 * sentence_embs + 0.3 * segment_embs
    return sentences, enriched_embs

# ---------------------------
# Dynamic sentence count
# ---------------------------
def dynamic_top_k(n_sentences, short_k=20, long_k=50):
    if n_sentences < 200:
        return short_k
    elif n_sentences > 800:
        return long_k
    else:
        # Linear scaling
        return int(short_k + (long_k - short_k) * (n_sentences / 800))
    

# ---------------------------
# Cluster-based selection 
# ---------------------------
def select_sentences_cluster_with_lead_cosine(text, short_k=20, long_k=50, n_head=2):
    sentences, enriched_embs = get_hierarchical_embeddings(text)
    n_sentences = len(sentences)
    if n_sentences == 0:
        return ""

    top_k = dynamic_top_k(n_sentences, short_k=short_k, long_k=long_k)

    # Always include lead sentences
    selected_idx = list(range(min(n_head, n_sentences)))

    # If we already reached top_k, truncate
    selected_idx = selected_idx[:top_k]
    remaining = top_k - len(selected_idx)

    if remaining > 0 and n_sentences > len(selected_idx):
        # Cluster remaining sentences
        cluster_candidates = [i for i in range(n_sentences) if i not in selected_idx]
        n_clusters = min(remaining, max(1, len(cluster_candidates)//10))
        if n_clusters > 0:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_embs = enriched_embs[cluster_candidates].cpu().numpy()
            cluster_ids = kmeans.fit_predict(cluster_embs)

            # Global embedding for cosine similarity
            global_emb = enriched_embs.mean(dim=0, keepdim=True)

            for cluster_id in range(n_clusters):
                cluster_idx = [cluster_candidates[i] for i in range(len(cluster_candidates)) if cluster_ids[i]==cluster_id]
                if not cluster_idx:
                    continue
                cluster_vectors = enriched_embs[cluster_idx]
                sims = util.pytorch_cos_sim(cluster_vectors, global_emb).cpu().numpy().flatten()
                best_idx = cluster_idx[sims.argmax()]
                selected_idx.append(best_idx)
                if len(selected_idx) >= top_k:
                    break

    selected_idx = sorted(selected_idx)[:top_k]
    return " ".join([sentences[i] for i in selected_idx])

# ---------------------------
# Chunked abstractive rewrite
# ---------------------------
def abstractive_rewrite_long_summary(extractive_summary, chunk_size=200, max_length=150, min_length=40):
    words = extractive_summary.split()
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    abstractive_chunks = []
    for chunk in chunks:
        inputs = bart_tokenizer(chunk, return_tensors="pt", truncation=True, max_length=1024).to(device)
        summary_ids = bart_model.generate(
            inputs.input_ids,
            num_beams=4,
            length_penalty=2.0,
            max_length=max_length,
            min_length=min_length,
            no_repeat_ngram_size=3,
            early_stopping=True
        )
        abstractive_chunk = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        abstractive_chunks.append(abstractive_chunk)

    return " ".join(abstractive_chunks)

def generate_extractive_summary(transcript, use_abstractive=False):
    extractive_summary = select_sentences_cluster_with_lead_cosine(transcript)

    if use_abstractive:
        final_summary = abstractive_rewrite_long_summary(extractive_summary)
    else:
        final_summary = extractive_summary

    
    return final_summary

def store_extractive_summary(video_id: str, extractive_summary: str, store_qdrant=True):
    """
    Store extractive summary in MongoDB and Qdrant .

    Args:
        video_id (str)
        extractive_summary (str)
        store_qdrant (bool): whether to store embedding in Qdrant
    """
    # Update MongoDB
    store_extractive(video_id=video_id,extractive_summary=extractive_summary)

    # Store embedding in Qdrant
    
    if store_qdrant:
        vector = embed_extractive_summary(extractive_summary)
        insert_summary(
            video_id=video_id,
            vector=vector.tolist() if hasattr(vector, "tolist") else vector,
            metadata={"video_id": video_id}
        )
