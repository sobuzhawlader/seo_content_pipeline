from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SectionBrief(BaseModel):
    h2: str
    h3s: List[str] = Field(default_factory=list)
    talking_points: List[str] = Field(default_factory=list)
    entities_to_include: List[str] = Field(default_factory=list)

class ArticleBrief(BaseModel):
    target_keyword: str
    search_intent: str
    recommended_word_count: int = 2500
    sections: List[SectionBrief]
    faq_list: List[Dict[str, str]] = Field(default_factory=list)
    meta_description: Optional[str] = None

class SERPIntelligence(BaseModel):
    query: str
    top_competitors: List[Dict[str, Any]]
    people_also_ask: List[str]
    related_searches: List[str]

class WPPostMetadata(BaseModel):
    meta_title: str
    meta_description: str
    focus_keyword: str

class ArticlePayload(BaseModel):
    title: str
    content_html: str
    summary: str
    schema_json: str
    metadata: WPPostMetadata
