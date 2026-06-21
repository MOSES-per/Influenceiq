import re
from collections import Counter

NICHE_KEYWORDS = {
    "fitness": [
        "fitness", "workout", "gym", "training", "health", "exercise",
        "body", "fatloss", "muscle"
    ],
    "fashion": [
        "fashion", "style", "outfit", "ootd", "clothing", "wear", "brand"
    ],
    "travel": [
        "travel", "trip", "vacation", "journey", "explore", "wanderlust"
    ],
    "tech": [
        "tech", "technology", "ai", "coding", "programming", "software",
        "developer", "startup"
    ],
    "finance": [
        "finance", "money", "invest", "trading", "crypto", "stocks", "wealth"
    ],
    "food": [
        "food", "recipe", "cooking", "eat", "meal", "delicious", "chef"
    ],
    "education": [
        "education", "learning", "study", "career", "student", "tutorial"
    ],
    "gaming": [
        "gaming", "gamer", "gameplay", "esports", "stream"
    ],
    "lifestyle": [
        "life", "daily", "routine", "vlog", "living", "selfcare"
    ]
}

def clean_text(text):
    text = (text or "").lower()
    text = re.sub(r"http\S+", "", text)   # remove links
    text = re.sub(r"@\w+", "", text)      # remove mentions
    text = re.sub(r"[^\w\s#]", "", text)  # remove punctuation
    return text

def extract_tokens(text):
    hashtags = re.findall(r"#(\w+)", text)
    words = re.findall(r"\b[a-z]{3,}\b", text)
    return hashtags + words

class ContentNLPAnalyzer:
    def __init__(self, profile_data, posts_data):
        self.bio = profile_data.get("bio", "")
        self.posts = posts_data or []

    def build_corpus(self):
        texts = [self.bio]

        for post in self.posts:
            texts.append(post.get("caption", ""))

        cleaned = [clean_text(t) for t in texts]
        tokens = []

        for text in cleaned:
            tokens.extend(extract_tokens(text))

        return tokens

    def keyword_distribution(self):
        tokens = self.build_corpus()
        return Counter(tokens)

    def niche_scores(self):
        token_counts = self.keyword_distribution()
        scores = {}

        for niche, keywords in NICHE_KEYWORDS.items():
            score = sum(token_counts.get(word, 0) for word in keywords)
            scores[niche] = score

        return scores

    def infer_niche(self):
        scores = self.niche_scores()

        sorted_niches = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        primary = sorted_niches[0][0] if sorted_niches and sorted_niches[0][1] > 0 else "general"
        secondary = [
            niche for niche, score in sorted_niches[1:3] if score > 0
        ]

        return {
            "Primary_Niche": primary,
            "Secondary_Niches": secondary,
            "Niche_Scores": scores
        }

    def content_drift(self):
        if not self.posts:
            return {"Early_Niche": None, "Recent_Niche": None, "Drift_Detected": False}

        mid = len(self.posts) // 2

        early_posts = self.posts[:mid]
        recent_posts = self.posts[mid:]

        early_analyzer = ContentNLPAnalyzer(
            {"bio": self.bio}, early_posts
        )
        recent_analyzer = ContentNLPAnalyzer(
            {"bio": self.bio}, recent_posts
        )

        early_niche = early_analyzer.infer_niche().get("Primary_Niche")
        recent_niche = recent_analyzer.infer_niche().get("Primary_Niche")

        drift = early_niche != recent_niche

        return {
            "Early_Niche": early_niche,
            "Recent_Niche": recent_niche,
            "Drift_Detected": drift
        }
