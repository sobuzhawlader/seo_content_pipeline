import streamlit as st
import json
import os
from datetime import datetime
from core.database import init_db, engine, TopicNode, ArticleContent, Session
from tasks.worker import executor, background_generation_pipeline
from agents.topical_mapper import build_topical_cluster_map
from agents.media_agent import MediaAgent
from publishers.wordpress import WordPressPublisher
from publishers.custom_site import CustomSitePublisher
import config

init_db()

st.set_page_config(
    page_title="SEOForge AI — Autonomous Content Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- WORLD-CLASS CUSTOM CSS -----------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Background gradient styling */
.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Glassmorphism Header Banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.12) 50%, rgba(236, 72, 153, 0.08) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hero-title {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    margin: 0;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 14px;
    margin-top: 4px;
    font-weight: 500;
}

.badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 9999px;
    color: #A5B4FC;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* KPI Metric Cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}

.metric-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 18px 20px;
    transition: all 0.25s ease;
}

.metric-card:hover {
    border-color: rgba(99, 102, 241, 0.35);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px -4px rgba(99, 102, 241, 0.15);
}

.metric-label {
    font-size: 13px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.1;
}

/* Modern Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(255, 255, 255, 0.02);
    padding: 8px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 14px;
    border: none;
    color: #94A3B8;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}

/* Card Containers */
.ui-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}

.pillar-box {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.04) 100%);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 16px;
    padding: 22px;
    margin-top: 14px;
}

/* Status Badges */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 700;
    text-transform: capitalize;
}

.status-pending { background: rgba(234, 179, 8, 0.15); color: #FACC15; border: 1px solid rgba(234, 179, 8, 0.3); }
.status-processing { 
    background: rgba(59, 130, 246, 0.15); 
    color: #60A5FA; 
    border: 1px solid rgba(59, 130, 246, 0.3);
    animation: pulse 2s infinite;
}
.status-drafted { background: rgba(168, 85, 247, 0.15); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
.status-published { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
.status-failed { background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }

@keyframes pulse {
    0% { opacity: 0.7; }
    50% { opacity: 1; }
    100% { opacity: 0.7; }
}

/* Primary Button Styling */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: #FFFFFF;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    padding: 10px 24px;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.25);
}

div.stButton > button:first-child:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #0B0F17;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 16px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 16px;
}

.brand-text {
    font-size: 18px;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.3px;
}

.brand-badge {
    background: linear-gradient(135deg, #6366F1, #EC4899);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    color: #FFFFFF;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------- SIDEBAR: API Keys & System Health -----------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size: 24px;">⚡</div>
        <div>
            <div class="brand-text">SEOForge AI <span class="brand-badge">PRO</span></div>
            <div style="font-size: 11px; color: #64748B;">Autonomous Production Pipeline</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔑 API Credentials")
    
    gemini_key = st.text_input(
        "Google Gemini API Key",
        value=config.GEMINI_API_KEY,
        type="password",
        help="Core generation engine (Gemini 2.5 Flash + Search Grounding)"
    )
    serper_key = st.text_input(
        "Serper.dev API Key",
        value=config.SERPER_API_KEY,
        type="password",
        help="Real-time Google SERP, competitor headings & PAA scraping"
    )
    unsplash_key = st.text_input(
        "Unsplash Client ID",
        value=config.UNSPLASH_CLIENT_ID,
        type="password",
        help="Automated editorial stock image sourcing (optional)"
    )
    
    st.divider()
    
    # Engine Status Indicators
    st.caption("SYSTEM ARCHITECTURE STATUS")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if gemini_key:
            st.markdown("🟢 **Gemini AI**: Ready")
        else:
            st.markdown("🔴 **Gemini AI**: Unset")
    with col_k2:
        if serper_key:
            st.markdown("🟢 **SERP Engine**: Live")
        else:
            st.markdown("🟡 **SERP Engine**: Fallback")
            
    st.markdown("""
    <div style="font-size: 11px; color: #475569; margin-top: 16px;">
        Model: <code>gemini-2.5-flash</code><br>
        Grounding: Google Search Tool<br>
        CMS Adapters: WordPress & Webhooks
    </div>
    """, unsafe_allow_html=True)

# ----------------- TOP BANNER & METRICS -----------------
with Session(engine) as session:
    total_topics = session.query(TopicNode).count()
    processing_count = session.query(TopicNode).filter(TopicNode.status == "processing").count()
    drafted_count = session.query(TopicNode).filter(TopicNode.status == "drafted").count()
    published_count = session.query(TopicNode).filter(TopicNode.status == "published").count()

st.markdown("""
<div class="hero-banner">
    <div>
        <h1 class="hero-title">Autonomous SEO Content Pipeline</h1>
        <div class="hero-subtitle">Production-grade AI agent orchestration from SERP intelligence to published authority content.</div>
    </div>
    <div class="badge-tag">
        <span>⚡ 2.5 Flash Grounded</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top KPI Metric Cards
st.markdown(f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-label">Target Keywords</div>
        <div class="metric-value">{total_topics}</div>
    </div>
    <div class="metric-card" style="border-color: rgba(59, 130, 246, 0.3);">
        <div class="metric-label" style="color: #60A5FA;">Active Processing</div>
        <div class="metric-value" style="color: #60A5FA;">{processing_count}</div>
    </div>
    <div class="metric-card" style="border-color: rgba(168, 85, 247, 0.3);">
        <div class="metric-label" style="color: #C084FC;">Ready for Review</div>
        <div class="metric-value" style="color: #C084FC;">{drafted_count}</div>
    </div>
    <div class="metric-card" style="border-color: rgba(16, 185, 129, 0.3);">
        <div class="metric-label" style="color: #34D399;">Published Live</div>
        <div class="metric-value" style="color: #34D399;">{published_count}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- 5 CORE TABS -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 1. Keyword Engine",
    "🗺️ 2. Topical Clusters",
    "⚡ 3. Pipeline Monitor",
    "✍️ 4. Editorial Studio",
    "🚀 5. Universal Publisher"
])

# ----------------- TAB 1: KEYWORD ENGINE -----------------
with tab1:
    st.subheader("Enqueue New Target Topic")
    st.markdown("Input any target seed keyword or search query. The agent will fetch competitor SERPs, generate a structured brief, write an exhaustive 2,000+ word article, and fact-check with Google Search.")
    
    col_input, col_action = st.columns([3, 1])
    with col_input:
        topic_title = st.text_input(
            "Primary Target Keyword / Search Query:",
            placeholder="e.g. Best Autonomous AI Agent Frameworks for Developers 2026",
            label_visibility="collapsed"
        )
    with col_action:
        enqueue_btn = st.button("🚀 Enqueue Generation", use_container_width=True)

    if enqueue_btn:
        if not topic_title.strip():
            st.toast("⚠️ Please enter a target keyword or topic title.", icon="⚠️")
        elif not gemini_key.strip():
            st.error("Please provide your Google Gemini API Key in the left sidebar.")
        else:
            with Session(engine) as session:
                node = TopicNode(title=topic_title.strip(), status="pending")
                session.add(node)
                session.commit()
                session.refresh(node)
                executor.submit(
                    background_generation_pipeline,
                    node.id,
                    serper_key.strip() or None,
                    unsplash_key.strip() or None,
                    gemini_key.strip() or None
                )
            st.success(f"Enqueued **'{topic_title}'** for autonomous execution! Track progress in Tab 3.")
            st.toast("Task successfully added to execution queue!", icon="✅")

# ----------------- TAB 2: TOPICAL CLUSTERS -----------------
with tab2:
    st.subheader("Topical Authority Map & Cluster Discovery")
    st.markdown("Discover the high-ranking **Pillar Page** and 4–6 supporting **Subtopic Clusters** for any broad niche to dominate topical authority.")
    
    niche_col, map_btn_col = st.columns([3, 1])
    with niche_col:
        niche_input = st.text_input(
            "Broad Niche / Seed Subject:",
            placeholder="e.g. Generative AI for Enterprise SEO",
            label_visibility="collapsed"
        )
    with map_btn_col:
        gen_map_btn = st.button("🗺️ Build Topical Map", use_container_width=True)

    if gen_map_btn:
        if not niche_input.strip():
            st.warning("Please specify a seed niche subject.")
        elif not gemini_key.strip():
            st.error("Please configure your Gemini API Key in the sidebar.")
        else:
            with st.spinner("Analyzing semantic hierarchy and competitor graphs..."):
                try:
                    cluster_data = build_topical_cluster_map(niche_input.strip(), api_key=gemini_key.strip())
                    
                    pillar = cluster_data.get("pillar_page", {})
                    st.markdown(f"""
                    <div class="pillar-box">
                        <div style="font-size: 12px; font-weight: 700; color: #818CF8; text-transform: uppercase; letter-spacing: 0.5px;">👑 Core Pillar Page</div>
                        <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin: 6px 0;">{pillar.get('title')}</div>
                        <div style="font-size: 13px; color: #94A3B8;">Primary Keyword: <code>{pillar.get('primary_keyword')}</code> &nbsp;•&nbsp; Intent: <strong>{pillar.get('search_intent')}</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### 🔗 Supporting Cluster Articles")
                    clusters = cluster_data.get("clusters", [])
                    for i, c in enumerate(clusters):
                        with st.container():
                            col_c_text, col_c_action = st.columns([3, 1])
                            with col_c_text:
                                st.markdown(f"""
                                <div style="background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;">
                                    <div style="font-weight: 600; color: #F1F5F9;">{i+1}. {c.get('title')}</div>
                                    <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Target Subtopic: <em>{c.get('target_subtopic')}</em> &nbsp;|&nbsp; Suggested Anchor: <code>{c.get('anchor_text_suggestion')}</code></div>
                                </div>
                                """, unsafe_allow_html=True)
                            with col_c_action:
                                if st.button(f"⚡ Enqueue Cluster #{i+1}", key=f"cluster_enq_{i}"):
                                    with Session(engine) as session:
                                        node = TopicNode(title=c.get('title'), status="pending")
                                        session.add(node)
                                        session.commit()
                                        session.refresh(node)
                                        executor.submit(
                                            background_generation_pipeline,
                                            node.id,
                                            serper_key.strip() or None,
                                            unsplash_key.strip() or None,
                                            gemini_key.strip() or None
                                        )
                                    st.success(f"Enqueued #{i+1}!")
                except Exception as e:
                    st.error(f"Topical mapping failed: {str(e)}")

# ----------------- TAB 3: PIPELINE MONITOR -----------------
with tab3:
    col_header, col_refresh = st.columns([3, 1])
    with col_header:
        st.subheader("Real-Time Execution Monitor")
    with col_refresh:
        if st.button("🔄 Refresh Pipeline", use_container_width=True):
            st.rerun()

    with Session(engine) as session:
        topics = session.query(TopicNode).order_by(TopicNode.id.desc()).all()
        if not topics:
            st.info("No pipeline jobs running. Enqueue a keyword in Tab 1 to see real-time updates.")
        else:
            for t in topics:
                badge_class = f"status-{t.status}"
                status_label = {
                    "pending": "⏳ Pending in Queue",
                    "processing": "⚙️ Generating (SERP + Writing)",
                    "drafted": "✅ Drafted (Ready)",
                    "published": "🌐 Published Live",
                    "failed": "❌ Pipeline Error"
                }.get(t.status, t.status)
                
                with st.container():
                    col_t_id, col_t_title, col_t_badge, col_t_link = st.columns([1, 4, 3, 2])
                    col_t_id.markdown(f"<span style='color: #64748B; font-weight: 700;'>#{t.id}</span>", unsafe_allow_html=True)
                    col_t_title.markdown(f"**{t.title}**")
                    col_t_badge.markdown(f"<span class='status-pill {badge_class}'>{status_label}</span>", unsafe_allow_html=True)
                    if t.live_url:
                        col_t_link.markdown(f"[🔗 View Live Post]({t.live_url})")
                    else:
                        col_t_link.caption("Awaiting Publishing")
                    st.divider()

# ----------------- TAB 4: EDITORIAL STUDIO -----------------
with tab4:
    st.subheader("Draft Review & Fact-Checked Editorial Studio")
    with Session(engine) as session:
        drafts = session.query(ArticleContent).all()
        if not drafts:
            st.info("No drafted articles ready for review. Check Tab 3 until an enqueued topic reaches 'drafted'.")
        else:
            draft_options = {d.id: f"#{d.id} — {d.meta_title}" for d in drafts}
            selected_id = st.selectbox(
                "Select Article to Inspect & Edit:",
                options=list(draft_options.keys()),
                format_func=lambda x: draft_options[x]
            )
            
            selected_draft = session.get(ArticleContent, selected_id)
            if selected_draft:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    new_meta_title = st.text_input("SEO Meta Title:", value=selected_draft.meta_title)
                with col_m2:
                    new_meta_desc = st.text_input("SEO Meta Description:", value=selected_draft.meta_description)
                
                updated_html = st.text_area(
                    "HTML Content Editor:",
                    value=selected_draft.content_html,
                    height=480
                )
                
                # Dynamic Stats Bar
                words = len(updated_html.split())
                read_time = max(1, round(words / 220))
                
                st.markdown(f"""
                <div style="display: flex; gap: 16px; margin: 12px 0 20px 0; color: #94A3B8; font-size: 13px; font-weight: 600;">
                    <span>📊 Word Count: <strong style="color: #F8FAFC;">{words} words</strong></span>
                    <span>⏱️ Estimated Reading Time: <strong style="color: #F8FAFC;">{read_time} min</strong></span>
                    <span>🛡️ Fact-Check Grounding: <strong style="color: #34D399;">Active (Google Search Grounded)</strong></span>
                </div>
                """, unsafe_allow_html=True)

                col_btn_save, col_btn_preview = st.columns([1, 1])
                with col_btn_save:
                    if st.button("💾 Save Revisions to Database", use_container_width=True):
                        selected_draft.meta_title = new_meta_title
                        selected_draft.meta_description = new_meta_desc
                        selected_draft.content_html = updated_html
                        session.add(selected_draft)
                        session.commit()
                        st.toast("Article updated and saved to SQLite!", icon="💾")
                
                with col_btn_preview:
                    with st.expander("👁️ Live Visual HTML Preview"):
                        st.markdown(
                            f"<div style='background: white; color: #1E293B; padding: 24px; border-radius: 12px;'>{updated_html}</div>",
                            unsafe_allow_html=True
                        )

                with st.expander("📋 Inspect Schema.org JSON-LD"):
                    try:
                        st.json(json.loads(selected_draft.schema_json))
                    except Exception:
                        st.text(selected_draft.schema_json)

# ----------------- TAB 5: UNIVERSAL PUBLISHER -----------------
with tab5:
    st.subheader("One-Click Universal Publisher (Human-in-the-Loop)")
    st.markdown("Publish fully audited and reviewed drafts to **WordPress REST API** with automated media uploads and Yoast/RankMath SEO tags, or dispatch via **Custom Webhook**.")
    
    with Session(engine) as session:
        eligible_topics = session.query(TopicNode).filter(TopicNode.status.in_(["drafted", "published"])).all()
        if not eligible_topics:
            st.info("No drafts ready for publishing yet.")
        else:
            selected_pub_id = st.selectbox(
                "Choose Article to Dispatch:",
                options=[t.id for t in eligible_topics],
                format_func=lambda x: f"#{x} — {session.get(TopicNode, x).title} [{session.get(TopicNode, x).status}]"
            )
            
            selected_topic = session.get(TopicNode, selected_pub_id)
            article_record = selected_topic.articles[0] if selected_topic.articles else None
            
            if article_record:
                target_cms = st.radio("Select Target Distribution Channel:", ["WordPress REST API", "Custom Site Webhook"], horizontal=True)
                
                if target_cms == "WordPress REST API":
                    col_w1, col_w2 = st.columns(2)
                    with col_w1:
                        wp_url = st.text_input("WordPress Site URL:", value=config.WP_URL or "https://example.com")
                        wp_user = st.text_input("Admin Username:", value=config.WP_USERNAME)
                    with col_w2:
                        wp_pass = st.text_input("Application Password:", value=config.WP_APP_PASSWORD, type="password")
                        post_status = st.selectbox("Publishing Status:", ["draft", "publish"])

                    include_feat_img = st.checkbox("Fetch & Attach Editorial Image via Unsplash", value=True)

                    if st.button("🚀 Push to WordPress REST API", use_container_width=True):
                        try:
                            with st.spinner("Connecting to WordPress REST API & uploading payload..."):
                                feat_media_id = None
                                active_unsplash = unsplash_key.strip() or config.UNSPLASH_CLIENT_ID
                                if include_feat_img and active_unsplash:
                                    img_bytes, alt = MediaAgent.fetch_unsplash_image(selected_topic.title, active_unsplash)
                                    if img_bytes:
                                        feat_media_id = MediaAgent.upload_to_wordpress_media(
                                            wp_url, wp_user, wp_pass, img_bytes, f"featured_{selected_topic.id}.jpg", alt
                                        )

                                pub = WordPressPublisher(wp_url, wp_user, wp_pass)
                                live_url = pub.publish(
                                    title=article_record.meta_title,
                                    content_html=article_record.content_html,
                                    meta_desc=article_record.meta_description,
                                    focus_kw=selected_topic.title,
                                    featured_media_id=feat_media_id,
                                    status=post_status
                                )
                                
                                selected_topic.status = "published"
                                selected_topic.live_url = live_url
                                session.add(selected_topic)
                                session.commit()
                                st.success(f"Article successfully published to WordPress! [Open Link]({live_url})")
                                st.balloons()
                        except Exception as e:
                            st.error(f"WordPress publishing failed: {str(e)}")

                else:
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        webhook_url = st.text_input("Webhook Endpoint URL:", value=config.CUSTOM_WEBHOOK_URL, placeholder="https://api.yourdomain.com/v1/articles")
                    with col_h2:
                        secret_token = st.text_input("API Secret / Bearer Token:", value=config.CUSTOM_WEBHOOK_SECRET, type="password")

                    if st.button("🚀 Dispatch Webhook Payload", use_container_width=True):
                        try:
                            pub = CustomSitePublisher(webhook_url, secret_token)
                            payload = {
                                "title": article_record.meta_title,
                                "content_html": article_record.content_html,
                                "meta_description": article_record.meta_description,
                                "schema_json": article_record.schema_json,
                                "topic": selected_topic.title,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            res = pub.publish(payload)
                            selected_topic.status = "published"
                            session.add(selected_topic)
                            session.commit()
                            st.success(f"Webhook delivered successfully: {res}")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Webhook dispatch failed: {str(e)}")
