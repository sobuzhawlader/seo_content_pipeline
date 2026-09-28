import streamlit as st
import json
import os
from core.database import init_db, engine, TopicNode, ArticleContent, Session
from tasks.worker import executor, background_generation_pipeline
from agents.topical_mapper import build_topical_cluster_map
from agents.media_agent import MediaAgent
from publishers.wordpress import WordPressPublisher
from publishers.custom_site import CustomSitePublisher
import config

init_db()

st.set_page_config(page_title="SEO Pipeline Control Center", layout="wide", page_icon="🚀")
st.title("Autonomous SEO Content Pipeline Control Center")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Topic & Keyword Input",
    "2. Topical Authority Clusters",
    "3. Pipeline Monitor",
    "4. Content Review & Editor",
    "5. Multi-CMS Publisher"
])

# ----------------- TAB 1: Input & Enqueue -----------------
with tab1:
    st.header("Enqueue Target Topic for Pipeline Generation")
    col1, col2 = st.columns(2)
    with col1:
        topic_title = st.text_input("Enter Target Keyword / Topic:", placeholder="e.g. Best AI Tools for Digital Marketing 2026")
    with col2:
        serper_key = st.text_input("Serper API Key:", value=config.SERPER_API_KEY, type="password")
        unsplash_key = st.text_input("Unsplash Client ID (Optional):", value=config.UNSPLASH_CLIENT_ID, type="password")

    if st.button("🚀 Enqueue Topic for Generation", use_container_width=True):
        if not topic_title.strip():
            st.warning("Please enter a valid topic or keyword!")
        else:
            with Session(engine) as session:
                node = TopicNode(title=topic_title.strip(), status="pending")
                session.add(node)
                session.commit()
                session.refresh(node)
                executor.submit(background_generation_pipeline, node.id, serper_key, unsplash_key)
            st.success(f"Topic '{topic_title}' enqueued successfully! Check progress in Tab 3.")

# ----------------- TAB 2: Topical Authority Clusters -----------------
with tab2:
    st.header("Topical Authority Map & Cluster Discovery")
    st.write("Generate a Pillar-and-Cluster topical hierarchy to establish semantic authority in your niche.")
    niche_input = st.text_input("Enter Broad Niche / Seed Subject:", placeholder="e.g. Technical SEO")
    
    if st.button("Generate Topical Map", use_container_width=True):
        if not niche_input.strip():
            st.warning("Please enter a seed niche!")
        else:
            with st.spinner("Analyzing semantic landscape and building cluster map..."):
                try:
                    cluster_data = build_topical_cluster_map(niche_input.strip())
                    st.subheader("🏛️ Pillar Page Recommendation")
                    pillar = cluster_data.get("pillar_page", {})
                    st.info(f"**Title:** {pillar.get('title')}\n\n**Keyword:** `{pillar.get('primary_keyword')}` | **Intent:** {pillar.get('search_intent')}")
                    
                    st.subheader("🔗 Supporting Cluster Articles")
                    clusters = cluster_data.get("clusters", [])
                    for i, c in enumerate(clusters):
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.write(f"**{i+1}. {c.get('title')}** (Subtopic: *{c.get('target_subtopic')}*)")
                        with col_b:
                            if st.button(f"Enqueue Cluster #{i+1}", key=f"cluster_btn_{i}"):
                                with Session(engine) as session:
                                    node = TopicNode(title=c.get('title'), status="pending")
                                    session.add(node)
                                    session.commit()
                                    session.refresh(node)
                                    executor.submit(background_generation_pipeline, node.id, serper_key, unsplash_key)
                                st.success(f"Enqueued '{c.get('title')}'!")
                except Exception as e:
                    st.error(f"Failed to generate cluster map: {str(e)}")

# ----------------- TAB 3: Pipeline Monitor -----------------
with tab3:
    st.header("Real-Time Pipeline Progress Tracker")
    if st.button("🔄 Refresh Status"):
        st.rerun()

    with Session(engine) as session:
        topics = session.query(TopicNode).order_by(TopicNode.id.desc()).all()
        if not topics:
            st.info("No topics have been enqueued yet.")
        else:
            for t in topics:
                col_id, col_name, col_status, col_url = st.columns([1, 4, 2, 3])
                col_id.write(f"**#{t.id}**")
                col_name.write(t.title)
                status_color = {
                    "pending": "⏳ Pending",
                    "processing": "⚙️ Processing",
                    "drafted": "✅ Drafted (Ready for Review)",
                    "published": "🌐 Published",
                    "failed": "❌ Failed"
                }.get(t.status, t.status)
                col_status.write(status_color)
                if t.live_url:
                    col_url.markdown(f"[{t.live_url}]({t.live_url})")
                else:
                    col_url.write("-")

# ----------------- TAB 4: Content Review & Editor -----------------
with tab4:
    st.header("Draft Review & Fact-Checked Content Editor")
    with Session(engine) as session:
        drafts = session.query(ArticleContent).all()
        if not drafts:
            st.info("No generated drafts found yet. Once a topic status reaches 'drafted', it will appear here.")
        else:
            draft_options = {d.id: f"#{d.id} - {d.meta_title}" for d in drafts}
            selected_id = st.selectbox("Select Article to Inspect:", options=list(draft_options.keys()), format_func=lambda x: draft_options[x])
            
            selected_draft = session.get(ArticleContent, selected_id)
            if selected_draft:
                st.subheader(f"Editing: {selected_draft.meta_title}")
                
                meta_col1, meta_col2 = st.columns(2)
                with meta_col1:
                    new_meta_title = st.text_input("Meta Title:", value=selected_draft.meta_title)
                with meta_col2:
                    new_meta_desc = st.text_input("Meta Description:", value=selected_draft.meta_description)
                
                updated_html = st.text_area("Article HTML Content:", value=selected_draft.content_html, height=450)
                
                word_count = len(updated_html.split())
                st.caption(f"Estimated Word Count: **{word_count} words**")

                col_save, col_preview = st.columns([1, 1])
                with col_save:
                    if st.button("💾 Save Draft Changes", use_container_width=True):
                        selected_draft.meta_title = new_meta_title
                        selected_draft.meta_description = new_meta_desc
                        selected_draft.content_html = updated_html
                        session.add(selected_draft)
                        session.commit()
                        st.success("Draft saved successfully!")
                
                with col_preview:
                    with st.expander("👁️ Preview Rendered HTML"):
                        st.markdown(updated_html, unsafe_allow_html=True)
                
                with st.expander("📋 View Schema.org JSON-LD"):
                    try:
                        st.json(json.loads(selected_draft.schema_json))
                    except Exception:
                        st.text(selected_draft.schema_json)

# ----------------- TAB 5: Multi-CMS Publisher -----------------
with tab5:
    st.header("One-Click Universal Publisher (Human-in-the-Loop)")
    with Session(engine) as session:
        draft_topics = session.query(TopicNode).filter(TopicNode.status.in_(["drafted", "published"])).all()
        if not draft_topics:
            st.info("No reviewed drafts ready for publishing.")
        else:
            selected_pub_topic_id = st.selectbox(
                "Choose Article to Publish:",
                options=[t.id for t in draft_topics],
                format_func=lambda x: f"#{x} - {session.get(TopicNode, x).title} [{session.get(TopicNode, x).status}]"
            )
            
            selected_pub_topic = session.get(TopicNode, selected_pub_topic_id)
            article_content = selected_pub_topic.articles[0] if selected_pub_topic.articles else None
            
            if article_content:
                cms_choice = st.radio("Select Target CMS Platform:", ["WordPress REST API", "Custom Site Webhook"])
                
                if cms_choice == "WordPress REST API":
                    wp_col1, wp_col2 = st.columns(2)
                    with wp_col1:
                        wp_url = st.text_input("WordPress URL:", value=config.WP_URL or "https://example.com")
                        wp_user = st.text_input("Username:", value=config.WP_USERNAME)
                    with wp_col2:
                        wp_pass = st.text_input("Application Password:", value=config.WP_APP_PASSWORD, type="password")
                        post_status = st.selectbox("Publishing Status:", ["draft", "publish"])

                    include_image = st.checkbox("Fetch and attach Featured Image via Unsplash", value=True)

                    if st.button("🚀 Publish to WordPress", use_container_width=True):
                        try:
                            with st.spinner("Publishing to WordPress..."):
                                featured_media_id = None
                                if include_image and config.UNSPLASH_CLIENT_ID:
                                    img_bytes, alt = MediaAgent.fetch_unsplash_image(selected_pub_topic.title, config.UNSPLASH_CLIENT_ID)
                                    if img_bytes:
                                        featured_media_id = MediaAgent.upload_to_wordpress_media(
                                            wp_url, wp_user, wp_pass, img_bytes, f"featured_{selected_pub_topic.id}.jpg", alt
                                        )

                                pub = WordPressPublisher(wp_url, wp_user, wp_pass)
                                live_link = pub.publish(
                                    title=article_content.meta_title,
                                    content_html=article_content.content_html,
                                    meta_desc=article_content.meta_description,
                                    focus_kw=selected_pub_topic.title,
                                    featured_media_id=featured_media_id,
                                    status=post_status
                                )
                                
                                selected_pub_topic.status = "published"
                                selected_pub_topic.live_url = live_link
                                session.add(selected_pub_topic)
                                session.commit()
                                st.success(f"Article published successfully! Link: {live_link}")
                        except Exception as e:
                            st.error(f"Publishing failed: {str(e)}")

                else:
                    wh_col1, wh_col2 = st.columns(2)
                    with wh_col1:
                        webhook_url = st.text_input("Webhook URL:", value=config.CUSTOM_WEBHOOK_URL)
                    with wh_col2:
                        secret = st.text_input("API Secret (Bearer Token):", value=config.CUSTOM_WEBHOOK_SECRET, type="password")

                    if st.button("🚀 Dispatch Webhook Payload", use_container_width=True):
                        try:
                            pub = CustomSitePublisher(webhook_url, secret)
                            payload = {
                                "title": article_content.meta_title,
                                "content_html": article_content.content_html,
                                "meta_description": article_content.meta_description,
                                "schema_json": article_content.schema_json,
                                "topic": selected_pub_topic.title
                            }
                            res = pub.publish(payload)
                            selected_pub_topic.status = "published"
                            session.add(selected_pub_topic)
                            session.commit()
                            st.success(f"Webhook delivered successfully: {res}")
                        except Exception as e:
                            st.error(f"Webhook delivery failed: {str(e)}")
