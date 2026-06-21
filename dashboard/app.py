import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from influenceiq.collector.instagram_collector import InstagramCollector
from influenceiq.analytics.engagement import EngagementAnalyzer
from influenceiq.analytics.authenticity import AuthenticityAnalyzer
from influenceiq.analytics.content_nlp import ContentNLPAnalyzer
from influenceiq.scoring.score_engine import ScoreEngine
from influenceiq.reports.exporter import export_csv, export_pdf



st.set_page_config(
    page_title="InfluenceIQ",
    page_icon="📊",
    layout="wide"
)

st.title("📊 InfluenceIQ – Influencer Intelligence Dashboard")
st.caption("Analyze public creator data using engagement, authenticity, and audience intelligence")

with st.sidebar:
    st.header("🔍 Analyze Influencer")
    username = st.text_input("Instagram Username", "")
    post_limit = st.slider("Number of posts to analyze", 10, 50, 30)
    analyze_btn = st.button("Run Analysis")

if analyze_btn and username:
    with st.spinner("Collecting and analyzing public data..."):
        try:
            collector = InstagramCollector(username)
            raw_data = collector.collect_all(limit=post_limit)

            profile = raw_data.get("profile_data", {})
            posts = raw_data.get("posts_data", [])

            # Analytics
            eqs = EngagementAnalyzer(profile, posts).compute_eqs()
            auth = AuthenticityAnalyzer(profile, posts, eqs).compute_authenticity()
            nlp = ContentNLPAnalyzer(profile, posts).infer_niche()

            iis = ScoreEngine(eqs, auth, nlp).compute_iis()

            # Show results
            st.subheader("👤 Influencer Overview")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Followers", profile.get("followers"))
            col2.metric("Following", profile.get("following"))
            col3.metric("Total Posts", profile.get("total_posts"))
            col4.metric("Verified", "Yes" if profile.get("is_verified") else "No")
            st.write(profile.get("bio"))

            st.subheader("📈 Engagement & Authenticity")
            col1, col2, col3 = st.columns(3)
            col1.metric("Engagement Quality Score", eqs.get("EQS"))
            col2.metric("Authenticity Index", auth.get("Authenticity_Index"))
            col3.metric("Risk Level", auth.get("Risk_Level"))

            engagement_values = [post.get("likes",0) + post.get("comments",0) for post in posts]
            fig, ax = plt.subplots()
            ax.plot(engagement_values, marker="o")
            ax.set_title("Engagement per Post")
            ax.set_xlabel("Post Index")
            ax.set_ylabel("Total Engagement")
            st.pyplot(fig)

            st.subheader("🧠 Audience & Content Intelligence")
            st.metric("Primary Niche", nlp.get("Primary_Niche"))
            st.write("Secondary Niches:", ", ".join(nlp.get("Secondary_Niches") or []))
            niche_df = pd.DataFrame(nlp.get("Niche_Scores", {}).items(), columns=["Niche", "Score"]).sort_values("Score", ascending=False)
            if not niche_df.empty:
                st.bar_chart(niche_df.set_index("Niche"))

            st.subheader("🎯 Final Decision")
            col1, col2 = st.columns(2)
            col1.metric("Influencer Intelligence Score (IIS)", iis.get("Influencer_Intelligence_Score"))
            col2.metric("Verdict", iis.get("Verdict"))
            st.json(iis.get("Score_Breakdown"))

            st.subheader("📄 Export Report")
            if st.button("Download CSV Report"):
                csv_path = export_csv(profile, eqs, auth, nlp, iis)
                st.success(f"CSV saved to {csv_path}")

            if st.button("Download PDF Report"):
                pdf_path = export_pdf(profile, eqs, auth, nlp, iis)
                st.success(f"PDF saved to {pdf_path}")

        except Exception as e:
            st.error(f"Error during analysis: {e}")
