import requests
from influenceiq.collector.base_collector import BaseCollector


class RedditCollector(BaseCollector):
    def __init__(self, username):
        self.username = username.strip().lstrip("u/")

    def collect_profile(self):
        url = f"https://www.reddit.com/user/{self.username}/about.json"
        headers = {"User-Agent": "InfluenceIQ/1.0"}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError("Reddit user not found or unavailable")

        data = response.json()["data"]

        profile_data = {
            "username": self.username,
            "display_name": self.username,
            "bio": data.get("subreddit", {}).get("public_description", ""),
            "category": None,
            "followers": data.get("subscribers", 0),
            "following": None,
            "total_posts": data.get("total_karma", 0),
            "external_links": [],
            "is_verified": False,
            "profile_pic_url": data.get("icon_img")
        }

        return profile_data

    def collect_posts(self, limit=30):
        url = f"https://www.reddit.com/user/{self.username}/submitted.json?limit={limit}"
        headers = {"User-Agent": "InfluenceIQ/1.0"}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []

        items = response.json()["data"]["children"]

        posts = []
        for item in items:
            data = item["data"]

            posts.append({
                "post_id": data.get("id"),
                "post_type": "post",
                "caption": data.get("title", ""),
                "hashtags": [],
                "mentions": [],
                "likes": data.get("ups", 0),
                "comments": data.get("num_comments", 0),
                "views": None,
                "timestamp": data.get("created_utc"),
                "post_url": f"https://reddit.com{data.get('permalink')}"
            })

        return posts
