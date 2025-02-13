from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # This Base will hold the metadata

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    sentiment = Column(String, nullable=False)  # "positive", "negative", "neutral"
    created_at = Column(DateTime, default=datetime.utcnow)
