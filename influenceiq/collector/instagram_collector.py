import time
import re
from playwright.sync_api import sync_playwright

from influenceiq.collector.base_collector import BaseCollector
from influenceiq.config.settings import get_random_delay


class InstagramCollector(BaseCollector):
    def __init__(self, username):
        self.username = username.strip().lstrip("@")
        self.profile_url = f"https://www.instagram.com/{self.username}/"

    def collect_profile(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )

            page = context.new_page()
            page.goto(self.profile_url, timeout=60000)

            # Allow JS to load
            page.wait_for_timeout(5000)

            # Check for private or unavailable profile
            if page.locator("text=This Account is Private").count() > 0:
                raise ValueError("Private account. Public data only.")

            # Extract profile text from DOM
            html = page.content()

            browser.close()

        return self._parse_profile_from_html(html)

    def collect_posts(self, limit=30):
        # Profile data already parsed in collect_profile
        return self.posts[:limit]

    def _parse_profile_from_html(self, html):
        """
        Extracts profile and post data from rendered HTML.
        This is best-effort and may fail gracefully.
        """

        # Followers / following / posts
        stats = re.findall(r'"edge_followed_by":{"count":(\d+)}', html)
        following = re.findall(r'"edge_follow":{"count":(\d+)}', html)
        total_posts = re.findall(r'"edge_owner_to_timeline_media":{"count":(\d+)}', html)

        if not stats:
            raise ValueError(
                "Unable to extract public Instagram data. "
                "Instagram may be restricting automated access."
            )

        followers = int(stats[0])
        following = int(following[0]) if following else 0
        total_posts = int(total_posts[0]) if total_posts else 0

        # Username & bio
        username_match = re.search(r'"username":"([^"]+)"', html)
        bio_match = re.search(r'"biography":"([^"]*)"', html)

        username = username_match.group(1) if username_match else self.username
        bio = bio_match.group(1).encode("utf-8").decode("unicode_escape") if bio_match else ""

        # Posts (best-effort)
        post_blocks = re.findall(r'"shortcode":"([^"]+)"', html)
        likes_blocks = re.findall(r'"edge_liked_by":{"count":(\d+)}', html)
        comments_blocks = re.findall(r'"edge_media_to_comment":{"count":(\d+)}', html)

        posts = []
        for i in range(min(len(post_blocks), 30)):
            posts.append({
                "post_id": post_blocks[i],
                "post_type": "image",
                "caption": "",
                "hashtags": [],
                "mentions": [],
                "likes": int(likes_blocks[i]) if i < len(likes_blocks) else 0,
                "comments": int(comments_blocks[i]) if i < len(comments_blocks) else 0,
                "views": None,
                "timestamp": None,
                "post_url": f"https://www.instagram.com/p/{post_blocks[i]}/"
            })

        self.posts = posts

        return {
            "username": username,
            "display_name": username,
            "bio": bio,
            "category": None,
            "followers": followers,
            "following": following,
            "total_posts": total_posts,
            "external_links": [],
            "is_verified": False,
            "profile_pic_url": None
        }
