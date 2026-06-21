# InfluenceIQ

InfluenceIQ is a cross-platform influencer intelligence engine that analyzes public social media data to compute **engagement quality, authenticity, content consistency, audience alignment**, and **platform confidence** — then combines these into an explainable **Influencer Intelligence Score (IIS)**.

The system is designed to be **ethical, platform-aware, and explainable**, prioritizing analytics quality over aggressive data scraping.

---

## Key Features

- **Engagement Quality Score (EQS)**
  - Follower-based and view-based engagement models
- **Authenticity Analysis**
  - Detects suspicious engagement patterns and bot-like behavior
- **Audience & Content Intelligence**
  - NLP-based niche detection and alignment scoring
- **Platform Confidence Score**
  - Quantifies reliability of platform data (YouTube > Reddit > Instagram)
- **Influencer Intelligence Score (IIS)**
  - Weighted, explainable final score with breakdown
- **Compare Two Creators**
  - Side-by-side comparison across all scores
- **Interactive Dashboard**
  - Expand / collapse report sections
- **CSV & PDF Reports**
  - Downloadable, shareable influencer reports

---

## Supported Platforms

| Platform | Data Access | Confidence |
|--------|------------|------------|
| YouTube | Official API | High |
| Reddit | Public JSON | Medium |
| Instagram | Sample / CSV | Limited |

> Instagram live scraping is intentionally restricted due to platform limitations.  
> InfluenceIQ supports Instagram analysis via **sample datasets or uploaded CSV files** to ensure stability and ethical use.

---

## Architecture Overview

+------------------+

Platform Collectors
YouTube API
Reddit JSON
Instagram CSV
+--------+---------+

markdown
Copy code
     |
     v
+------------------+

Analytics Layer
Engagement (EQS)
Authenticity
NLP / Niche
Confidence Score
+--------+---------+

markdown
Copy code
     |
     v
+------------------+

Scoring Engine
IIS Computation
Score Breakdown
+--------+---------+

markdown
Copy code
     |
     v
+------------------+

Streamlit UI
Single / Compare
Expandable Views
Visual Analytics
+--------+---------+

markdown
Copy code
     |
     v
+------------------+

Reports
CSV Export
PDF Export
+------------------+

yaml
Copy code

---

## Quick Start

1. Create a virtual environment and install requirements:
   ```bash
   pip install -r requirements.txt
Run the Streamlit dashboard:

bash
Copy code
streamlit run dashboard/app.py
Project Structure
collector/ – Platform data acquisition modules

analytics/ – Engagement, authenticity, NLP, confidence scoring

storage/ – Raw JSON and SQLite storage

scoring/ – Influencer Intelligence Score (IIS) engine

reports/ – CSV and PDF export logic

dashboard/ – Streamlit user interface

main.py – Sample pipeline runner

Design Principles
Explainability over black-box scoring

Ethical handling of restricted platforms

Separation of concerns

Analytics-first, scraping-second

Notes
Only public data is analyzed.

Instagram analysis is non-live by design.

This project is intended for research, analytics, and evaluation, not surveillance.