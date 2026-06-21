import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# -------------------------
# CSV EXPORT (IN-MEMORY)
# -------------------------
def export_csv(profile, eqs, auth, nlp, iis):
    data = []

    # Profile
    data.append(["Profile", "Username", profile.get("username")])
    data.append(["Profile", "Followers", profile.get("followers")])
    data.append(["Profile", "Following", profile.get("following")])
    data.append(["Profile", "Verified", profile.get("is_verified")])
    data.append(["Profile", "Bio", profile.get("bio")])

    # Engagement
    data.append(["Engagement", "EQS", eqs.get("EQS")])
    data.append(["Engagement", "Engagement Rate", eqs.get("engagement_rate")])
    data.append(["Engagement", "Comment Strength", eqs.get("comment_strength_ratio")])
    data.append(["Engagement", "Consistency", eqs.get("engagement_consistency")])

    # Authenticity
    data.append(["Authenticity", "Authenticity Index", auth.get("Authenticity_Index")])
    data.append(["Authenticity", "Risk Level", auth.get("Risk_Level")])
    for k, v in auth.get("Signals", {}).items():
        data.append(["Authenticity Signal", k, v])

    # Audience
    data.append(["Audience", "Primary Niche", nlp.get("Primary_Niche")])
    data.append(["Audience", "Secondary Niches", ", ".join(nlp.get("Secondary_Niches", []))])
    for niche, score in nlp.get("Niche_Scores", {}).items():
        data.append(["Niche Score", niche, score])

    # Final
    data.append(["Final", "IIS", iis.get("Influencer_Intelligence_Score")])
    data.append(["Final", "Verdict", iis.get("Verdict")])

    df = pd.DataFrame(data, columns=["Section", "Metric", "Value"])

    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return buffer


# -------------------------
# PDF EXPORT (IN-MEMORY)
# -------------------------
def export_pdf(profile, eqs, auth, nlp, iis):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    def heading(text):
        elements.append(Paragraph(f"<b>{text}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))

    def line(text):
        elements.append(Paragraph(text, styles["Normal"]))
        elements.append(Spacer(1, 8))

    heading("InfluenceIQ – Influencer Intelligence Report")

    heading("Influencer Overview")
    line(f"Username: {profile.get('username')}")
    line(f"Followers: {profile.get('followers')}")
    line(f"Following: {profile.get('following')}")
    line(f"Verified: {profile.get('is_verified')}")
    line(f"Bio: {profile.get('bio')}")

    heading("Engagement Analytics")
    line(f"EQS: {eqs.get('EQS')}")
    line(f"Engagement Rate: {eqs.get('engagement_rate')}")
    line(f"Comment Strength: {eqs.get('comment_strength_ratio')}")
    line(f"Consistency: {eqs.get('engagement_consistency')}")

    heading("Authenticity Analysis")
    line(f"Authenticity Index: {auth.get('Authenticity_Index')}")
    line(f"Risk Level: {auth.get('Risk_Level')}")
    for k, v in auth.get("Signals", {}).items():
        line(f"{k}: {v}")

    heading("Audience & Content Intelligence")
    line(f"Primary Niche: {nlp.get('Primary_Niche')}")
    line(f"Secondary Niches: {', '.join(nlp.get('Secondary_Niches', [])) or 'None'}")
    for niche, score in nlp.get("Niche_Scores", {}).items():
        line(f"{niche}: {score}")

    heading("Final Verdict")
    line(f"IIS: {iis.get('Influencer_Intelligence_Score')}")
    line(f"Recommendation: {iis.get('Verdict')}")

    doc.build(elements)
    buffer.seek(0)

    return buffer
