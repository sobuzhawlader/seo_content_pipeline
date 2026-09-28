# Autonomous SEO Content Pipeline

An end-to-end autonomous, production-grade SEO agent pipeline built in Python with Google Gemini 2.5 Flash, Serper API, and Streamlit.

## 🌟 Key Features

1. **SERP & Competitor Intelligence (`agents/research_agent.py`):**
   - Fetches live Google SERP results via Serper API.
   - Extracts top 7 competitor snippets, People Also Ask (PAA) questions, and related queries.

2. **Topical Authority & Semantic Clustering (`agents/topical_mapper.py`):**
   - Discovers Pillar Page opportunities and creates 4–6 supporting cluster articles.

3. **Iterative Section-by-Section Writer (`agents/section_writer.py`):**
   - Chained sequential section drafting (400–600 words/section) to reach 2,000+ words of technical depth.
   - Preserves running context across headings.
   - Generates FAQ section + valid Schema.org `FAQPage` JSON-LD markup.
   - Automatically injects internal links from published articles.

4. **Two-Step Fact-Checking & Grounding (`agents/fact_checker.py`):**
   - Step 1: Real-time Google Search Grounding to audit claims, statistics, and dates.
   - Step 2: Formats audited article into clean, structured JSON without API conflict.

5. **Media Pipeline (`agents/media_agent.py`):**
   - Automatic Unsplash image search.
   - Binary upload to WordPress Media Library with dynamic alt-text.

6. **Multi-CMS Universal Publisher (`publishers/`):**
   - WordPress REST API with Yoast SEO (`_yoast_wpseo_metadesc`, `_yoast_wpseo_focuskw`) and Rank Math support.
   - Custom Webhook dispatcher with Bearer token authentication.

7. **Streamlit Visual Control Center (`app.py`):**
   - Tab 1: Keyword Input & Background Pipeline Execution.
   - Tab 2: Topical Authority Map & Cluster Discovery.
   - Tab 3: Real-Time Pipeline Progress Tracker.
   - Tab 4: Content Review & Fact-Checked Diff Editor.
   - Tab 5: One-Click Multi-CMS Publishing (Human-in-the-Loop).

---

## 📁 Directory Structure

```
seo_content_pipeline/
├── core/
│   ├── __init__.py
│   ├── models.py              # Pydantic data schemas
│   └── database.py            # SQLite & SQLModel database state
├── agents/
│   ├── __init__.py
│   ├── research_agent.py      # Serper API integration
│   ├── topical_mapper.py      # Semantic pillar/cluster builder
│   ├── brief_agent.py         # Content brief generator
│   ├── section_writer.py      # 2000+ words section-by-section engine
│   ├── fact_checker.py        # Two-step Google Search Grounding
│   └── media_agent.py         # Unsplash image & WP media upload
├── publishers/
│   ├── __init__.py
│   ├── base.py                # Abstract Base Class for publishers
│   ├── wordpress.py           # WP REST API (Post + Media + SEO metadata)
│   └── custom_site.py         # Custom Webhook adapter
├── tasks/
│   ├── __init__.py
│   └── worker.py              # Background ThreadPool queue & link filtering
├── config.py                  # Environment config loader
├── app.py                     # Streamlit Visual Control Center
├── requirements.txt           # Dependencies
└── .env.example               # Environment variables template
```

---

## 🚀 Quickstart Guide

### 1. Set Up Environment

```bash
cd /Users/md.sobuj/.gemini/antigravity/scratch/seo_content_pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Required:
- `GEMINI_API_KEY`: Google AI Studio API key
- `SERPER_API_KEY`: Serper API key (for Google SERP scraping)
- `UNSPLASH_CLIENT_ID`: (Optional) for automated featured images

### 3. Launch Control Center

```bash
streamlit run app.py
```
