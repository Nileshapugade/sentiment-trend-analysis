from sqlalchemy import Column, Integer, String, Text, DateTime,Float
from datetime import datetime
from .database import Base

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # This Base will hold the metadata

class SentimentAnalysis(Base):
    __tablename__ = 'sentiment_analysis'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    sentiment = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<SentimentAnalysis(id={self.id}, text={self.text}, sentiment={self.sentiment}, confidence={self.confidence})>"