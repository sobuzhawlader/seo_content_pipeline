from concurrent.futures import ThreadPoolExecutor
import json
import logging
from typing import List, Dict, Any
from core.database import engine, TopicNode, ArticleContent, Session
from agents.research_agent import SerpResearchAgent
from agents.brief_agent import generate_content_brief
from agents.section_writer import generate_longform_article
from agents.fact_checker import verify_and_ground_draft

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=3)

def filter_relevant_links(target_title: str, live_articles: List[Dict[str, Any]], max_links: int = 5) -> List[Dict[str, Any]]:
    """Selects top relevant articles based on keyword overlap to avoid token bloat."""
    target_words = set(target_title.lower().split())
    scored_articles = []
    for article in live_articles:
        if not article.get("live_url"):
            continue
        title_words = set(article.get("title", "").lower().split())
        overlap = len(target_words.intersection(title_words))
        scored_articles.append((overlap, article))
    scored_articles.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_articles[:max_links]]

def background_generation_pipeline(
    topic_id: int,
    serper_key: str = None,
    unsplash_key: str = None,
    gemini_key: str = None,
    custom_brief: dict = None
):
    """Executes the full pipeline asynchronously and updates SQLite status."""
    with Session(engine) as session:
        topic = session.get(TopicNode, topic_id)
        if not topic:
            logger.error(f"Topic {topic_id} not found in database.")
            return
        
        topic.status = "processing"
        session.commit()

        try:
            logger.info(f"Starting pipeline for Topic {topic_id}: '{topic.title}'")
            
            # 1. Content Brief (Use custom brief if supplied from Stage 2, else fetch SERP and generate)
            if custom_brief:
                brief = custom_brief
                logger.info("Using user-reviewed Stage 2 Content Brief.")
            else:
                serp_agent = SerpResearchAgent(serper_key)
                intel = serp_agent.fetch_serp_intelligence(topic.title)
                logger.info("Stage 1 SERP Intelligence gathered.")
                brief = generate_content_brief(topic.title, intel, api_key=gemini_key)
                logger.info("Stage 2 Content Brief generated.")

            # 2. Contextual Link Filtering & Section Writing
            raw_live_topics = session.query(TopicNode).filter(TopicNode.live_url != None).all()
            all_live_articles = [
                {"id": t.id, "title": t.title, "live_url": t.live_url}
                for t in raw_live_topics
            ]
            relevant_links = filter_relevant_links(topic.title, all_live_articles, max_links=5)
            raw_article = generate_longform_article(brief, relevant_links, api_key=gemini_key)
            logger.info(f"Stage 3 Drafting complete: ({raw_article.get('word_count')} words).")

            # 3. Fact-Checking & Grounding
            checked_article = verify_and_ground_draft(raw_article["content_html"], topic.title, api_key=gemini_key)
            final_html = checked_article.get("corrected_html", raw_article["content_html"])
            logger.info("Stage 3 Fact-checking & grounding complete.")

            # 4. Save Draft to Database
            article_record = ArticleContent(
                topic_id=topic.id,
                meta_title=topic.title,
                meta_description=brief.get("meta_description") or f"Learn everything about {topic.title} in this in-depth guide.",
                content_html=final_html,
                content_markdown="",
                schema_json=json.dumps(raw_article.get("schema_json", {})),
                brief_json=json.dumps(brief)
            )
            topic.status = "drafted"
            session.add(article_record)
            session.add(topic)
            session.commit()
            logger.info(f"Article saved to DB as drafted.")

        except Exception as e:
            logger.exception(f"Pipeline failed for topic {topic_id}: {str(e)}")
            topic.status = "failed"
            session.commit()
