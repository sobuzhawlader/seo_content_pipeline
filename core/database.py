from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from config import DATABASE_URL

class TopicNode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = Field(default="pending")  # pending, processing, drafted, published, failed
    live_url: Optional[str] = None
    
    articles: List["ArticleContent"] = Relationship(back_populates="topic")

class ArticleContent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topicnode.id")
    meta_title: str
    meta_description: str
    content_html: str
    content_markdown: str = ""
    schema_json: str = "{}"
    brief_json: Optional[str] = "{}"
    
    topic: Optional[TopicNode] = Relationship(back_populates="articles")

class LinkGraph(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_topic_id: int = Field(foreign_key="topicnode.id")
    target_topic_id: int = Field(foreign_key="topicnode.id")
    anchor_text: str

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)
