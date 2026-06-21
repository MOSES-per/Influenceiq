from googleapiclient.discovery import build
from influenceiq.collector.base_collector import BaseCollector
from influenceiq.config.settings import YOUTUBE_API_KEY


class YouTubeCollector(BaseCollector):
    def __init__(self, channel_identifier):
        """
        channel_identifier can be:
        - channel ID
        - username
        - channel handle (without @)
        """
        self.channel_identifier = channel_identifier
        self.youtube = build(
            "youtube",
            "v3",
            developerKey=YOUTUBE_API_KEY
        )

    # -------------------------
    # PUBLIC METHODS
    # -------------------------

    def collect_profile(self):
        channel = self._get_channel()
        stats = channel["statistics"]
        snippet = channel["snippet"]

        profile_data = {
            "username": snippet.get("customUrl", self.channel_identifier),
            "display_name": snippet.get("title"),
            "bio": snippet.get("description", ""),
            "category": None,
            "followers": int(stats.get("subscriberCount", 0)),
            "following": None,
            "total_posts": int(stats.get("videoCount", 0)),
            "external_links": [],
            "is_verified": None,
            "profile_pic_url": snippet["thumbnails"]["high"]["url"]
        }

        self.channel_id = channel["id"]
        return profile_data

    def collect_posts(self, limit=30):
        videos = self._get_videos(limit)

        posts = []
        for video in videos:
            stats = video["statistics"]
            snippet = video["snippet"]

            posts.append({
                "post_id": video["id"],
                "post_type": "video",
                "caption": snippet.get("title", ""),
                "hashtags": [],
                "mentions": [],
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "views": int(stats.get("viewCount", 0)),
                "timestamp": snippet.get("publishedAt"),
                "post_url": f"https://www.youtube.com/watch?v={video['id']}"
            })

        return posts

    # -------------------------
    # INTERNAL HELPERS
    # -------------------------

    def _get_channel(self):
        request = self.youtube.search().list(
            part="snippet",
            q=self.channel_identifier,
            type="channel",
            maxResults=1
        )
        response = request.execute()

        if not response["items"]:
            raise ValueError("YouTube channel not found")

        channel_id = response["items"][0]["snippet"]["channelId"]

        channel_request = self.youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        channel_response = channel_request.execute()

        return channel_response["items"][0]

    def _get_videos(self, limit):
        search_request = self.youtube.search().list(
            part="id",
            channelId=self.channel_id,
            order="date",
            maxResults=limit,
            type="video"
        )
        search_response = search_request.execute()

        video_ids = [item["id"]["videoId"] for item in search_response["items"]]

        video_request = self.youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        video_response = video_request.execute()

        return video_response["items"]
