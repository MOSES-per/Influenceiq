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

### 1. Open the project

```bash
cd C:\Users\moses\influenceiq
```

### 2. Create the virtual environment (once)

InfluenceIQ uses a Python virtual environment named `venv`. It isolates this project's Python packages from the system Python installation and other projects.

```bash
python -m venv venv
```

### 3. Activate it (Windows)

```bash
venv\Scripts\activate
```

You should see `(venv)` at the beginning of the terminal prompt.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the dashboard

From the project root, use:

```bash
streamlit run influenceiq/dashboard/app.py
```

> **Important:** Do not use `streamlit run dashboard/app.py` from the project root.

The dashboard normally runs at `http://localhost:8501`.

### 6. Run the project later

The environment only needs to be created once. On later runs:

```bash
cd C:\Users\moses\influenceiq
venv\Scripts\activate
streamlit run influenceiq/dashboard/app.py
```

### 7. Stop and deactivate

Stop Streamlit with `Ctrl+C`, then optionally run:

```bash
deactivate
```

## Project Structure

```text
influenceiq/
├── influenceiq/
│   ├── collector/
│   ├── analytics/
│   ├── scoring/
│   ├── reports/
│   ├── storage/
│   ├── dashboard/
│   └── sample_data/
├── requirements.txt
├── README.md
└── venv/
```

### Main components

- `collector/` – platform data acquisition
- `analytics/` – engagement, authenticity, and NLP analysis
- `scoring/` – IIS calculation
- `reports/` – CSV/PDF reporting
- `storage/` – JSON and SQLite storage
- `dashboard/` – Streamlit UI
- `sample_data/` – Instagram sample data and CSV template
- `requirements.txt` – Python dependencies
- `venv/` – local Python virtual environment; normally not committed to Git

