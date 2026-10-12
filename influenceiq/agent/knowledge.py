"""RAG layer: a small in-memory vector store (embeddings + cosine similarity).

It holds two kinds of documents:
  * "methodology" - how InfluenceIQ's scores are computed (so the agent can explain them)
  * "post"        - titles/captions of creators that have been analysed
"""
import threading

import numpy as np

from influenceiq.agent import llm

METHODOLOGY_DOCS = [
    ("methodology:iis",
     "Influencer Intelligence Score (IIS): a weighted sum of four parts, each between 0 and 1: "
     "Engagement Quality (35%), Authenticity (30%), Consistency (20%) and Audience Alignment (15%). "
     "Verdict: IIS >= 0.75 is HIGHLY RECOMMENDED, IIS >= 0.55 is POTENTIAL COLLAB, below 0.55 is LOW PRIORITY."),
    ("methodology:eqs",
     "Engagement Quality Score (EQS): combines engagement rate (40%), comment strength ratio (25%), "
     "engagement depth (20%) and engagement consistency (15%). YouTube uses a views-based rate "
     "((likes + comments) / views); Reddit and Instagram use a follower-based rate. "
     "Instagram comments count half as much as likes. Consistency is 1 / (1 + coefficient of variation) "
     "of engagement across posts, so steady engagement scores higher than spiky engagement."),
    ("methodology:authenticity",
     "Authenticity Index: heuristic rules, not machine learning. It averages five risk signals: low "
     "engagement rate, comment-to-like imbalance, volatile engagement, likes far below 1% of followers, "
     "and generic comments (currently a placeholder that always scores 0 because comment text is not collected). "
     "Authenticity Index = 1 minus the average signal. Risk level: LOW RISK below 0.3, MEDIUM RISK below 0.6, "
     "otherwise HIGH RISK. A low index means engagement looks unusual for the audience size; it is not proof of fake followers."),
    ("methodology:niche",
     "Niche detection is keyword based. It counts niche keywords (fitness, fashion, travel, tech, finance, food, "
     "education, gaming, lifestyle) in the bio and in post titles/captions. Audience Alignment is the share of "
     "keyword hits that belong to the top niche, so a creator focused on one topic scores higher than a mixed one. "
     "Content drift compares the main niche of the older half of posts with the newer half."),
    ("methodology:data",
     "Data sources and limits: YouTube data comes from the official YouTube Data API (highest reliability), "
     "Reddit from public JSON endpoints (medium), and Instagram only from sample or uploaded CSV data (limited). "
     "Only post titles/captions and public counts are collected: no comment text and no private accounts."),
]


class VectorStore:
    def __init__(self, embed_fn=None):
        self._embed_fn = embed_fn
        self._lock = threading.Lock()
        self.ids = []
        self.texts = []
        self.metas = []
        self._matrix = np.zeros((0, 0), dtype=np.float32)
        self._methodology_loaded = False

    def _embed(self, texts):
        fn = self._embed_fn or llm.embed
        return np.array(fn(texts), dtype=np.float32)

    @staticmethod
    def _normalize(m):
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return m / norms

    def add(self, ids, texts, metas):
        """Add documents, skipping ids that are already stored."""
        with self._lock:
            existing = set(self.ids)
            new = [i for i, d in enumerate(ids) if d not in existing]
            if not new:
                return 0
            vecs = self._normalize(self._embed([texts[i] for i in new]))
            self._matrix = vecs if self._matrix.size == 0 else np.vstack([self._matrix, vecs])
            for i in new:
                self.ids.append(ids[i])
                self.texts.append(texts[i])
                self.metas.append(metas[i])
            return len(new)

    def ensure_methodology(self):
        if self._methodology_loaded:
            return
        ids = [d[0] for d in METHODOLOGY_DOCS]
        texts = [d[1] for d in METHODOLOGY_DOCS]
        metas = [{"type": "methodology"} for _ in METHODOLOGY_DOCS]
        self.add(ids, texts, metas)
        self._methodology_loaded = True

    @staticmethod
    def _creator_matches(meta, creator):
        """Loose match: 'mkbhd' matches the stored name 'Marques Brownlee' via its alias."""
        c = creator.lower().strip()
        names = [str(meta.get("creator", "")).lower(), str(meta.get("alias", "")).lower()]
        return any(n and (c in n or n in c) for n in names)

    def has_posts_for(self, creator):
        return any(m.get("type") == "post" and self._creator_matches(m, creator) for m in self.metas)

    def search(self, query, top_k=4, creator=None):
        """Top-k most similar documents (optionally only posts of one creator)."""
        self.ensure_methodology()
        if not self.ids:
            return []
        q = self._normalize(self._embed([query]))[0]
        scores = self._matrix @ q
        order = np.argsort(-scores)
        results = []
        for idx in order:
            meta = self.metas[idx]
            if creator and (meta.get("type") != "post" or not self._creator_matches(meta, creator)):
                continue
            results.append({
                "score": round(float(scores[idx]), 3),
                "type": meta.get("type"),
                "creator": meta.get("creator"),
                "text": self.texts[idx],
            })
            if len(results) >= top_k:
                break
        return results


_store = VectorStore()


def get_store():
    return _store
