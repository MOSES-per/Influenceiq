import numpy as np

GENERIC_PATTERNS = [
    r"^nice$",
    r"^nice pic$",
    r"^great$",
    r"^awesome$",
    r"^love it$",
    r"^[🔥❤️😍]+$"
]

def is_generic_comment(text):
    text = text.lower().strip()
    for pattern in GENERIC_PATTERNS:
        try:
            if __import__('re').match(pattern, text):
                return True
        except Exception:
            continue
    return False

class AuthenticityAnalyzer:
    def __init__(self, profile_data, posts_data, engagement_metrics):
        self.followers = profile_data.get("followers", 0)
        self.posts = posts_data or []
        self.engagement = engagement_metrics or {}

    def low_engagement_signal(self):
        er = self.engagement.get("engagement_rate", 0)

        if self.followers > 100000 and er < 0.005:
            return 1.0
        if er < 0.01:
            return 0.6
        return 0.0

    def comment_like_signal(self):
        csr = self.engagement.get("comment_strength_ratio", 0)

        if csr < 0.005:
            return 1.0
        if csr < 0.01:
            return 0.5
        return 0.0

    def generic_comment_signal(self):
        # Placeholder until comment text scraping is added
        return 0.0

    def volatility_signal(self):
        consistency = self.engagement.get("engagement_consistency", 0)

        if consistency < 0.3:
            return 1.0
        if consistency < 0.5:
            return 0.5
        return 0.0

    def like_follower_signal(self):
        likes = [post.get("likes", 0) for post in self.posts]
        avg_likes = float(np.mean(likes)) if likes else 0.0

        expected = self.followers * 0.01  # 1% baseline

        if expected == 0:
            return 0.0

        if avg_likes < expected * 0.3:
            return 1.0
        if avg_likes < expected * 0.6:
            return 0.5
        return 0.0

    def compute_authenticity(self):
        signals = {
            "low_engagement": self.low_engagement_signal(),
            "comment_like_imbalance": self.comment_like_signal(),
            "volatility": self.volatility_signal(),
            "like_follower_anomaly": self.like_follower_signal(),
            "generic_comments": self.generic_comment_signal()
        }

        score = float(np.mean(list(signals.values())))

        if score < 0.3:
            level = "LOW RISK"
        elif score < 0.6:
            level = "MEDIUM RISK"
        else:
            level = "HIGH RISK"

        return {
            "Authenticity_Index": round(1 - score, 3),
            "Risk_Level": level,
            "Signals": signals,
            "Confidence": round(1 - float(np.std(list(signals.values()))), 3)
        }
