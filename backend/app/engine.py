import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import settings

logger = logging.getLogger("ipmprs.engine")

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having",
    "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how",
    "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the",
    "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "proposal", "department", "police", "request", "need", "project"
}

def extract_keywords(text: str) -> List[str]:
    """Extract significant keywords from text for highlighting and overlap analysis."""
    tokens = re.findall(r"\b[A-Za-z0-9\-_]{3,}\b", text.lower())
    seen = set()
    keywords = []
    for t in tokens:
        if t not in STOP_WORDS and t not in seen:
            seen.add(t)
            keywords.append(t)
    return keywords

class PrecedentEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PrecedentEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.is_semantic = False
        self.active_engine = "Initializing..."
        self._load_engine()

    def _load_engine(self):
        """Attempts to load sentence-transformers once; auto-falls back to TF-IDF."""
        try:
            logger.info("Loading sentence-transformers model '%s'...", self.model_name)
            from sentence_transformers import SentenceTransformer
            # Keep local development/startup offline-safe. If the model is not
            # already cached, the existing TF-IDF fallback is used immediately.
            self.model = SentenceTransformer(self.model_name, local_files_only=True)
            self.is_semantic = True
            self.active_engine = f"Sentence Transformers ({self.model_name})"
            logger.info("Successfully loaded %s", self.active_engine)
        except Exception as e:
            logger.warning("Falling back to TF-IDF vectorizer due to: %s", str(e))
            self.model = None
            self.is_semantic = False
            self.active_engine = "TF-IDF Vectorizer (Scikit-Learn Fallback)"

    def encode(self, text: str) -> Optional[List[float]]:
        """Encodes text to a float vector if semantic model is active; otherwise None."""
        if self.is_semantic and self.model:
            try:
                emb = self.model.encode(text, convert_to_numpy=True)
                return emb.tolist()
            except Exception as e:
                logger.error("Encoding error: %s", str(e))
        return None

    def compute_similarity(
        self,
        query: str,
        proposals_data: List[Dict[str, Any]],
        threshold: float = 0.35,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid semantic (cosine) + keyword search over proposal candidates.
        """
        if not proposals_data:
            return []

        query_keywords = extract_keywords(query)
        corpus_texts = [p["corpus_text"] for p in proposals_data]

        # 1. Semantic Cosine Similarity
        semantic_scores = np.zeros(len(proposals_data))
        if self.is_semantic and self.model:
            try:
                query_vec = self.model.encode([query], convert_to_numpy=True)
                
                # Retrieve or compute proposal vectors
                candidate_vecs = []
                for p in proposals_data:
                    if p.get("embedding"):
                        candidate_vecs.append(p["embedding"])
                    else:
                        candidate_vecs.append(self.model.encode(p["corpus_text"], convert_to_numpy=True))
                
                candidate_matrix = np.array(candidate_vecs)
                sims = cosine_similarity(query_vec, candidate_matrix)[0]
                semantic_scores = np.clip(sims, 0.0, 1.0)
            except Exception as e:
                logger.warning("Semantic similarity computation error, falling back to TF-IDF: %s", str(e))
                self.is_semantic = False
                self.active_engine = "TF-IDF Vectorizer (Scikit-Learn Fallback)"

        # 2. Keyword / TF-IDF Vectorizer Similarity
        try:
            tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=5000)
            all_texts = [query] + corpus_texts
            tfidf_matrix = tfidf.fit_transform(all_texts)
            tfidf_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            keyword_scores = np.clip(tfidf_sims, 0.0, 1.0)
        except Exception as e:
            logger.warning("TF-IDF calculation error: %s", str(e))
            keyword_scores = np.zeros(len(proposals_data))

        # 3. Hybrid Blend
        results = []
        for idx, p in enumerate(proposals_data):
            if self.is_semantic:
                # 65% semantic meaning + 35% exact keyword/lexical overlap
                blended_score = float(0.65 * semantic_scores[idx] + 0.35 * keyword_scores[idx])
            else:
                blended_score = float(keyword_scores[idx])

            # Clamp between 0.0 and 1.0
            final_score = round(max(0.0, min(1.0, blended_score)), 4)
            is_strong = final_score >= threshold

            # Overlapping matching tokens
            proposal_kw = extract_keywords(p["corpus_text"])
            matched_tokens = [w for w in query_keywords if w in proposal_kw]

            # Construct transparent "why matched"
            why_parts = []
            if self.is_semantic and semantic_scores[idx] > 0.3:
                why_parts.append(f"Conceptual alignment ({int(semantic_scores[idx]*100)}% semantic score)")
            if matched_tokens:
                sample_tokens = matched_tokens[:5]
                why_parts.append(f"Direct terminology overlap on: {', '.join(sample_tokens)}")
            if p.get("category") and p["category"].lower() in query.lower():
                why_parts.append(f"Matching category '{p['category']}'")
            if not why_parts:
                why_parts.append("Broad departmental and keyword correlation")
            
            why_matched = "; ".join(why_parts)

            results.append({
                "id": p["id"],
                "proposal_code": p["proposal_code"],
                "title": p["title"],
                "category": p["category"],
                "department": p["department"],
                "cost": p["cost"],
                "decision": p.get("decision"),  # NEVER invent
                "reason": p.get("reason"),      # NEVER invent
                "date": p["date"],
                "source_link": f"/proposals/{p['id']}",
                "similarity_score": final_score,
                "is_strong_precedent": is_strong,
                "highlighted_matches": matched_tokens[:8],
                "why_matched": why_matched,
                "implementation_outcome": p.get("implementation_outcome"),
                "lessons_learned": p.get("lessons_learned")
            })

        # Sort descending by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

# Global singleton engine
precedent_engine = PrecedentEngine()
