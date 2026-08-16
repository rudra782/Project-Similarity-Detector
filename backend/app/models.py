from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from .database import Base

def now(): return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    title = Column(String(240), nullable=False, index=True)
    abstract = Column(Text, nullable=False)
    description = Column(Text, default="")
    keywords = Column(JSON, default=list)
    category = Column(String(80), index=True)
    academic_year = Column(String(20), index=True)
    team_name = Column(String(160), default="")
    report_text = Column(Text, default="")
    source_code = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=now)

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    title = Column(String(240), nullable=False)
    category = Column(String(80), default="")
    academic_year = Column(String(20), default="")
    team_name = Column(String(160), default="")
    overall_score = Column(Float, default=0)
    classification = Column(String(40), default="Low Similarity")
    created_at = Column(DateTime(timezone=True), default=now)

class SimilarityResult(Base):
    __tablename__ = "similarity_results"
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    rank = Column(Integer)
    score = Column(Float)
    classification = Column(String(40))
    components = Column(JSON)
    shared_keywords = Column(JSON)
    evidence = Column(JSON)
