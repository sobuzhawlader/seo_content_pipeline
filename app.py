import streamlit as st
import json
import os
from datetime import datetime
from core.database import init_db, engine, TopicNode, ArticleContent, Session
from tasks.worker import executor, background_generation_pipeline
from agents.topical_mapper import build_topical_cluster_map
from agents.research_agent import SerpResearchAgent
from agents.brief_agent import generate_content_brief
from agents.media_agent import MediaAgent
from publishers.wordpress import WordPressPublisher
from publishers.custom_site import CustomSitePublisher
import config

init_db()

st.set_page_config(
    page_title="SEOForge AI — 3-Stage Content Funnel",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SESSION STATE MANAGEMENT -----------------
if "stage2_topic" not in st.session_state:
    st.session_state.stage2_topic = ""
if "stage2_brief" not in st.session_state:
    st.session_state.stage2_brief = None

# ----------------- WORLD-CLASS CUSTOM CSS -----------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.main .block-container {
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Glassmorphism Header Banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.12) 50%, rgba(236, 72, 153, 0.08) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 22px 30px;
    margin-bottom: 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hero-title {
    font-size: 26px;
    font-weight: 800;
    background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    margin: 0;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 13px;
    margin-top: 4px;
    font-weight: 500;
}

/* 3-Stage Progress Nav */
.stage-indicator {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}

.stage-pill {
    flex: 1;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.06);
    background: rgba(255, 255, 255, 0.02);
    color: #64748B;
}

.stage-pill.active {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
    border-color: rgba(99, 102, 241, 0.4);
    color: #C7D2FE;
}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: rgba(255, 255, 255, 0.02);
    padding: 8px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 12px 22px;
    font-weight: 700;
    font-size: 15px;
    border: none;
    color: #94A3B8;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
}

/* Pillar & Box Styling */
.pillar-box {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.04) 100%);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 16px;
    padding: 22px;
    margin-top: 14px;
}

.brief-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
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

section[data-testid="stSidebar"] {
    background-color: #0B0F17;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------- SIDEBAR: API Keys & Credentials -----------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
        <span style="font-size: 26px;">⚡</span>
        <div>
            <div style="font-size: 18px; font-weight: 800; color: #FFF;">SEOForge AI</div>
            <div style="font-size: 11px; color: #64748B;">3-Stage Autonomous Content Pipeline</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔑 API Credentials")
    gemini_key = st.text_input("Google Gemini API Key", value=config.GEMINI_API_KEY, type="password")
    serper_key = st.text_input("Serper.dev API Key", value=config.SERPER_API_KEY, type="password", help="For Google SERP scraping")
    unsplash_key = st.text_input("Unsplash Client ID", value=config.UNSPLASH_CLIENT_ID, type="password", help="For featured images (optional)")
    
    st.divider()
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown("🟢 **Gemini AI**: Ready" if gemini_key else "🔴 **Gemini AI**: Unset")
    with col_k2:
        st.markdown("🟢 **SERP**: Live" if serper_key else "🟡 **SERP**: Fallback")
        
    st.divider()
    st.caption("FRAMEWORK METRICS")
    st.markdown("""
    • **Stage 1**: Behzad Hussain & Koray Framework<br>
    • **Stage 2**: Information Gain & Triples Brief<br>
    • **Stage 3**: 2,500+ Words Anti-AI Writing & Dispatch
    """, unsafe_allow_html=True)

# ----------------- TOP BANNER -----------------
st.markdown("""
<div class="hero-banner">
    <div>
        <h1 class="hero-title">SEO Content Pipeline: 3-Stage Funnel</h1>
        <div class="hero-subtitle">1. Topical Map ➔ 2. Content Brief ➔ 3. Content Writing & Publishing</div>
    </div>
    <div style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 9999px; padding: 6px 14px; color: #A5B4FC; font-size: 12px; font-weight: 700;">
        ⚡ Enterprise SEO Workflow
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- 3 MAIN STAGES -----------------
stage1_tab, stage2_tab, stage3_tab = st.tabs([
    "🗺️ Section 1: Topical Map",
    "📋 Section 2: Content Brief",
    "✍️ Section 3: Content Writing & Publishing"
])

# =========================================================================
# SECTION 1: TOPICAL MAP ARCHITECT
# =========================================================================
with stage1_tab:
    st.subheader("Stage 1: Topical Authority Map & Semantic Hierarchy")
    st.caption("Powered by Behzad Hussain (Rank Brilliance, Pakistan) & Koray Tuğberk Gübür's Semantic SEO Methodology")
    st.markdown("Input any seed niche to extract the **Central Entity**, **Source Context**, **Core Pillar**, and **Tri-Tier Supporting Clusters** with exact anchor text rules.")
    
    col_n1, col_n2 = st.columns([3, 1])
    with col_n1:
        seed_niche = st.text_input("Enter Seed Niche / Broad Subject:", placeholder="e.g. Technical SEO or Espresso Machines", key="seed_niche_input")
    with col_n2:
        gen_map_btn = st.button("🗺️ Build Topical Map", use_container_width=True)

    if gen_map_btn:
        if not seed_niche.strip():
            st.warning("Please enter a seed niche subject.")
        elif not gemini_key.strip():
            st.error("Please configure your Gemini API Key in the left sidebar.")
        else:
            with st.spinner("Analyzing semantic entity hierarchy according to Behzad Hussain's framework..."):
                try:
                    cluster_data = build_topical_cluster_map(seed_niche.strip(), api_key=gemini_key.strip())
                    st.session_state["cached_topical_map"] = cluster_data
                except Exception as e:
                    st.error(f"Topical mapping failed: {str(e)}")

    if "cached_topical_map" in st.session_state:
        cdata = st.session_state["cached_topical_map"]
        central_entity = cdata.get("central_entity", "Core Subject")
        source_context = cdata.get("source_context", "Authoritative Domain Perspective")
        
        st.markdown(f"""
        <div style="display: flex; gap: 14px; margin: 16px 0;">
            <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 12px 18px; flex: 1;">
                <div style="font-size: 11px; font-weight: 700; color: #A5B4FC; text-transform: uppercase;">🌐 Central Entity</div>
                <div style="font-size: 17px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{central_entity}</div>
            </div>
            <div style="background: rgba(236, 72, 153, 0.1); border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 12px; padding: 12px 18px; flex: 1;">
                <div style="font-size: 11px; font-weight: 700; color: #F472B6; text-transform: uppercase;">🎯 Source Context (Domain Angle)</div>
                <div style="font-size: 17px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{source_context}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        pillar = cdata.get("pillar_page", {})
        st.markdown(f"""
        <div class="pillar-box">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 12px; font-weight: 700; color: #818CF8; text-transform: uppercase; letter-spacing: 0.5px;">👑 Core Section (Primary Pillar Page)</span>
                <span style="background: rgba(129, 140, 248, 0.2); padding: 3px 10px; border-radius: 9999px; font-size: 11px; color: #C7D2FE; font-weight: 600;">{pillar.get('target_word_count', 3500)} Words</span>
            </div>
            <div style="font-size: 21px; font-weight: 800; color: #FFFFFF; margin: 8px 0 4px 0;">{pillar.get('title')}</div>
            <div style="font-size: 13px; color: #CBD5E1; margin-bottom: 8px;"><em>"{pillar.get('semantic_definition', '')}"</em></div>
            <div style="font-size: 12px; color: #94A3B8;">Primary Keyword: <code style="color: #A5B4FC;">{pillar.get('primary_keyword')}</code> &nbsp;•&nbsp; Intent: <strong>{pillar.get('search_intent')}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        col_p1, col_p2 = st.columns([3, 1])
        with col_p2:
            if st.button("📋 Send Pillar to Stage 2 (Brief)", key="send_pillar_btn"):
                st.session_state.stage2_topic = pillar.get("title", "")
                st.success(f"Loaded Pillar '{pillar.get('title')}' into Section 2!")
                st.rerun()

        st.markdown("#### 🔗 Tri-Tier Supporting Clusters & Internal Linking Vectors")
        for i, c in enumerate(cdata.get("clusters", [])):
            tier = c.get("tier", "Outer")
            tier_color = {"Core": "#F59E0B", "Contextual Bridge": "#38BDF8", "Outer": "#A855F7"}.get(tier, "#94A3B8")
            
            with st.container():
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-weight: 700; color: #F8FAFC; font-size: 15px;">{i+1}. {c.get('title')}</span>
                            <span style="background: rgba(255,255,255,0.05); color: {tier_color}; border: 1px solid {tier_color}44; border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 700;">{tier}</span>
                        </div>
                        <div style="font-size: 12px; color: #94A3B8; line-height: 1.6;">
                            🎯 <strong>Target Query:</strong> <code>{c.get('target_subtopic')}</code> &nbsp;|&nbsp; <strong>Attribute:</strong> <em>{c.get('attribute_focus', '')}</em><br>
                            🔗 <strong>Outbound to Pillar:</strong> <code style="color: #34D399;">"{c.get('outbound_anchor_text')}"</code> &nbsp;|&nbsp; 
                            📥 <strong>Inbound:</strong> <code style="color: #60A5FA;">"{c.get('inbound_anchor_text')}"</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_c2:
                    if st.button(f"📋 Send to Stage 2 (Brief)", key=f"send_cl_{i}"):
                        st.session_state.stage2_topic = c.get("title", "")
                        st.success(f"Loaded '{c.get('title')}' into Section 2!")
                        st.rerun()

# =========================================================================
# SECTION 2: CONTENT BRIEF ENGINE
# =========================================================================
with stage2_tab:
    st.subheader("Stage 2: Semantic & Information-Gain Content Brief")
    st.caption("Extract competitor SERP gaps, define knowledge graph triples, and construct an unbreakable H2/H3 blueprint.")
    
    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        brief_target_topic = st.text_input(
            "Target Keyword / Topic for Brief:",
            value=st.session_state.stage2_topic,
            placeholder="e.g. Best Open Source AI Agent Frameworks 2026",
            key="brief_topic_input"
        )
    with col_b2:
        generate_brief_btn = st.button("🚀 Generate Content Brief", use_container_width=True)

    if generate_brief_btn:
        if not brief_target_topic.strip():
            st.warning("Please specify a topic or keyword.")
        elif not gemini_key.strip():
            st.error("Please configure your Gemini API Key in the sidebar.")
        else:
            with st.spinner("Scraping live SERPs & generating Information-Gain Brief..."):
                try:
                    serp_agent = SerpResearchAgent(serper_key.strip() or None)
                    serp_intel = serp_agent.fetch_serp_intelligence(brief_target_topic.strip())
                    brief_result = generate_content_brief(brief_target_topic.strip(), serp_intel, api_key=gemini_key.strip())
                    st.session_state.stage2_brief = brief_result
                    st.session_state.stage2_topic = brief_target_topic.strip()
                    st.toast("Content Brief generated successfully!", icon="✅")
                except Exception as e:
                    st.error(f"Brief generation failed: {str(e)}")

    if st.session_state.stage2_brief:
        sb = st.session_state.stage2_brief
        st.divider()
        
        # Action banner to push to Stage 3
        col_bar1, col_bar2 = st.columns([3, 1])
        with col_bar1:
            st.markdown(f"### 📋 Content Blueprint for: `{sb.get('target_keyword')}`")
            st.caption(f"Search Intent: **{sb.get('search_intent')}** &nbsp;|&nbsp; Recommended Word Count: **{sb.get('recommended_word_count', 2800)}+ words**")
        with col_bar2:
            if st.button("✍️ Send to Stage 3 (Write Article)", use_container_width=True, type="primary"):
                with Session(engine) as session:
                    node = TopicNode(title=sb.get('target_keyword'), status="pending")
                    session.add(node)
                    session.commit()
                    session.refresh(node)
                    executor.submit(
                        background_generation_pipeline,
                        node.id,
                        serper_key.strip() or None,
                        unsplash_key.strip() or None,
                        gemini_key.strip() or None,
                        sb
                    )
                st.success("Enqueued for Stage 3 Longform Writing! Switch to Section 3 to monitor and publish.")
                st.toast("Article writing started in background!", icon="🚀")

        # 1. Information Gain & Missing Competitor Gaps
        st.markdown("#### 💡 Information Gain Angles (Competitor SERP Gaps)")
        for gap in sb.get("information_gain_angles", []):
            st.markdown(f"- ⚡ **{gap}**")
            
        # 2. Semantic Triples & Knowledge Graph
        st.markdown("#### 🧬 Semantic Entity Triples (Knowledge Graph Vectors)")
        triples_col1, triples_col2 = st.columns(2)
        triples = sb.get("semantic_entity_triples", [])
        for idx, tr in enumerate(triples):
            target_col = triples_col1 if idx % 2 == 0 else triples_col2
            target_col.markdown(f"<div style='background: rgba(99,102,241,0.08); border-left: 3px solid #6366F1; padding: 8px 12px; margin-bottom: 6px; font-size: 13px; font-family: monospace;'>{tr}</div>", unsafe_allow_html=True)

        # 3. H2/H3 Section Blueprint
        st.markdown("#### 📐 Section-by-Section Heading Architecture")
        for i, sec in enumerate(sb.get("sections", [])):
            with st.expander(f"H2 [{i+1}]: {sec.get('h2')}", expanded=(i==0)):
                if sec.get("featured_snippet_target"):
                    st.info(f"🎯 **Featured Snippet Target (First 50 Words):** {sec.get('featured_snippet_target')}")
                if sec.get("format_directive"):
                    st.caption(f"📊 **Structure Directive:** `{sec.get('format_directive')}`")
                st.write(f"**Key Points:** {', '.join(sec.get('talking_points', []))}")
                st.write(f"**Entities to Include:** {', '.join(sec.get('entities_to_include', []))}")
                if sec.get("h3s"):
                    st.write(f"**H3 Subheadings:** {', '.join(sec.get('h3s'))}")

        # 4. PAA FAQ Blueprint
        st.markdown("#### ❓ People Also Ask (PAA) Schema Target")
        for faq in sb.get("faq_list", []):
            st.markdown(f"• **Q:** *{faq.get('question')}* ➔ **A:** {faq.get('answer_guideline')}")

# =========================================================================
# SECTION 3: CONTENT WRITING & PUBLISHING STUDIO
# =========================================================================
with stage3_tab:
    st.subheader("Stage 3: Autonomous Content Writing & Multi-CMS Publishing")
    st.caption("Iterative section-by-section writing (2,500+ words), Google Search Grounding fact-checking, and 1-Click Publishing.")
    
    col_sync_head, col_sync_btn = st.columns([3, 1])
    with col_sync_head:
        st.markdown("#### ⚡ Active Writing Jobs & Queue Monitor")
    with col_sync_btn:
        if st.button("🔄 Refresh Pipeline Status", use_container_width=True):
            st.rerun()

    with Session(engine) as session:
        topics = session.query(TopicNode).order_by(TopicNode.id.desc()).all()
        if not topics:
            st.info("No active or completed writing jobs found. Send a topic from Section 1 or Section 2 to start writing.")
        else:
            for t in topics:
                badge_class = f"status-{t.status}"
                status_label = {
                    "pending": "⏳ Pending in Queue",
                    "processing": "⚙️ Writing & Grounding (2,500+ Words)",
                    "drafted": "✅ Drafted (Ready for Review)",
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

    st.markdown("---")
    st.markdown("### ✍️ Editorial Studio & 1-Click Publisher")
    
    with Session(engine) as session:
        drafts = session.query(ArticleContent).all()
        if not drafts:
            st.info("No generated articles ready for review yet. When a job above reaches 'Drafted', you can inspect, edit, and publish it here.")
        else:
            draft_options = {d.id: f"#{d.id} — {d.meta_title}" for d in drafts}
            selected_id = st.selectbox(
                "Select Article to Review & Publish:",
                options=list(draft_options.keys()),
                format_func=lambda x: draft_options[x]
            )
            
            selected_draft = session.get(ArticleContent, selected_id)
            if selected_draft:
                col_em1, col_em2 = st.columns(2)
                with col_em1:
                    new_meta_title = st.text_input("SEO Meta Title:", value=selected_draft.meta_title)
                with col_em2:
                    new_meta_desc = st.text_input("SEO Meta Description:", value=selected_draft.meta_description)
                
                updated_html = st.text_area("Full HTML Content (Semantic & Anti-AI Humanized):", value=selected_draft.content_html, height=480)
                
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
                    with st.expander("👁️ Live Visual HTML Blog Preview"):
                        st.markdown(
                            f"<div style='background: white; color: #1E293B; padding: 24px; border-radius: 12px;'>{updated_html}</div>",
                            unsafe_allow_html=True
                        )

                with st.expander("📋 View Schema.org JSON-LD"):
                    try:
                        st.json(json.loads(selected_draft.schema_json))
                    except Exception:
                        st.text(selected_draft.schema_json)

                # --- 1-Click Multi-CMS Publisher ---
                st.markdown("#### 🚀 1-Click Publishing Gateway")
                target_cms = st.radio("Select Target Distribution Channel:", ["WordPress REST API", "Custom Site Webhook"], horizontal=True)
                
                if target_cms == "WordPress REST API":
                    col_w1, col_w2 = st.columns(2)
                    with col_w1:
                        wp_url = st.text_input("WordPress Site URL:", value=config.WP_URL or "https://example.com")
                        wp_user = st.text_input("Admin Username:", value=config.WP_USERNAME)
                    with col_w2:
                        wp_pass = st.text_input("Application Password:", value=config.WP_APP_PASSWORD, type="password")
                        post_status = st.selectbox("Publishing Status:", ["draft", "publish"])

                    include_feat_img = st.checkbox("Fetch & Attach Editorial Stock Image via Unsplash", value=True)

                    if st.button("🚀 Push to WordPress REST API", use_container_width=True):
                        try:
                            with st.spinner("Connecting to WordPress REST API & uploading payload..."):
                                feat_media_id = None
                                active_unsplash = unsplash_key.strip() or config.UNSPLASH_CLIENT_ID
                                if include_feat_img and active_unsplash:
                                    img_bytes, alt = MediaAgent.fetch_unsplash_image(selected_draft.meta_title, active_unsplash)
                                    if img_bytes:
                                        feat_media_id = MediaAgent.upload_to_wordpress_media(
                                            wp_url, wp_user, wp_pass, img_bytes, f"featured_{selected_draft.id}.jpg", alt
                                        )

                                pub = WordPressPublisher(wp_url, wp_user, wp_pass)
                                live_url = pub.publish(
                                    title=selected_draft.meta_title,
                                    content_html=selected_draft.content_html,
                                    meta_desc=selected_draft.meta_description,
                                    focus_kw=selected_draft.meta_title,
                                    featured_media_id=feat_media_id,
                                    status=post_status
                                )
                                
                                parent_topic = session.get(TopicNode, selected_draft.topic_id)
                                if parent_topic:
                                    parent_topic.status = "published"
                                    parent_topic.live_url = live_url
                                    session.add(parent_topic)
                                    session.commit()
                                st.success(f"Article successfully published to WordPress! [Open Live Post]({live_url})")
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
                                "title": selected_draft.meta_title,
                                "content_html": selected_draft.content_html,
                                "meta_description": selected_draft.meta_description,
                                "schema_json": selected_draft.schema_json,
                                "topic": selected_draft.meta_title,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            res = pub.publish(payload)
                            parent_topic = session.get(TopicNode, selected_draft.topic_id)
                            if parent_topic:
                                parent_topic.status = "published"
                                session.add(parent_topic)
                                session.commit()
                            st.success(f"Webhook delivered successfully: {res}")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Webhook dispatch failed: {str(e)}")
