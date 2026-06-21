import numpy as np


def normalize(value, min_val=0, max_val=1):
    if max_val - min_val == 0:
        return 0
    return (value - min_val) / (max_val - min_val)


class EngagementAnalyzer:
    def __init__(self, profile_data, posts_data):
        self.followers = profile_data.get("followers", 0)
        self.posts = posts_data or []

    # -------------------------
    # PLATFORM DETECTION
    # -------------------------

    def detect_platform(self):
        if any(post.get("views") for post in self.posts):
            return "YouTube"

        if self.posts and self.posts[0].get("post_type") == "post":
            return "Reddit"

        return "Instagram"

    # -------------------------
    # CORE METRICS
    # -------------------------

    def _engagement_per_post(self):
        engagement = []
        for post in self.posts:
            likes = post.get("likes", 0)
            comments = post.get("comments", 0)

            # Instagram comment signal is weaker
            if self.detect_platform() == "Instagram":
                total = likes + (0.5 * comments)
            else:
                total = likes + comments

            engagement.append(total)

        return np.array(engagement) if engagement else np.array([0])

    def engagement_rate(self):
        """Follower-based engagement (Instagram / Reddit)"""
        if self.followers == 0:
            return 0.0

        engagement = self._engagement_per_post()
        return float(np.mean(engagement) / self.followers)

    def youtube_engagement_rate(self):
        """View-based engagement (YouTube)"""
        rates = []

        for post in self.posts:
            views = post.get("views")
            if views and views > 0:
                rate = (post.get("likes", 0) + post.get("comments", 0)) / views
                rates.append(rate)

        return float(np.mean(rates)) if rates else 0.0

    def comment_strength_ratio(self):
        ratios = []

        for post in self.posts:
            likes = post.get("likes", 0)
            if likes > 0:
                ratios.append(post.get("comments", 0) / likes)

        return float(np.mean(ratios)) if ratios else 0.0

    def engagement_consistency(self):
        engagement = self._engagement_per_post()

        if np.mean(engagement) == 0:
            return 0.0

        variation = np.std(engagement) / np.mean(engagement)
        return 1 / (1 + variation)

    def engagement_depth(self):
        comments = [post.get("comments", 0) for post in self.posts]
        return float(np.mean(comments)) if comments else 0.0

    # -------------------------
    # FINAL EQS
    # -------------------------

    def compute_eqs(self):
        platform = self.detect_platform()

        # Platform-aware ER
        if platform == "YouTube":
            er = self.youtube_engagement_rate()
        else:
            er = self.engagement_rate()

        csr = self.comment_strength_ratio()
        edf = self.engagement_depth()
        ec = self.engagement_consistency()

        # Normalize
        er_n = normalize(er, 0, 0.10)
        csr_n = normalize(csr, 0, 0.10)
        edf_n = normalize(edf, 0, 500)
        ec_n = normalize(ec, 0, 1)

        eqs = (
            0.40 * er_n +
            0.25 * csr_n +
            0.20 * edf_n +
            0.15 * ec_n
        )

        return {
            "platform": platform,
            "engagement_model": (
                "views-based" if platform == "YouTube"
                else "followers-based (best-effort)" if platform == "Instagram"
                else "followers-based"
            ),
            "EQS": round(eqs, 3),
            "engagement_rate": round(er, 6),
            "comment_strength_ratio": round(csr, 6),
            "engagement_depth": round(edf, 3),
            "engagement_consistency": round(ec, 3)
        }
