from collector.instagram_collector import InstagramCollector
from analytics.engagement import EngagementAnalyzer
from analytics.authenticity import AuthenticityAnalyzer
from analytics.content_nlp import ContentNLPAnalyzer
from scoring.score_engine import ScoreEngine
from storage.raw_store import RawJSONStore, RawSQLiteStore

if __name__ == "__main__":
    username = "instagram"  # change to a public username for testing

    collector = InstagramCollector(username)
    collected_data = collector.collect_all(limit=10)

    # Add collection metadata
    collected_data["collection_metadata"] = {
        "platform": "instagram",
        "username": username
    }

    # Save as JSON
    json_store = RawJSONStore()
    json_path = json_store.save("instagram", username, collected_data)

    # Save to SQLite
    sqlite_store = RawSQLiteStore()
    sqlite_store.save("instagram", username, collected_data)

    profile = collected_data["profile_data"]
    posts = collected_data["posts_data"]

    eqs_result = EngagementAnalyzer(profile, posts).compute_eqs()
    auth_result = AuthenticityAnalyzer(profile, posts, eqs_result).compute_authenticity()
    nlp_result = ContentNLPAnalyzer(profile, posts).infer_niche()

    score_engine = ScoreEngine(eqs_result, auth_result, nlp_result)
    iis = score_engine.compute_iis()

    print("IIS:", iis)
