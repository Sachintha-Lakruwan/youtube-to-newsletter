import nltk
nltk.download('punkt_tab')
from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize
from embeddings.embedder import embed_extractive_summary
from db.mongo_client import store_extractive
from qdrant.qdrant_cli import insert_summary
import torch
from transformers import BartTokenizer, BartForConditionalGeneration

# BART setup (abstractive)
bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

sbert_model_name = "all-MiniLM-L6-v2"
sbert = SentenceTransformer(sbert_model_name)

def compute_relevance_scores(sentences):
    """
    Relevance score: cosine similarity of each sentence embedding to the mean document embedding.
    Returns scores list matching sentences.
    """
    embeds = sbert.encode(sentences, convert_to_tensor=True, show_progress_bar=False)
    doc_embed = embeds.mean(dim=0, keepdim=True)
    cos = util.cos_sim(embeds, doc_embed).squeeze().cpu().numpy()
    # normalize to 0..1
    cos = (cos - cos.min()) / (cos.max() - cos.min() + 1e-8)
    return cos.tolist(), embeds

def compute_coherence_scores(sentences, sent_embeds=None):
    """
    Coherence score for each sentence: similarity with the previous sentence (0 for first sentence).
    We return a list same length as sentences.
    """
    if sent_embeds is None:
        sent_embeds = sbert.encode(sentences, convert_to_tensor=True, show_progress_bar=False)
    scores = [0.0] * len(sentences)
    if len(sentences) < 2:
        return scores
    for i in range(1, len(sentences)):
        sim = util.cos_sim(sent_embeds[i], sent_embeds[i-1]).item()
        # normalize later combined with relevance; keep raw sim ([-1,1])
        scores[i] = (sim + 1) / 2.0  # map to [0,1]
    return scores

# Select top-k extractive sentences using combined score
def select_extractive(sentences, top_k=8, alpha=0.7):
    """
    alpha: weight for relevance, (1-alpha) for coherence
    Returns selected sentences and their original indices (kept in original order).
    """
    relevance_scores, sent_embeds = compute_relevance_scores(sentences)
    coherence_scores = compute_coherence_scores(sentences, sent_embeds)
    final_scores = []
    for r, c in zip(relevance_scores, coherence_scores):
        final_scores.append(alpha * r + (1 - alpha) * c)
    # pick top_k indices
    import numpy as np
    idx_sorted = np.argsort(final_scores)[::-1]
    top_idx = sorted(idx_sorted[:min(top_k, len(sentences))])  # sort to keep original order
    selected = [sentences[i] for i in top_idx]
    return selected, top_idx, sent_embeds

def abstractive_rewrite(text, max_input_tokens=1024, max_output_tokens=500, min_output_tokens=120):
    """
    Feed text to BART and return abstractive summary string.
    Text will be truncated if needed by tokenizer.
    """
    inputs = bart_tokenizer([text], max_length=max_input_tokens, truncation=True, return_tensors="pt")
    with torch.no_grad():
        summary_ids = bart_model.generate(
            inputs["input_ids"],
            num_beams=5,
            length_penalty=1.0,
            max_length=max_output_tokens,
            min_length=min_output_tokens,
            no_repeat_ngram_size=3,
            early_stopping=True,
        )
    summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return summary

def hybrid_fusion(extractive_sents, abstractive_summary, dedupe_threshold=0.82):
    """
    Combine abstractive summary (split to sentences) with extractive sentences.
    We dedupe by embedding similarity: if a candidate sentence is highly similar to one already taken, skip it.
    Final ordering: we preserve original order for extractive sentences; abstractive sentences are placed first,
    but duplicates removed.
    """
    abs_sents = sent_tokenize(abstractive_summary)
    all_candidates = []
    # mark source type for potential weighting/debugging
    for s in abs_sents:
        all_candidates.append(("abs", s))
    for s in extractive_sents:
        all_candidates.append(("ext", s))

    final = []
    final_embeds = []
    for src, s in all_candidates:
        emb = sbert.encode(s, convert_to_tensor=True)
        keep = True
        for fe in final_embeds:
            if util.cos_sim(emb, fe).item() >= dedupe_threshold:
                keep = False
                break
        if keep:
            final.append((src, s))
            final_embeds.append(emb)
    # produce final text: we can order by preferring extractive order after abstractive:

    abs_final = [s for src, s in final if src == "abs"]
    ext_final = [s for src, s in final if src == "ext"]
    final_text = " ".join(abs_final + ext_final)
    return final_text

def generate_extractive_summary(transcript: str, top_k=8, alpha=0.7) -> str:
    """
    Generate an extractive summary from transcript text.

    Args:
        transcript (str): full transcript text
        top_k (int): number of sentences to select
        alpha (float): weight for relevance vs coherence

    Returns:
        str: extractive summary
    """
    sentences = sent_tokenize(transcript)
    selected_sents, selected_idx, sent_embeds = select_extractive(sentences, top_k=top_k, alpha=alpha)
    #selected_sents, _, _ = select_extractive(sentences, top_k=top_k, alpha=alpha)
    bart_input = " ".join(selected_sents)
    abstractive_summary = abstractive_rewrite(bart_input)
    final_extractive_summary = hybrid_fusion(selected_sents, abstractive_summary)

    #extractive_summary = " ".join(selected_sents)
    return final_extractive_summary


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
