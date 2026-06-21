class BaseCollector:
    """Base class for all platform collectors.
    Enforces a common interface.
    """

    def collect_profile(self):
        raise NotImplementedError("collect_profile() not implemented")

    def collect_posts(self, limit=30):
        raise NotImplementedError("collect_posts() not implemented")

    def collect_all(self, limit=30):
        """Collects profile + posts together."""
        return {
            "profile_data": self.collect_profile(),
            "posts_data": self.collect_posts(limit)
        }
