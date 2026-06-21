import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path

from influenceiq.collector.reddit_collector import RedditCollector
from influenceiq.collector.youtube_collector import YouTubeCollector

from influenceiq.analytics.engagement import EngagementAnalyzer
from influenceiq.analytics.authenticity import AuthenticityAnalyzer
from influenceiq.analytics.content_nlp import ContentNLPAnalyzer
from influenceiq.scoring.score_engine import ScoreEngine
from influenceiq.reports.exporter import export_csv, export_pdf


# -------------------------
# PLATFORM BADGES
# -------------------------
PLATFORM_BADGES = {
    "YouTube": "🔴 YouTube (Live API)",
    "Reddit": "🟠 Reddit (Public Data)",
    "Instagram (Sample / CSV)": "🟣 Instagram (Restricted / Sample)"
}

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="InfluenceIQ",
    page_icon="📊",
    layout="wide"
)

st.title("📊 InfluenceIQ – Multi-Platform Influencer Intelligence")
st.caption(
    "Analyze creators using engagement quality, authenticity heuristics, "
    "and audience intelligence across platforms."
)

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.header("🔍 Analyze Influencer")

    platform = st.selectbox(
        "Platform",
        ["YouTube", "Reddit", "Instagram (Sample / CSV)"]
    )

    username = st.text_input(
        "Creator Identifier",
        help="YouTube: channel | Reddit: username | Instagram: optional"
    )

    post_limit = st.slider("Number of posts to analyze", 5, 50, 20)

    uploaded_csv = None
    if platform == "Instagram (Sample / CSV)":
        uploaded_csv = st.file_uploader(
            "Upload Instagram CSV (optional)",
            type=["csv"]
        )

        template_path = Path("influenceiq/sample_data/instagram_template.csv")
        if template_path.exists():
            with open(template_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Instagram CSV Template",
                    f,
                    "instagram_template.csv",
                    "text/csv"
                )

    analyze_btn = st.button("Run Analysis")

# -------------------------
# MAIN LOGIC
# -------------------------
if analyze_btn:
    with st.spinner("Collecting and analyzing data..."):
        try:
            # -------------------------
            # DATA COLLECTION
            # -------------------------
            if platform == "YouTube":
                collector = YouTubeCollector(username)
                raw = collector.collect_all(limit=post_limit)
                profile, posts = raw["profile_data"], raw["posts_data"]

            elif platform == "Reddit":
                collector = RedditCollector(username)
                raw = collector.collect_all(limit=post_limit)
                profile, posts = raw["profile_data"], raw["posts_data"]

            else:
                st.info(
                    "Instagram live data access is restricted. "
                    "Using sample or uploaded data."
                )

                if uploaded_csv:
                    df = pd.read_csv(uploaded_csv)

                    posts = [{
                        "post_type": "image",
                        "likes": int(r.get("likes", 0)),
                        "comments": int(r.get("comments", 0)),
                        "views": None
                    } for _, r in df.iterrows()]

                    profile = {
                        "username": "uploaded_instagram_creator",
                        "followers": int(df["followers"].iloc[0]),
                        "following": None,
                        "bio": "Instagram dataset uploaded via CSV",
                        "total_posts": len(posts),
                        "is_verified": False
                    }
                else:
                    with open("influenceiq/sample_data/instagram_sample.json") as f:
                        raw = json.load(f)
                    profile, posts = raw["profile_data"], raw["posts_data"]

            # -------------------------
            # PLATFORM BADGE
            # -------------------------
            st.markdown(f"## {PLATFORM_BADGES[platform]}")

            # -------------------------
            # ANALYTICS
            # -------------------------
            eqs = EngagementAnalyzer(profile, posts).compute_eqs()
            auth = AuthenticityAnalyzer(profile, posts, eqs).compute_authenticity()
            nlp = ContentNLPAnalyzer(profile, posts).infer_niche()
            iis = ScoreEngine(eqs, auth, nlp).compute_iis()

            # -------------------------
            # REPORTS UI (RESTORED)
            # -------------------------
            st.subheader("👤 Influencer Overview")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Followers", profile.get("followers"))
            col2.metric("Following", profile.get("following"))
            col3.metric("Total Posts", profile.get("total_posts"))
            col4.metric("Verified", "Yes" if profile.get("is_verified") else "No")
            st.write(profile.get("bio"))

            st.subheader("📈 Engagement & Authenticity")
            col1, col2, col3 = st.columns(3)
            col1.metric("Engagement Quality Score (EQS)", eqs["EQS"])
            col2.metric("Authenticity Index", auth["Authenticity_Index"])
            col3.metric("Risk Level", auth["Risk_Level"])

            engagement_values = [
                post.get("likes", 0) + post.get("comments", 0)
                for post in posts
            ]

            if engagement_values:
                fig, ax = plt.subplots()
                ax.plot(engagement_values, marker="o")
                ax.set_title("Engagement per Post")
                ax.set_xlabel("Post Index")
                ax.set_ylabel("Total Engagement")
                st.pyplot(fig)

            st.subheader("🧠 Audience & Content Intelligence")
            st.metric("Primary Niche", nlp["Primary_Niche"])
            st.write(
                "Secondary Niches:",
                ", ".join(nlp.get("Secondary_Niches", [])) or "None"
            )

            niche_scores = nlp.get("Niche_Scores", {})
            if niche_scores:
                niche_df = (
                    pd.DataFrame(niche_scores.items(), columns=["Niche", "Score"])
                    .sort_values("Score", ascending=False)
                )
                st.bar_chart(niche_df.set_index("Niche"))

            st.subheader("🎯 Final Decision")
            col1, col2 = st.columns(2)
            col1.metric(
                "Influencer Intelligence Score (IIS)",
                iis["Influencer_Intelligence_Score"]
            )
            col2.metric("Verdict", iis["Verdict"])
            st.json(iis["Score_Breakdown"])

            # -------------------------
            # EXPORTS (FIXED & WORKING)
            # -------------------------
            st.subheader("📄 Export Report")

            csv_buffer = export_csv(profile, eqs, auth, nlp, iis)
            st.download_button(
                "⬇️ Download CSV Report",
                csv_buffer,
                "influenceiq_report.csv",
                "text/csv"
            )

            pdf_buffer = export_pdf(profile, eqs, auth, nlp, iis)
            st.download_button(
                "⬇️ Download PDF Report",
                pdf_buffer,
                "influenceiq_report.pdf",
                "application/pdf"
            )

        except Exception as e:
            st.error("Error during analysis")
            st.code(str(e))
